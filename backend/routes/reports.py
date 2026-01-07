"""
Report Generation API Routes - Phase 7
REST endpoints for report generation, download, and management
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from models.auth import User
from models.report_schema import (
    ReportGenerationRequest,
    ReportMetadataResponse,
    ReportTypeEnum,
    ReportFormatEnum
)
from utils.auth import get_current_user
from utils.report_service import get_report_service
from utils.excel_generator import get_excel_generator, get_csv_generator
from utils.pdf_generator import get_pdf_generator
from utils.audit_service import AuditService
from models.audit_schema import AuditEventType, AuditSeverity
from datetime import datetime
from typing import List, Optional
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ReportMetadataResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new report
    
    - **report_type**: Type of report (screening_summary, flagged_items, case_history, compliance_audit)
    - **report_format**: Export format (pdf, excel, csv)
    - **filters**: Optional filters for date range, entity types, etc.
    - **title**: Optional custom title
    - **include_charts**: Include charts and visualizations (PDF/Excel only)
    """
    try:
        # Get report service
        report_service = get_report_service(db)
        
        # Generate report data based on type
        if request.report_type == ReportTypeEnum.SCREENING_SUMMARY:
            report_data = report_service.generate_screening_summary(request.filters)
        elif request.report_type == ReportTypeEnum.FLAGGED_ITEMS:
            report_data = report_service.generate_flagged_items_report(request.filters)
        elif request.report_type == ReportTypeEnum.CASE_HISTORY:
            report_data = report_service.generate_case_history_report(request.filters)
        elif request.report_type == ReportTypeEnum.COMPLIANCE_AUDIT:
            report_data = report_service.generate_compliance_audit_report(request.filters)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Convert Pydantic model to dict
        data_dict = report_data.dict()
        
        # Prepare metadata
        metadata = {
            'title': request.title or f"{request.report_type.value.replace('_', ' ').title()} Report",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generated_by': current_user.username,
            'date_from': request.filters.date_from.strftime('%Y-%m-%d') if request.filters and request.filters.date_from else 'N/A',
            'date_to': request.filters.date_to.strftime('%Y-%m-%d') if request.filters and request.filters.date_to else 'N/A',
        }
        
        # Generate file based on format
        if request.report_format == ReportFormatEnum.PDF:
            pdf_generator = get_pdf_generator()
            if request.report_type == ReportTypeEnum.SCREENING_SUMMARY:
                filepath = pdf_generator.generate_screening_summary_pdf(data_dict, metadata)
            elif request.report_type == ReportTypeEnum.FLAGGED_ITEMS:
                filepath = pdf_generator.generate_flagged_items_pdf(data_dict, metadata)
            elif request.report_type == ReportTypeEnum.CASE_HISTORY:
                filepath = pdf_generator.generate_case_history_pdf(data_dict, metadata)
            else:  # COMPLIANCE_AUDIT
                filepath = pdf_generator.generate_compliance_audit_pdf(data_dict, metadata)
        
        elif request.report_format == ReportFormatEnum.EXCEL:
            excel_generator = get_excel_generator()
            if request.report_type == ReportTypeEnum.SCREENING_SUMMARY:
                filepath = excel_generator.generate_screening_summary_excel(data_dict, metadata)
            elif request.report_type == ReportTypeEnum.FLAGGED_ITEMS:
                filepath = excel_generator.generate_flagged_items_excel(data_dict, metadata)
            elif request.report_type == ReportTypeEnum.CASE_HISTORY:
                filepath = excel_generator.generate_case_history_excel(data_dict, metadata)
            else:  # COMPLIANCE_AUDIT
                filepath = excel_generator.generate_compliance_audit_excel(data_dict, metadata)
        
        elif request.report_format == ReportFormatEnum.CSV:
            csv_generator = get_csv_generator()
            # For CSV, we'll export the main data list
            if request.report_type == ReportTypeEnum.FLAGGED_ITEMS:
                headers = ['id', 'kamco_name', 'kamco_type', 'blacklist_name', 'match_score', 'status', 'severity', 'flagged_by', 'created_at']
                filepath = csv_generator.generate_csv(data_dict.get('flagged_items', []), headers, 'flagged_items')
            elif request.report_type == ReportTypeEnum.CASE_HISTORY:
                headers = ['case_number', 'status', 'priority', 'created_at', 'resolved_at']
                filepath = csv_generator.generate_csv(data_dict.get('cases', []), headers, 'case_history')
            elif request.report_type == ReportTypeEnum.COMPLIANCE_AUDIT:
                headers = ['id', 'action_type', 'entity_name', 'entity_type', 'decision', 'reviewed_by', 'created_at', 'ip_address']
                filepath = csv_generator.generate_csv(data_dict.get('audit_trail', []), headers, 'compliance_audit')
            else:
                # For screening summary, export top matches
                headers = ['name', 'source', 'count', 'avg_score']
                filepath = csv_generator.generate_csv(data_dict.get('top_blacklist_matches', []), headers, 'screening_summary')
        
        else:
            raise HTTPException(status_code=400, detail="Invalid report format")
        
        # Get file info
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        report_id = filename.rsplit('.', 1)[0]  # Use filename without extension as ID
        
        # Log report generation
        audit_service = AuditService(db)
        audit_service.log_user_action(
            event_type=AuditEventType.REPORT_GENERATED,
            action=f"Generated {request.report_type.value} report in {request.report_format.value} format",
            user_id=current_user.id,
            username=current_user.username,
            user_role=current_user.role.value,
            resource_type="report",
            resource_id=report_id,
            metadata={
                "report_type": request.report_type.value,
                "report_format": request.report_format.value,
                "file_size": file_size,
                "filters": request.filters.dict() if request.filters else None
            }
        )
        
        # Build response
        return ReportMetadataResponse(
            report_id=report_id,
            report_type=request.report_type.value,
            report_format=request.report_format.value,
            title=metadata['title'],
            generated_at=metadata['generated_at'],
            generated_by=current_user.username,
            date_range={
                'from': metadata['date_from'],
                'to': metadata['date_to']
            },
            filters_applied=request.filters.dict() if request.filters else None,
            total_records=data_dict.get('total_screenings') or data_dict.get('total_flagged') or data_dict.get('total_cases') or data_dict.get('total_actions', 0),
            file_path=filepath,
            file_size=file_size,
            download_url=f"/api/reports/download/{filename}",
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/download/{filename}")
async def download_report(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download a generated report file
    
    - **filename**: Name of the report file to download
    """
    filepath = os.path.join("reports", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Determine media type based on extension
    ext = filename.rsplit('.', 1)[-1].lower()
    media_types = {
        'pdf': 'application/pdf',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv'
    }
    
    media_type = media_types.get(ext, 'application/octet-stream')
    
    # Log report download
    audit_service = AuditService(db)
    audit_service.log_user_action(
        event_type=AuditEventType.REPORT_DOWNLOADED,
        action=f"Downloaded report: {filename}",
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        resource_type="report",
        resource_id=filename,
        metadata={"filename": filename, "format": ext}
    )
    
    return FileResponse(
        path=filepath,
        media_type=media_type,
        filename=filename
    )


@router.get("/list")
async def list_reports(
    report_type: Optional[str] = None,
    report_format: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    List all generated reports
    
    - **report_type**: Filter by report type (optional)
    - **report_format**: Filter by format (optional)
    - **limit**: Maximum number of reports to return (default: 50)
    """
    try:
        reports_dir = "reports"
        
        if not os.path.exists(reports_dir):
            return {"success": True, "reports": [], "count": 0}
        
        # Get all files in reports directory
        files = os.listdir(reports_dir)
        reports = []
        
        for filename in files:
            filepath = os.path.join(reports_dir, filename)
            
            # Skip directories
            if not os.path.isfile(filepath):
                continue
            
            # Extract info from filename
            ext = filename.rsplit('.', 1)[-1].lower()
            name_parts = filename.rsplit('.', 1)[0].split('_')
            
            # Filter by format
            if report_format and ext != report_format:
                continue
            
            # Filter by type (rough matching from filename)
            if report_type:
                if report_type not in filename.lower():
                    continue
            
            # Get file stats
            stats = os.stat(filepath)
            
            reports.append({
                'filename': filename,
                'report_type': '_'.join(name_parts[:-2]) if len(name_parts) > 2 else 'unknown',
                'format': ext,
                'size': stats.st_size,
                'created_at': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'download_url': f"/api/reports/download/{filename}"
            })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply limit
        reports = reports[:limit]
        
        return {
            "success": True,
            "reports": reports,
            "count": len(reports)
        }
    
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.delete("/{filename}")
async def delete_report(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a report file
    
    - **filename**: Name of the report file to delete
    
    Note: Only admins and finalizers can delete reports
    """
    # Check permissions
    if current_user.role not in ['admin', 'finalizer']:
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete reports")
    
    filepath = os.path.join("reports", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    try:
        os.remove(filepath)
        logger.info(f"Report deleted by {current_user.username}: {filename}")
        
        return {
            "success": True,
            "message": f"Report {filename} deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")


@router.get("/preview/{report_type}")
async def preview_report_data(
    report_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Preview report data without generating a file
    Returns JSON data that would be used in the report
    
    - **report_type**: Type of report to preview
    """
    try:
        report_service = get_report_service(db)
        
        # Generate preview data (last 7 days by default)
        from datetime import timedelta
        from models.report_schema import ReportFilter
        
        filters = ReportFilter(
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now()
        )
        
        if report_type == "screening_summary":
            data = report_service.generate_screening_summary(filters)
        elif report_type == "flagged_items":
            data = report_service.generate_flagged_items_report(filters)
        elif report_type == "case_history":
            data = report_service.generate_case_history_report(filters)
        elif report_type == "compliance_audit":
            data = report_service.generate_compliance_audit_report(filters)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        return {
            "success": True,
            "report_type": report_type,
            "preview_period": "Last 7 days",
            "data": data.dict()
        }
    
    except Exception as e:
        logger.error(f"Error previewing report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to preview report: {str(e)}")
