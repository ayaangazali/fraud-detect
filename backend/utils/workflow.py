"""
Workflow Validation Utilities
Enforces state transition rules and workflow integrity
"""
from typing import Optional, List, Tuple
from models.case import CaseStatus
from models.database import InReviewQueue, FlaggedItem


class WorkflowValidator:
    """
    Validates workflow state transitions and enforces business rules
    """
    
    # Define valid state transitions
    # Format: {current_status: [list of valid next statuses]}
    VALID_STATUS_TRANSITIONS = {
        CaseStatus.OPEN: [CaseStatus.IN_REVIEW, CaseStatus.CLEARED],
        CaseStatus.IN_REVIEW: [
            CaseStatus.FLAGGED,
            CaseStatus.CLEARED,
            CaseStatus.CHECKER_REVIEW
        ],
        CaseStatus.FLAGGED: [
            CaseStatus.CHECKER_REVIEW,
            CaseStatus.IN_REVIEW,  # Undo flag
            CaseStatus.CLEARED
        ],
        CaseStatus.CHECKER_REVIEW: [
            CaseStatus.IN_REVIEW,  # Recheck
            CaseStatus.AWAITING_FINAL,
            CaseStatus.REJECTED,
            CaseStatus.ESCALATED
        ],
        CaseStatus.AWAITING_FINAL: [
            CaseStatus.CLOSED,
            CaseStatus.REJECTED,
            CaseStatus.ESCALATED
        ],
        CaseStatus.ESCALATED: [
            CaseStatus.CLOSED,
            CaseStatus.REJECTED,
            CaseStatus.IN_REVIEW
        ],
        CaseStatus.CLOSED: [],  # Terminal state
        CaseStatus.REJECTED: [],  # Terminal state
        CaseStatus.CLEARED: []  # Terminal state
    }
    
    @staticmethod
    def can_transition(current_status: CaseStatus, new_status: CaseStatus) -> Tuple[bool, Optional[str]]:
        """
        Check if a status transition is valid
        
        Args:
            current_status: Current case status
            new_status: Desired new status
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, "error message")
        """
        # Check if current status exists in transition map
        if current_status not in WorkflowValidator.VALID_STATUS_TRANSITIONS:
            return False, f"Unknown current status: {current_status}"
        
        # Check if new status is valid for current status
        valid_next_statuses = WorkflowValidator.VALID_STATUS_TRANSITIONS[current_status]
        
        if new_status not in valid_next_statuses:
            return False, (
                f"Invalid status transition from {current_status.value} to {new_status.value}. "
                f"Valid transitions: {', '.join([s.value for s in valid_next_statuses]) if valid_next_statuses else 'None (terminal state)'}"
            )
        
        return True, None
    
    @staticmethod
    def can_undo_flag(flagged_item: FlaggedItem, queue_item: InReviewQueue, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if a flag can be undone
        
        Args:
            flagged_item: FlaggedItem to check
            queue_item: InReviewQueue item
            user_id: ID of user attempting undo
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if user is the original screener
        if queue_item.screener_id != user_id:
            return False, "Only the original screener can undo a flag"
        
        # Check if checker has reviewed the item
        if flagged_item.checker_id is not None:
            return False, "Cannot undo flag after checker review has started"
        
        # Check if finalizer has reviewed the item
        if flagged_item.finalizer_id is not None:
            return False, "Cannot undo flag after finalizer review has started"
        
        # Check if case is in a terminal state
        terminal_statuses = ["closed", "rejected", "cleared", "cancelled"]
        if queue_item.status in terminal_statuses:
            return False, f"Cannot undo flag when case is in {queue_item.status} status"
        
        return True, None
    
    @staticmethod
    def can_checker_review(flagged_item: FlaggedItem, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if a checker can review a flagged item
        
        Args:
            flagged_item: FlaggedItem to check
            user_id: ID of checker attempting review
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if checker is assigned
        if flagged_item.checker_id is None:
            return False, "No checker assigned to this item"
        
        # Check if this checker is assigned
        if flagged_item.checker_id != user_id:
            return False, "You are not assigned to this flagged item"
        
        # Check if already reviewed
        if flagged_item.checker_reviewed_at is not None:
            return False, "This item has already been reviewed by checker"
        
        # Check if finalizer has already reviewed
        if flagged_item.finalizer_id is not None:
            return False, "This item has already been reviewed by finalizer"
        
        return True, None
    
    @staticmethod
    def can_finalizer_approve(flagged_item: FlaggedItem) -> Tuple[bool, Optional[str]]:
        """
        Check if a finalizer can approve a flagged item
        
        Args:
            flagged_item: FlaggedItem to check
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if checker has approved
        if flagged_item.status != "approved":
            return False, "Item must be approved by checker before final approval"
        
        # Check if checker has reviewed
        if flagged_item.checker_id is None:
            return False, "Item must be reviewed by checker before final approval"
        
        # Check if already finalized
        if flagged_item.finalizer_id is not None:
            return False, "This item has already been reviewed by finalizer"
        
        return True, None
    
    @staticmethod
    def can_finalizer_override(flagged_item: FlaggedItem) -> Tuple[bool, Optional[str]]:
        """
        Check if a finalizer can override a decision
        Finalizers have more authority, so fewer restrictions
        
        Args:
            flagged_item: FlaggedItem to check
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if already finalized
        if flagged_item.finalizer_id is not None:
            return False, "This item has already been reviewed by finalizer"
        
        # Finalizers can override at any stage before finalization
        return True, None
    
    @staticmethod
    def can_assign_checker(flagged_item: FlaggedItem) -> Tuple[bool, Optional[str]]:
        """
        Check if a checker can be assigned to a flagged item
        
        Args:
            flagged_item: FlaggedItem to check
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if already assigned
        if flagged_item.checker_id is not None:
            return False, f"Checker already assigned (ID: {flagged_item.checker_id})"
        
        # Check if finalizer has reviewed
        if flagged_item.finalizer_id is not None:
            return False, "Cannot assign checker after finalizer review"
        
        return True, None
    
    @staticmethod
    def can_recheck(flagged_item: FlaggedItem, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if a checker can request a recheck
        
        Args:
            flagged_item: FlaggedItem to check
            user_id: ID of checker requesting recheck
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if this checker is assigned
        if flagged_item.checker_id != user_id:
            return False, "You are not assigned to this flagged item"
        
        # Check if finalizer has reviewed
        if flagged_item.finalizer_id is not None:
            return False, "Cannot request recheck after finalizer review"
        
        return True, None
    
    @staticmethod
    def get_required_approvals(risk_score: int) -> List[str]:
        """
        Determine what approvals are required based on risk score
        
        Args:
            risk_score: Risk score (1-10)
            
        Returns:
            List of required approval levels: ['screener', 'checker', 'finalizer']
        """
        required = ["screener"]  # Screener always required
        
        if risk_score >= 7:
            required.append("checker")
        
        if risk_score >= 9:
            required.append("finalizer")
        
        return required
    
    @staticmethod
    def is_terminal_status(status: CaseStatus) -> bool:
        """
        Check if a status is terminal (no further transitions allowed)
        
        Args:
            status: Case status to check
            
        Returns:
            True if terminal, False otherwise
        """
        terminal_statuses = {
            CaseStatus.CLOSED,
            CaseStatus.REJECTED,
            CaseStatus.CLEARED
        }
        return status in terminal_statuses
    
    @staticmethod
    def validate_escalation(current_status: CaseStatus) -> Tuple[bool, Optional[str]]:
        """
        Check if a case can be escalated from its current status
        
        Args:
            current_status: Current case status
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Cannot escalate terminal states
        if WorkflowValidator.is_terminal_status(current_status):
            return False, f"Cannot escalate case in terminal status: {current_status.value}"
        
        # Can escalate from any non-terminal status
        return True, None
