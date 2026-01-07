"""
Email Service for Phase 6 - Email Notifications
Handles SMTP configuration, email sending, and template rendering
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending notifications
    
    Features:
    - SMTP configuration from environment variables
    - HTML email templates
    - Async sending (non-blocking)
    - Fallback to file logging if SMTP fails
    """
    
    # Hardcoded recipient as requested
    DEFAULT_RECIPIENT = "aagazali@kamcoinvest.com"
    
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.email_from = os.getenv("EMAIL_FROM", "noreply@kamcoinvest.com")
        self.email_to = os.getenv("EMAIL_TO", self.DEFAULT_RECIPIENT)
        
        # Email queue for async sending
        self.email_queue: List[Dict[str, Any]] = []
        
        # Check if SMTP is configured
        self.smtp_configured = bool(self.smtp_user and self.smtp_password)
        
        if not self.smtp_configured:
            logger.warning("SMTP not configured - emails will be logged to file")
    
    def send_email(
        self,
        subject: str,
        html_content: str,
        recipient: Optional[str] = None,
        async_send: bool = True
    ) -> bool:
        """
        Send an email
        
        Args:
            subject: Email subject
            html_content: HTML email body
            recipient: Email recipient (uses default if None)
            async_send: Send asynchronously in background thread
            
        Returns:
            True if email was sent/queued successfully
        """
        recipient = recipient or self.email_to
        
        if async_send:
            # Send in background thread
            thread = Thread(
                target=self._send_email_sync,
                args=(subject, html_content, recipient)
            )
            thread.daemon = True
            thread.start()
            return True
        else:
            # Send synchronously
            return self._send_email_sync(subject, html_content, recipient)
    
    def _send_email_sync(
        self,
        subject: str,
        html_content: str,
        recipient: str
    ) -> bool:
        """
        Send email synchronously (internal method)
        
        Args:
            subject: Email subject
            html_content: HTML email body
            recipient: Email recipient
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = recipient
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            if self.smtp_configured:
                # Send via SMTP
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
                
                logger.info(f"✅ Email sent: {subject} to {recipient}")
                return True
            else:
                # Fallback: Log to file
                self._log_email_to_file(subject, html_content, recipient)
                logger.info(f"📧 Email logged to file: {subject}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            # Try to log to file as fallback
            try:
                self._log_email_to_file(subject, html_content, recipient)
                logger.info(f"📁 Email logged to file as fallback: {subject}")
            except Exception as log_error:
                logger.error(f"❌ Failed to log email to file: {str(log_error)}")
            return False
    
    def _log_email_to_file(
        self,
        subject: str,
        html_content: str,
        recipient: str
    ):
        """
        Log email to file when SMTP is not available
        
        Args:
            subject: Email subject
            html_content: HTML email body
            recipient: Email recipient
        """
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{log_dir}/email_{timestamp}.html"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"<!-- \n")
            f.write(f"To: {recipient}\n")
            f.write(f"From: {self.email_from}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write(f"-->\n\n")
            f.write(html_content)
    
    # Template methods for different notification types
    
    def send_screening_alert(
        self,
        entity_name: str,
        entity_type: str,
        blacklist_name: str,
        match_score: int,
        risk_level: str,
        civil_id_match: bool = False
    ) -> bool:
        """
        Send screening match alert email
        
        Args:
            entity_name: Name of Kamco entity
            entity_type: Type (client, vendor, staff, other)
            blacklist_name: Name of blacklist entry
            match_score: Match score (0-100)
            risk_level: Risk level (CRITICAL, HIGH, MEDIUM, LOW)
            civil_id_match: Whether Civil ID matched
            
        Returns:
            True if email sent successfully
        """
        subject = f"🚨 {risk_level} Risk Screening Match Detected"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
                .alert {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
                .risk-critical {{ border-left-color: #dc3545; background-color: #f8d7da; }}
                .risk-high {{ border-left-color: #fd7e14; background-color: #ffe5d0; }}
                .details {{ margin: 20px 0; }}
                .detail-row {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
                .badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
                .badge-critical {{ background-color: #dc3545; color: white; }}
                .badge-high {{ background-color: #fd7e14; color: white; }}
                .badge-medium {{ background-color: #ffc107; color: black; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚨 Screening Match Alert</h2>
                    <p>A potential blacklist match has been detected</p>
                </div>
                
                <div class="content">
                    <div class="alert {'risk-critical' if risk_level == 'CRITICAL' else 'risk-high' if risk_level == 'HIGH' else ''}">
                        <strong>⚠️ Action Required:</strong> This match requires immediate review and verification.
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Risk Level:</span>
                            <span class="badge badge-{risk_level.lower()}">{risk_level}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Match Score:</span>
                            <span class="value">{match_score}%</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Kamco Entity:</span>
                            <span class="value">{entity_name} ({entity_type})</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Blacklist Match:</span>
                            <span class="value">{blacklist_name}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Civil ID Match:</span>
                            <span class="value">{'✅ Yes' if civil_id_match else '❌ No (Name match only)'}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Detection Time:</span>
                            <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        <strong>Next Steps:</strong><br>
                        1. Review the match details in the compliance system<br>
                        2. Verify the identity and relationship<br>
                        3. Make a decision to approve or reject the match<br>
                        4. Document your findings
                    </p>
                </div>
                
                <div class="footer">
                    <p>Kamco Compliance Screening System</p>
                    <p>This is an automated notification. Do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(subject, html_content)
    
    def send_flagged_item_notification(
        self,
        entity_name: str,
        entity_type: str,
        reason: str,
        flagged_by: str
    ) -> bool:
        """
        Send new flagged item notification
        
        Args:
            entity_name: Name of entity
            entity_type: Type of entity
            reason: Reason for flagging
            flagged_by: Username who flagged
            
        Returns:
            True if email sent successfully
        """
        subject = f"🚩 New Item Flagged for Review: {entity_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ffc107; color: #212529; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
                .details {{ margin: 20px 0; }}
                .detail-row {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚩 Item Flagged for Review</h2>
                </div>
                
                <div class="content">
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Entity:</span>
                            <span class="value">{entity_name}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Type:</span>
                            <span class="value">{entity_type}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Reason:</span>
                            <span class="value">{reason}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Flagged By:</span>
                            <span class="value">{flagged_by}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Time:</span>
                            <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        This item requires checker review and verification.
                    </p>
                </div>
                
                <div class="footer">
                    <p>Kamco Compliance Screening System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(subject, html_content)
    
    def send_case_decision_notification(
        self,
        case_id: int,
        entity_name: str,
        decision: str,
        decided_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Send case decision notification
        
        Args:
            case_id: Case ID
            entity_name: Entity name
            decision: APPROVED or REJECTED
            decided_by: Username who made decision
            notes: Optional notes
            
        Returns:
            True if email sent successfully
        """
        is_approved = decision.upper() == "APPROVED"
        emoji = "✅" if is_approved else "❌"
        color = "#28a745" if is_approved else "#dc3545"
        
        subject = f"{emoji} Case Decision: {entity_name} - {decision}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
                .details {{ margin: 20px 0; }}
                .detail-row {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .notes {{ background-color: #fff; padding: 15px; border-left: 4px solid {color}; margin: 15px 0; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{emoji} Case Decision Made</h2>
                    <p>A compliance case has been {decision.lower()}</p>
                </div>
                
                <div class="content">
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Case ID:</span>
                            <span class="value">#{case_id}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Entity:</span>
                            <span class="value">{entity_name}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Decision:</span>
                            <span class="value"><strong>{decision}</strong></span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Decided By:</span>
                            <span class="value">{decided_by}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Time:</span>
                            <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                    
                    {f'<div class="notes"><strong>Notes:</strong><br>{notes}</div>' if notes else ''}
                </div>
                
                <div class="footer">
                    <p>Kamco Compliance Screening System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(subject, html_content)
    
    def send_upload_completion_notification(
        self,
        total_rows: int,
        valid_rows: int,
        errors_count: int,
        uploaded_by: str,
        filename: str
    ) -> bool:
        """
        Send blacklist upload completion notification
        
        Args:
            total_rows: Total rows in file
            valid_rows: Valid rows uploaded
            errors_count: Number of errors
            uploaded_by: Username who uploaded
            filename: Uploaded filename
            
        Returns:
            True if email sent successfully
        """
        success_rate = (valid_rows / total_rows * 100) if total_rows > 0 else 0
        emoji = "✅" if errors_count == 0 else "⚠️"
        
        subject = f"{emoji} Blacklist Upload Complete: {filename}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #17a2b8; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat {{ text-align: center; padding: 15px; background-color: #fff; border-radius: 5px; flex: 1; margin: 0 5px; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: #17a2b8; }}
                .stat-label {{ color: #6c757d; font-size: 14px; }}
                .details {{ margin: 20px 0; }}
                .detail-row {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📊 Blacklist Upload Complete</h2>
                </div>
                
                <div class="content">
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">{total_rows}</div>
                            <div class="stat-label">Total Rows</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: #28a745;">{valid_rows}</div>
                            <div class="stat-label">Valid</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: #dc3545;">{errors_count}</div>
                            <div class="stat-label">Errors</div>
                        </div>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Success Rate:</span>
                            <span class="value {'success' if success_rate == 100 else 'warning' if success_rate >= 90 else 'error'}">
                                {success_rate:.1f}%
                            </span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Filename:</span>
                            <span class="value">{filename}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Uploaded By:</span>
                            <span class="value">{uploaded_by}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">Upload Time:</span>
                            <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        {f'<span class="success">✅ Upload completed successfully with no errors!</span>' if errors_count == 0 else f'<span class="warning">⚠️ Upload completed with {errors_count} errors. Please review the error log.</span>'}
                    </p>
                </div>
                
                <div class="footer">
                    <p>Kamco Compliance Screening System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(subject, html_content)


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """
    Get singleton email service instance
    
    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
