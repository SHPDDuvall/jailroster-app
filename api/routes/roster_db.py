"""
Flask routes for roster management using SQLAlchemy database.
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from functools import wraps
from datetime import datetime
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
from ..models.roster import db, Roster

roster_bp = Blueprint('roster', __name__)

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    """Decorator to require a specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            if 'user_id' not in session:
                return jsonify({'error': 'Unauthorized'}), 401
            user = {'role': session.get('user_role')}
            if user.get('role') != required_role and user.get('role') != 'admin':
                return jsonify({'error': 'Forbidden'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================================
# CRUD Operations
# ============================================================================

@roster_bp.route('', methods=['GET'])
@require_auth
def get_roster():
    """Get all roster records."""
    try:
        records = Roster.query.all()
        return jsonify([record.to_dict() for record in records]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roster_bp.route('/<record_id>', methods=['GET'])
@require_auth
def get_record(record_id):
    """Get a specific roster record."""
    try:
        record = Roster.query.get(record_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        return jsonify(record.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roster_bp.route('', methods=['POST'])
@require_auth
def create_record():
    """Create a new roster record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate a unique ID
        new_id = str(int(datetime.now().timestamp() * 1000))
        data['id'] = new_id
        
        # Create the record from the dictionary
        record = Roster.from_dict(data)
        record.id = new_id
        
        # Save to database
        db.session.add(record)
        db.session.commit()
        
        return jsonify(record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@roster_bp.route('/<record_id>', methods=['PUT'])
@require_auth
def update_record(record_id):
    """Update an existing roster record."""
    try:
        record = Roster.query.get(record_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update the record
        updated_record = Roster.from_dict(data)
        
        # Copy attributes from the updated record to the existing one
        for key, value in updated_record.to_dict().items():
            if key != 'id':  # Don't update the ID
                setattr(record, key, getattr(updated_record, key))
        
        db.session.commit()
        
        return jsonify(record.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@roster_bp.route('/<record_id>', methods=['DELETE'])
@require_role('admin')
def delete_record(record_id):
    """Delete a roster record."""
    try:
        record = Roster.query.get(record_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': 'Record deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PDF Export
# ============================================================================

def generate_pdf_report(records):
    """Generate a PDF report from roster records."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    
    # Title
    pdf.cell(0, 10, 'Jail Roster Report', ln=True, align='C')
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')
    pdf.ln(5)
    
    # Table header
    col_widths = [15, 20, 15, 15, 20, 15, 15, 15, 15, 20, 15]
    headers = ['Location', 'Cell', 'Name', 'OCA #', 'Arrest Date', 'Charges', 'Bond', 'Court Date', 'Release Date', 'Status', 'Notes']
    
    pdf.set_font('Arial', 'B', 7)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()
    
    # Table rows
    pdf.set_font('Arial', '', 6)
    for record in records:
        # Status
        if record.release_date_time:
            status = 'Released'
        elif record.court_date:
            status = 'Pending Court'
        else:
            status = 'In Custody'
        
        # Format dates
        arrest_date = record.arrest_date_time.strftime('%m/%d/%Y') if record.arrest_date_time else ''
        court_date = record.court_date.strftime('%m/%d/%Y') if record.court_date else ''
        release_date = record.release_date_time.strftime('%m/%d/%Y') if record.release_date_time else ''
        
        # Row data
        row_data = [
            record.jail_location or '',
            record.cell or '',
            record.name or '',
            record.oca_number or '',
            arrest_date,
            (record.charges or '')[:15],  # Truncate charges
            record.bond or '',
            court_date,
            release_date,
            status,
            (record.holders_notes or '')[:10]  # Truncate notes
        ]
        
        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 8, str(data), border=1, align='L')
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

@roster_bp.route('/export/pdf', methods=['GET'])
@require_auth
def export_pdf():
    """Export roster as PDF."""
    try:
        records = Roster.query.all()
        pdf_data = generate_pdf_report(records)
        
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'jail_roster_{datetime.now().strftime("%Y-%m-%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Email Export
# ============================================================================

@roster_bp.route('/export/pdf/email', methods=['POST'])
@require_auth
def export_pdf_email():
    """Send roster as PDF via email."""
    try:
        data = request.get_json()
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({'error': 'Email address is required'}), 400
        
        # Get SMTP configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL', 'noreply@shakerpd.com')
        sender_password = os.getenv('SENDER_PASSWORD', '')
        
        if not sender_password:
            return jsonify({'error': 'Email configuration not set up'}), 500
        
        # Generate PDF
        records = Roster.query.all()
        pdf_data = generate_pdf_report(records)
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f'Jail Roster Report - {datetime.now().strftime("%Y-%m-%d")}'
        
        # Email body
        body = f"""
Dear Recipient,

Please find attached the Jail Roster Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.

This report contains all current inmate records in the system.

Best regards,
Shaker Police Department
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(pdf_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename= jail_roster_{datetime.now().strftime("%Y-%m-%d")}.pdf')
        msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return jsonify({'message': 'Email sent successfully'}), 200
    except smtplib.SMTPAuthenticationError:
        return jsonify({'error': 'Email authentication failed. Check your credentials.'}), 500
    except smtplib.SMTPException as e:
        return jsonify({'error': f'SMTP error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# Import/Export (JSON)
# ============================================================================

@roster_bp.route('/export/json', methods=['GET'])
@require_auth
def export_json():
    """Export roster as JSON."""
    try:
        records = Roster.query.all()
        data = [record.to_dict() for record in records]
        
        return send_file(
            io.BytesIO(json.dumps(data, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'jail_roster_{datetime.now().strftime("%Y-%m-%d")}.json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roster_bp.route('/import/json', methods=['POST'])
@require_role('admin')
def import_json():
    """Import roster from JSON file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and parse JSON
        import json
        data = json.load(file)
        
        if not isinstance(data, list):
            return jsonify({'error': 'Invalid JSON format. Expected an array of records.'}), 400
        
        # Import records
        imported_count = 0
        for record_data in data:
            try:
                record = Roster.from_dict(record_data)
                db.session.add(record)
                imported_count += 1
            except Exception as e:
                print(f"Error importing record: {str(e)}")
        
        db.session.commit()
        
        return jsonify({'message': f'Successfully imported {imported_count} records'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

import os
import json
