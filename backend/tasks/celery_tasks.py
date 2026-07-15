"""
tasks/celery_tasks.py — Celery background tasks.

Three tasks:
1. export_user_booking_history  — Async CSV export triggered by user.
2. send_daily_trek_reminders    — Scheduled daily by Celery Beat.
3. send_monthly_admin_report    — Scheduled on the 1st of each month by Celery Beat.

Redis acts as both Celery broker and result backend.
"""

import csv
import os
import smtplib
import json
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# TASK 1: Async CSV Export (user-triggered)
@shared_task(bind=True)
def export_user_booking_history(self, user_id: int):
    """
    Generates a CSV of a user's full booking history.
    The task ID is returned to the frontend immediately; the user polls
    /api/user/export-status/<task_id> to know when it's ready.
    """
    # Import Flask app context inside the task
    from app import create_app
    from models import User, Booking

    app = create_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found.")

        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

        export_dir = app.config["EXPORT_DIR"]
        os.makedirs(export_dir, exist_ok=True)

        filename = f"booking_history_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "User ID", "User Name", "Trek Name", "Location",
                "Booking Status", "Booking Date", "Trek Start Date", "Trek End Date"
            ])
            for b in bookings:
                writer.writerow([
                    user_id,
                    user.name,
                    b.trek.name if b.trek else "—",
                    b.trek.location if b.trek else "—",
                    b.status,
                    b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "—",
                    b.trek.start_date.isoformat() if b.trek and b.trek.start_date else "—",
                    b.trek.end_date.isoformat() if b.trek and b.trek.end_date else "—",
                ])

        logger.info(f"CSV export for user {user_id} saved to {filepath}")
        # Return the filename so the frontend can use it as a download parameter
        return filename


# TASK 2: Daily Upcoming Trek Reminders (Celery Beat)
@shared_task
def send_daily_trek_reminders():
    """
    Finds users with treks starting in the next 3 days and sends them
    a reminder. Uses smtplib with the app's MAIL config.
    In development, the Python smtpd debug server can be run with:
        python -m smtpd -n -c DebuggingServer localhost:1025
    """
    from app import create_app
    from models import Booking, Trek

    app = create_app()
    with app.app_context():
        today      = date.today()
        three_days = today + timedelta(days=3)

        # Find bookings where trek starts within 3 days and booking is active
        upcoming = (
            Booking.query
            .join(Trek, Booking.trek_id == Trek.id)
            .filter(
                Booking.status == "Booked",
                Trek.start_date >= today,
                Trek.start_date <= three_days,
            )
            .all()
        )

        sent = 0
        for booking in upcoming:
            user = booking.trekker
            trek = booking.trek
            if not user or not trek:
                continue

            subject = f"[PeakPath] Reminder: {trek.name} starts soon!"
            body = f"""
Hello {user.name},

This is a friendly reminder from PeakPath 🏔️

Your upcoming trek is approaching:

  Trek:      {trek.name}
  Location:  {trek.location}
  Difficulty:{trek.difficulty}
  Start Date:{trek.start_date.strftime("%d %B %Y")}
  End Date:  {trek.end_date.strftime("%d %B %Y")}
  Duration:  {trek.duration_days} day(s)

Please make sure you are prepared and have all required gear.

Explore. Book. Trek. — PeakPath Team
            """.strip()

            try:
                _send_email(app.config, user.email, subject, body)
                sent += 1
            except Exception as e:
                logger.warning(f"Failed to send reminder to {user.email}: {e}")

        logger.info(f"Daily reminders: sent {sent} out of {len(upcoming)} upcoming bookings.")
        return {"sent": sent, "total": len(upcoming)}


