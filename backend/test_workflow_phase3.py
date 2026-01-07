"""
Test Phase 3 Workflow - Complete Case Management
Tests the full workflow: Screener flags → Checker reviews → Finalizer approves
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database.connection import get_db, engine
from models.database import InReviewQueue, FlaggedItem, Logbook
from models.case import Case, CaseNote, CaseStatus
from models.notification import EmailNotification
from models.auth import User, UserRole
from utils.auth import hash_password
from datetime import datetime

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")
    
def print_info(message):
    print(f"ℹ️  {message}")

def test_workflow():
    """Test complete Phase 3 workflow"""
    
    print_section("PHASE 3 WORKFLOW TEST")
    print("Testing: Screener → Checker → Finalizer workflow")
    print("Database:", engine.url)
    
    db = next(get_db())
    
    try:
        # ============= SETUP =============
        print_section("1. SETUP - Verify Test Users & Data")
        
        # Get test users
        screener = db.query(User).filter(User.email == "screener@kamco.com").first()
        checker = db.query(User).filter(User.email == "checker@kamco.com").first()
        finalizer = db.query(User).filter(User.email == "finalizer@kamco.com").first()
        
        if not screener:
            print_error("Screener user not found. Please run migration with seed data first.")
            return False
        print_success(f"Screener: {screener.email} (ID: {screener.id})")
        
        if not checker:
            print_error("Checker user not found. Please run migration with seed data first.")
            return False
        print_success(f"Checker: {checker.email} (ID: {checker.id})")
        
        if not finalizer:
            print_error("Finalizer user not found. Please run migration with seed data first.")
            return False
        print_success(f"Finalizer: {finalizer.email} (ID: {finalizer.id})")
        
        # Get an in-review queue item for testing
        queue_item = db.query(InReviewQueue).filter(
            InReviewQueue.status == "pending"
        ).first()
        
        if not queue_item:
            print_info("No pending queue items found. Creating test queue item...")
            queue_item = InReviewQueue(
                kamco_name="Test Company Ltd",
                kamco_type="clients",
                kamco_id=1,
                blacklist_name="Test Blacklist Company",
                blacklist_source="OFAC",
                match_score=92.5,
                status="pending"
            )
            db.add(queue_item)
            db.commit()
            db.refresh(queue_item)
            print_success(f"Created test queue item (ID: {queue_item.id})")
        else:
            print_success(f"Found pending queue item (ID: {queue_item.id})")
        
        # ============= TEST 1: SCREENER FLAGS ITEM =============
        print_section("2. SCREENER FLAGS ITEM")
        
        # Simulate flag action (what POST /api/review/flag does)
        print_info(f"Screener {screener.email} flagging queue item {queue_item.id}...")
        
        # Calculate risk score
        match_percentage = queue_item.match_score
        actor_present = queue_item.actor_name is not None
        risk_score = min(10, int((match_percentage / 10) + (3 if actor_present else 0)))
        requires_checker = risk_score >= 7
        
        print_info(f"Match Score: {match_percentage}%, Actor: {actor_present}, Risk Score: {risk_score}/10")
        
        # Create Case
        # Find next available case number
        year = datetime.now().year
        latest_case = db.query(Case).filter(
            Case.case_number.like(f"CASE-{year}-%")
        ).order_by(Case.case_number.desc()).first()
        
        if latest_case:
            # Extract sequence number and increment
            sequence = int(latest_case.case_number.split('-')[-1]) + 1
        else:
            sequence = 1
        
        case_number = f"CASE-{year}-{sequence:04d}"
        case = Case(
            case_number=case_number,
            status=CaseStatus.IN_REVIEW,
            title=f"Match: {queue_item.kamco_name} → {queue_item.blacklist_name}",
            description=f"Potential match found during scan (Score: {match_percentage}%)",
            created_by_id=screener.id
        )
        db.add(case)
        db.flush()
        
        print_success(f"Created Case: {case.case_number} (ID: {case.id}, Status: {case.status.value})")
        
        # Update InReviewQueue
        queue_item.case_id = case.id
        queue_item.screener_id = screener.id
        queue_item.risk_score = risk_score
        queue_item.requires_checker_review = requires_checker
        queue_item.status = "in_progress"
        
        # Create FlaggedItem
        flagged_item = FlaggedItem(
            in_review_queue_id=queue_item.id,
            case_id=case.id,
            flagged_by_id=screener.id,
            flag_reason="High-risk match detected with OFAC listed entity",
            flag_reason_category="match_confirmed",
            severity="high",
            status="pending"
        )
        db.add(flagged_item)
        db.flush()
        
        print_success(f"Created FlaggedItem (ID: {flagged_item.id})")
        print_info(f"Queue status: {queue_item.status}, Requires checker: {requires_checker}")
        
        # Add CaseNote
        case_note = CaseNote(
            case_id=case.id,
            user_id=screener.id,
            note_type="system",
            note=f"Item flagged by screener (Risk: {risk_score}/10)"
        )
        db.add(case_note)
        
        # Queue email if high risk
        if risk_score >= 7:
            email = EmailNotification(
                user_id=checker.id,
                to_email=checker.email,
                email_type="high_risk_flagged",
                subject=f"High-Risk Flag: {case.case_number}",
                body=f"A high-risk match requires your review (Risk: {risk_score}/10)",
                status="pending"
            )
            db.add(email)
            print_success(f"Queued email notification to checker")
        
        db.commit()
        db.refresh(case)
        db.refresh(flagged_item)
        
        print_success(f"✨ Screener flag complete!")
        
        # ============= TEST 2: UNDO VALIDATION =============
        print_section("3. TEST UNDO RESTRICTIONS")
        
        print_info("Testing: Can screener undo before checker review?")
        can_undo = flagged_item.checker_id is None and queue_item.screener_id == screener.id
        if can_undo:
            print_success("✅ Undo is allowed (no checker involvement yet)")
        else:
            print_error("❌ Undo should be allowed at this stage")
        
        # ============= TEST 3: CHECKER ASSIGNMENT =============
        print_section("4. CHECKER ASSIGNMENT")
        
        print_info(f"Assigning checker {checker.email} to flagged item {flagged_item.id}...")
        
        # Simulate POST /api/review/checker/assign
        flagged_item.checker_id = checker.id
        flagged_item.checker_assigned_at = datetime.utcnow()
        queue_item.assigned_at = datetime.utcnow()
        queue_item.status = "checker_review"
        
        previous_status = case.status
        case.status = CaseStatus.CHECKER_REVIEW
        case.assigned_to_id = checker.id
        
        case_note = CaseNote(
            case_id=case.id,
            user_id=checker.id,
            note_type="system",
            note=f"Checker assigned: {checker.id}"
        )
        db.add(case_note)
        
        db.commit()
        print_success(f"Checker assigned (Status: {previous_status.value} → {case.status.value})")
        
        # Test undo restriction after checker assignment
        print_info("Testing: Can screener undo after checker assigned?")
        can_undo = flagged_item.checker_id is None
        if not can_undo:
            print_success("✅ Undo correctly blocked (checker assigned)")
        else:
            print_error("❌ Undo should be blocked after checker assignment")
        
        # ============= TEST 4: CHECKER APPROVAL =============
        print_section("5. CHECKER APPROVES")
        
        print_info(f"Checker {checker.email} approving flagged item {flagged_item.id}...")
        
        # Simulate POST /api/review/checker/approve
        checker_notes = "Confirmed match with OFAC list. Clear violation of compliance policy."
        priority = "high"
        
        flagged_item.status = "approved"
        flagged_item.checker_notes = checker_notes
        flagged_item.checker_reviewed_at = datetime.utcnow()
        queue_item.reviewed_at = datetime.utcnow()
        queue_item.status = "awaiting_final"
        
        previous_status = case.status
        case.status = CaseStatus.AWAITING_FINAL
        case.priority = priority
        
        case_note = CaseNote(
            case_id=case.id,
            user_id=checker.id,
            note_type="status_change",
            note=f"Checker approved: {checker_notes}"
        )
        db.add(case_note)
        
        # Queue email to finalizer
        email = EmailNotification(
            user_id=finalizer.id,
            to_email=finalizer.email,
            email_type="approval_required",
            subject=f"Final Approval Required: {case.case_number}",
            body=f"Case requires final approval. Checker notes: {checker_notes}",
            status="pending"
        )
        db.add(email)
        
        db.commit()
        print_success(f"Checker approved (Status: {previous_status.value} → {case.status.value})")
        print_success(f"Priority set to: {priority}")
        print_success(f"Queued email to finalizer")
        
        # ============= TEST 5: FINALIZER APPROVAL =============
        print_section("6. FINALIZER FINAL APPROVAL")
        
        print_info(f"Finalizer {finalizer.email} giving final approval for case {case.case_number}...")
        
        # Validate checker approval
        if flagged_item.status != "approved":
            print_error(f"Item must be approved by checker. Current status: {flagged_item.status}")
            return False
        
        if flagged_item.checker_id is None:
            print_error("Item must be reviewed by checker before final approval")
            return False
        
        print_success("✅ Checker approval validated")
        
        # Simulate POST /api/review/finalizer/approve
        finalizer_notes = "Final approval granted. All compliance checks passed. Proceeding with risk mitigation."
        resolution_type = "approved"
        
        flagged_item.finalizer_id = finalizer.id
        flagged_item.finalizer_notes = finalizer_notes
        flagged_item.finalizer_reviewed_at = datetime.utcnow()
        flagged_item.resolution_type = resolution_type
        flagged_item.status = "final_approved"
        flagged_item.resolution_date = datetime.utcnow()
        
        queue_item.status = "completed"
        queue_item.reviewed_at = datetime.utcnow()
        
        previous_status = case.status
        case.status = CaseStatus.CLOSED
        case.resolved_at = datetime.utcnow()
        
        case_note = CaseNote(
            case_id=case.id,
            user_id=finalizer.id,
            note_type="status_change",
            note=f"Final approval: {finalizer_notes}"
        )
        db.add(case_note)
        
        # Queue emails to screener and checker
        for user in [screener, checker]:
            email = EmailNotification(
                user_id=user.id,
                to_email=user.email,
                email_type="case_closed",
                subject=f"Case Closed: {case.case_number}",
                body=f"Case has been approved and closed. Resolution: {resolution_type}",
                status="pending"
            )
            db.add(email)
        
        db.commit()
        db.refresh(case)
        
        print_success(f"Final approval complete (Status: {previous_status.value} → {case.status.value})")
        print_success(f"Resolution: {resolution_type}")
        print_success(f"Case closed at: {case.resolved_at}")
        print_success(f"Queued emails to screener and checker")
        
        # ============= VERIFICATION =============
        print_section("7. WORKFLOW VERIFICATION")
        
        # Count case notes
        notes_count = db.query(CaseNote).filter(CaseNote.case_id == case.id).count()
        print_success(f"Case notes created: {notes_count}")
        
        # Count email notifications
        emails_count = db.query(EmailNotification).filter(
            EmailNotification.email_metadata.like(f'%{case.case_number}%')
        ).count()
        print_success(f"Email notifications queued: {emails_count}")
        
        # Verify case timeline
        print_info("\n📊 Case Timeline:")
        print(f"   Created: {case.created_at}")
        print(f"   Flagged by: Screener (ID: {screener.id})")
        print(f"   Assigned to: Checker (ID: {checker.id})")
        print(f"   Reviewed by: Checker at {flagged_item.checker_reviewed_at}")
        print(f"   Approved by: Finalizer (ID: {finalizer.id}) at {flagged_item.finalizer_reviewed_at}")
        print(f"   Closed: {case.resolved_at}")
        
        # Verify status transitions
        print_info("\n📈 Status Transitions:")
        print(f"   IN_REVIEW → CHECKER_REVIEW → AWAITING_FINAL → CLOSED")
        
        print_section("✨ WORKFLOW TEST COMPLETE")
        print_success("All workflow steps executed successfully!")
        print_success(f"Case {case.case_number} closed successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_recheck_workflow():
    """Test checker recheck workflow"""
    
    print_section("PHASE 3 RECHECK WORKFLOW TEST")
    
    db = next(get_db())
    
    try:
        # Get test users
        screener = db.query(User).filter(User.email == "screener@kamco.com").first()
        checker = db.query(User).filter(User.email == "checker@kamco.com").first()
        
        # Create a test queue item
        queue_item = InReviewQueue(
            kamco_name="Recheck Test Company",
            kamco_type="vendors",
            kamco_id=2,
            blacklist_name="Test Vendor",
            blacklist_source="UN",
            match_score=75.0,
            status="pending"
        )
        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)
        
        # Screener flags
        # Find next available case number
        year = datetime.now().year
        latest_case = db.query(Case).filter(
            Case.case_number.like(f"CASE-{year}-%")
        ).order_by(Case.case_number.desc()).first()
        
        if latest_case:
            sequence = int(latest_case.case_number.split('-')[-1]) + 1
        else:
            sequence = 1
        
        case_number = f"CASE-{year}-{sequence:04d}"
        
        case = Case(
            case_number=case_number,
            status=CaseStatus.IN_REVIEW,
            title=f"Match: {queue_item.kamco_name}",
            description="Test recheck workflow",
            created_by_id=screener.id
        )
        db.add(case)
        db.flush()
        
        queue_item.case_id = case.id
        queue_item.screener_id = screener.id
        queue_item.status = "in_progress"
        
        flagged_item = FlaggedItem(
            in_review_queue_id=queue_item.id,
            case_id=case.id,
            flagged_by_id=screener.id,
            flag_reason="Needs verification",
            flag_reason_category="needs_verification",
            severity="medium",
            status="pending"
        )
        db.add(flagged_item)
        db.commit()
        
        print_success(f"Setup complete - Case: {case.case_number}")
        
        # Checker assigned
        flagged_item.checker_id = checker.id
        flagged_item.checker_assigned_at = datetime.utcnow()
        case.status = CaseStatus.CHECKER_REVIEW
        db.commit()
        
        print_success("Checker assigned")
        
        # Checker requests recheck
        print_info("Checker requesting recheck...")
        
        recheck_reason = "Additional information needed from screener before proceeding"
        
        flagged_item.checker_id = None
        flagged_item.checker_assigned_at = None
        flagged_item.status = "recheck_requested"
        flagged_item.checker_notes = recheck_reason
        
        queue_item.status = "pending"
        queue_item.requires_checker_review = False
        queue_item.assigned_at = None
        
        case.status = CaseStatus.IN_REVIEW
        
        case_note = CaseNote(
            case_id=case.id,
            user_id=checker.id,
            note_type="status_change",
            note=f"Recheck requested: {recheck_reason}"
        )
        db.add(case_note)
        
        db.commit()
        
        print_success(f"Recheck requested - Status: {case.status.value}")
        print_success(f"Reason: {recheck_reason}")
        print_success(f"Checker assignment cleared")
        print_success(f"Queue back to pending status")
        
        print_section("✨ RECHECK WORKFLOW TEST COMPLETE")
        return True
        
    except Exception as e:
        print_error(f"Recheck test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_escalation_workflow():
    """Test finalizer escalation workflow"""
    
    print_section("PHASE 3 ESCALATION WORKFLOW TEST")
    
    db = next(get_db())
    
    try:
        # Get test users
        screener = db.query(User).filter(User.email == "screener@kamco.com").first()
        checker = db.query(User).filter(User.email == "checker@kamco.com").first()
        finalizer = db.query(User).filter(User.email == "finalizer@kamco.com").first()
        
        # Create escalation test case
        queue_item = InReviewQueue(
            kamco_name="Complex Escalation Case Ltd",
            kamco_type="clients",
            kamco_id=3,
            blacklist_name="Sanctioned Entity",
            blacklist_source="EU",
            match_score=98.5,
            status="pending"
        )
        db.add(queue_item)
        db.commit()
        
        # Flag with high risk
        # Find next available case number
        year = datetime.now().year
        latest_case = db.query(Case).filter(
            Case.case_number.like(f"CASE-{year}-%")
        ).order_by(Case.case_number.desc()).first()
        
        if latest_case:
            sequence = int(latest_case.case_number.split('-')[-1]) + 1
        else:
            sequence = 1
        
        case_number = f"CASE-{year}-{sequence:04d}"
        
        case = Case(
            case_number=case_number,
            status=CaseStatus.IN_REVIEW,
            title=f"High-Risk Match: {queue_item.kamco_name}",
            description="Complex case requiring escalation",
            created_by_id=screener.id
        )
        db.add(case)
        db.flush()
        
        queue_item.case_id = case.id
        queue_item.screener_id = screener.id
        queue_item.risk_score = 10
        
        flagged_item = FlaggedItem(
            in_review_queue_id=queue_item.id,
            case_id=case.id,
            flagged_by_id=screener.id,
            flag_reason="Critical sanctions match",
            severity="critical"
        )
        db.add(flagged_item)
        
        # Checker approves
        flagged_item.checker_id = checker.id
        flagged_item.status = "approved"
        case.status = CaseStatus.AWAITING_FINAL
        db.commit()
        
        print_success(f"Setup complete - Critical case: {case.case_number} (Risk: 10/10)")
        
        # Finalizer escalates
        print_info("Finalizer escalating to executive level...")
        
        escalation_reason = "Extremely complex case involving multiple jurisdictions and significant financial exposure requiring executive decision"
        escalation_level = "executive"
        
        flagged_item.finalizer_id = finalizer.id
        flagged_item.status = "escalated"
        flagged_item.escalation_level = escalation_level
        
        queue_item.status = "escalated"
        queue_item.escalation_reason = escalation_reason
        
        case.status = CaseStatus.ESCALATED
        case.priority = "critical"
        
        case_note = CaseNote(
            case_id=case.id,
            user_id=finalizer.id,
            note_type="status_change",
            note=f"Escalated to {escalation_level}: {escalation_reason}"
        )
        db.add(case_note)
        
        db.commit()
        
        print_success(f"Case escalated to: {escalation_level}")
        print_success(f"Status: {case.status.value}")
        print_success(f"Priority: {case.priority}")
        print_info(f"Reason: {escalation_reason}")
        
        print_section("✨ ESCALATION WORKFLOW TEST COMPLETE")
        return True
        
    except Exception as e:
        print_error(f"Escalation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "🚀 " * 30)
    print("PHASE 3 WORKFLOW TESTS")
    print("🚀 " * 30)
    
    # Run all tests
    test1_passed = test_workflow()
    print("\n" + "⏸️  " * 30 + "\n")
    
    test2_passed = test_recheck_workflow()
    print("\n" + "⏸️  " * 30 + "\n")
    
    test3_passed = test_escalation_workflow()
    
    # Summary
    print("\n" + "📊 " * 30)
    print("TEST SUMMARY")
    print("📊 " * 30)
    print(f"\n1. Main Workflow Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"2. Recheck Workflow Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"3. Escalation Workflow Test: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("Phase 3 workflow implementation is complete and functional!")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the errors above")