# TASK 3: Monthly Admin Activity Report (Celery Beat)
@shared_task
def send_monthly_admin_report():
    """
    Generates a monthly HTML email report for the Admin.
    Scheduled to run on the 1st of every month.
    """
    from app import create_app
    from models import User, Trek, Booking
    from sqlalchemy import func

    app = create_app()
    with app.app_context():
        # Build the report for the previous calendar month
        today  = date.today()
        # First day of current month → last day of previous month
        first_this_month  = today.replace(day=1)
        last_prev_month   = first_this_month - timedelta(days=1)
        first_prev_month  = last_prev_month.replace(day=1)

        month_label = first_prev_month.strftime("%B %Y")

        # Count bookings in the previous month
        monthly_bookings = Booking.query.filter(
            Booking.booking_date >= datetime.combine(first_prev_month, datetime.min.time()),
            Booking.booking_date <= datetime.combine(last_prev_month, datetime.max.time()),
        ).count()

        # Completed treks in previous month
        completed_treks = Trek.query.filter(
            Trek.status == "Completed",
            Trek.end_date >= first_prev_month,
            Trek.end_date <= last_prev_month,
        ).count()

        # Unique participants (users with at least one completed/booked booking last month)
        participants = db_session = app.extensions["sqlalchemy"].session
        unique_users = Booking.query.filter(
            Booking.booking_date >= datetime.combine(first_prev_month, datetime.min.time()),
            Booking.booking_date <= datetime.combine(last_prev_month, datetime.max.time()),
            Booking.status.in_(["Booked", "Completed"])
        ).with_entities(func.count(func.distinct(Booking.user_id))).scalar()

        # Popular treks last month
        popular_query = (
            app.extensions["sqlalchemy"].session
            .query(Trek.name, Trek.location, func.count(Booking.id).label("cnt"))
            .join(Booking, Booking.trek_id == Trek.id)
            .filter(
                Booking.booking_date >= datetime.combine(first_prev_month, datetime.min.time()),
                Booking.booking_date <= datetime.combine(last_prev_month, datetime.max.time()),
            )
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
            .all()
        )
        popular_rows = "".join(
            f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>" for r in popular_query
        )

        html_body = f"""
        <html><body>
        <h2 style="color:#2d6a4f;">PeakPath — Monthly Report: {month_label}</h2>
        <p>Hello Admin,</p>
        <p>Here is the automated monthly summary for <strong>{month_label}</strong>. A PDF version is attached to this email.</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%;">
          <tr style="background:#2d6a4f;color:white;">
            <th>Metric</th><th>Value</th>
          </tr>
          <tr><td>Total Bookings</td><td>{monthly_bookings}</td></tr>
          <tr><td>Completed Treks</td><td>{completed_treks}</td></tr>
          <tr><td>Unique Participants</td><td>{unique_users}</td></tr>
        </table>
        <br/>
        <h3>Popular Treks This Month</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%;">
          <tr style="background:#2d6a4f;color:white;">
            <th>Trek Name</th><th>Location</th><th>Bookings</th>
          </tr>
          {popular_rows}
        </table>
        <br/>
        <p>Explore. Book. Trek. — PeakPath System</p>
        </body></html>
        """

        subject = f"[PeakPath] Monthly Activity Report — {month_label}"
        admin_email = app.config.get("ADMIN_EMAIL", "admin@peakpath.com")

        # Generate PDF report
        export_dir = app.config["EXPORT_DIR"]
        os.makedirs(export_dir, exist_ok=True)
        pdf_filename = f"monthly_report_{first_prev_month.strftime('%Y_%m')}.pdf"
        pdf_path = os.path.join(export_dir, pdf_filename)

        try:
            generate_report_pdf(
                pdf_path,
                month_label,
                monthly_bookings,
                completed_treks,
                unique_users,
                popular_query
            )
            attachments = [pdf_path]
            logger.info(f"PDF monthly report generated at {pdf_path}")
        except Exception as pdf_err:
            logger.error(f"Failed to generate monthly PDF report: {pdf_err}")
            attachments = None

        try:
            _send_email(app.config, admin_email, subject, html_body, html=True, attachments=attachments)
            logger.info(f"Monthly report sent to {admin_email}.")
        except Exception as e:
            logger.error(f"Failed to send monthly report: {e}")

        return {"month": month_label, "bookings": monthly_bookings}


# PDF Report Generator (ReportLab)
def generate_report_pdf(filepath, month_label, bookings_count, completed_count, unique_users, popular_treks):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#2d6a4f'),
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading3'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#40916c'),
        spaceAfter=20
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2b2b2b')
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=body_style,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    # Title & Header
    story.append(Paragraph(f"PeakPath 🏔️", title_style))
    story.append(Paragraph(f"Monthly Admin Activity Report — {month_label}", subtitle_style))
    story.append(Spacer(1, 10))

    # General Stats Table
    stats_data = [
        [Paragraph('Metric', header_style), Paragraph('Value', header_style)],
        [Paragraph('Total Bookings Created', body_style), Paragraph(str(bookings_count), body_style)],
        [Paragraph('Completed Treks', body_style), Paragraph(str(completed_count), body_style)],
        [Paragraph('Unique Participants', body_style), Paragraph(str(unique_users), body_style)]
    ]
    t1 = Table(stats_data, colWidths=[200, 100])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d6a4f')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e2e2')),
    ]))
    
    story.append(Paragraph("<b>Summary Metrics</b>", styles['Heading2']))
    story.append(Spacer(1, 5))
    story.append(t1)
    story.append(Spacer(1, 20))

    # Popular Treks Table
    popular_data = [
        [Paragraph('Trek Name', header_style), Paragraph('Location', header_style), Paragraph('Bookings Count', header_style)]
    ]
    for trek_name, location, count in popular_treks:
        popular_data.append([
            Paragraph(trek_name, body_style),
            Paragraph(location, body_style),
            Paragraph(str(count), body_style)
        ])
    t2 = Table(popular_data, colWidths=[180, 180, 80])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d6a4f')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e2e2')),
    ]))
    
    story.append(Paragraph("<b>Popular Treks This Month</b>", styles['Heading2']))
    story.append(Spacer(1, 5))
    story.append(t2)
    story.append(Spacer(1, 30))

    # Footer
    story.append(Paragraph("<font color='#666666'>This is an automated report generated by the PeakPath System.</font>", body_style))

    doc.build(story)


# Internal email helper (supports attachments)
def _send_email(config: dict, to: str, subject: str, body: str, html: bool = False, attachments: list = None):
    """
    Send an email via the configured SMTP server.
    For local development: python -m smtpd -n -c DebuggingServer localhost:1025
    """
    from email.mime.base import MIMEBase
    from email import encoders

    msg = MIMEMultipart("alternative") if not attachments else MIMEMultipart()
    msg["Subject"] = subject
    msg["From"]    = "noreply@peakpath.com"
    msg["To"]      = to

    if attachments:
        # Attach HTML or plain text body first
        body_part = MIMEText(body, "html" if html else "plain")
        msg.attach(body_part)
        
        # Attach binary files
        for filepath in attachments:
            if not os.path.exists(filepath):
                continue
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={filename}",
            )
            msg.attach(part)
    else:
        part = MIMEText(body, "html" if html else "plain")
        msg.attach(part)

    server = smtplib.SMTP(config.get("MAIL_SERVER", "localhost"), config.get("MAIL_PORT", 1025))
    server.sendmail("noreply@peakpath.com", to, msg.as_string())
    server.quit()
