"""
Flask routes for roster management using SQLAlchemy database.
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from functools import wraps
from datetime import datetime
import io
import os
import traceback
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
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
        
        # Update the record fields directly
        from datetime import datetime as dt
        
        # Helper functions
        def parse_datetime(dt_str):
            if not dt_str:
                return None
            try:
                return dt.fromisoformat(dt_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return None
        
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return dt.fromisoformat(date_str).date()
            except (ValueError, AttributeError):
                return None
        
        # Update all fields
        record.jail_location = data.get('jailLocation', record.jail_location)
        record.cell = data.get('cell', record.cell)
        record.day_number = data.get('dayNumber', record.day_number)
        record.total_number = data.get('totalNumber', record.total_number)
        record.name = data.get('name', record.name)
        record.dob = parse_date(data.get('dob', '')) or record.dob
        record.ssn = data.get('ssn', record.ssn)
        record.sex_m = data.get('sexM', record.sex_m)
        record.sex_f = data.get('sexF', record.sex_f)
        record.oca_number = data.get('ocaNumber', record.oca_number)
        record.arrest_date_time = parse_datetime(data.get('arrestDateTime', '')) or record.arrest_date_time
        record.misdemeanor = data.get('misdemeanor', record.misdemeanor)
        record.felony = data.get('felony', record.felony)
        record.charges = data.get('charges', record.charges)
        record.court_packet = data.get('courtPacket', record.court_packet)
        record.inst = data.get('inst', record.inst)
        record.court_case_ticket = data.get('courtCaseTicket', record.court_case_ticket)
        record.bond_change_notice = data.get('bondChangeNotice', record.bond_change_notice)
        record.bond = data.get('bond', record.bond)
        record.waiver = data.get('waiver', record.waiver)
        record.court_date = parse_date(data.get('courtDate', '')) or record.court_date
        record.release_date_time = parse_datetime(data.get('releaseDateTime', '')) or record.release_date_time
        record.holders_notes = data.get('holdersNotes', record.holders_notes)
        record.charging_docs = data.get('chargingDocs', record.charging_docs)
        
        # Handle photo data properly
        photo_data = data.get('suspectPhotoBase64', '')
        if photo_data:
            record.suspect_photo_base64 = photo_data.encode('utf-8') if isinstance(photo_data, str) else photo_data
        
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
    """Generate a professionally formatted PDF report from roster records."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Header Section
    pdf.set_fill_color(25, 25, 112)  # Navy blue background
    pdf.rect(0, 0, 297, 25, 'F')
    
    # Title
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font('Arial', 'B', 18)
    pdf.set_y(8)
    pdf.cell(0, 10, 'SHAKER HEIGHTS POLICE DEPARTMENT', ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 6, 'Jail Roster Report', ln=True, align='C')
    
    # Reset text color and add metadata
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(30)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, f'Report Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', ln=True, align='R')
    pdf.cell(0, 5, f'Total Records: {len(records)}', ln=True, align='R')
    pdf.ln(3)
    
    # Separate Active and Released inmates
    active_inmates = [r for r in records if not r.release_date_time]
    released_inmates = [r for r in records if r.release_date_time]
    
    # Active Inmates Section
    if active_inmates:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, f'Active Inmates in Custody ({len(active_inmates)})', ln=True, fill=True)
        pdf.ln(2)
        
        # Table header for active inmates
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(70, 130, 180)  # Steel blue
        pdf.set_text_color(255, 255, 255)
        
        col_widths = [25, 15, 40, 20, 30, 60, 25, 30]
        headers = ['Location', 'Cell', 'Name', 'OCA #', 'Arrest Date', 'Charges', 'Bond', 'Court Date']
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        pdf.ln()
        
        # Table rows for active inmates
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 8)
        
        for idx, record in enumerate(active_inmates):
            # Alternate row colors
            if idx % 2 == 0:
                pdf.set_fill_color(245, 245, 245)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            # Format dates
            arrest_date = record.arrest_date_time.strftime('%m/%d/%Y %H:%M') if record.arrest_date_time else ''
            court_date = record.court_date.strftime('%m/%d/%Y') if record.court_date else ''
            
            # Truncate long text
            charges = (record.charges or '')[:40] + '...' if record.charges and len(record.charges) > 40 else (record.charges or '')
            
            # Row data
            row_data = [
                record.jail_location or '',
                record.cell or '',
                record.name or '',
                record.oca_number or '',
                arrest_date,
                charges,
                record.bond or '',
                court_date
            ]
            
            for i, data in enumerate(row_data):
                pdf.cell(col_widths[i], 7, str(data), border=1, align='L', fill=True)
            pdf.ln()
        
        pdf.ln(5)
    
    # Released Inmates Section
    if released_inmates:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, f'Released Inmates ({len(released_inmates)})', ln=True, fill=True)
        pdf.ln(2)
        
        # Table header for released inmates
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(169, 169, 169)  # Gray
        pdf.set_text_color(255, 255, 255)
        
        col_widths_rel = [25, 15, 40, 30, 30, 50, 30]
        headers_rel = ['Location', 'Cell', 'Name', 'Arrest Date', 'Release Date', 'Charges', 'Notes']
        
        for i, header in enumerate(headers_rel):
            pdf.cell(col_widths_rel[i], 8, header, border=1, fill=True, align='C')
        pdf.ln()
        
        # Table rows for released inmates
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 8)
        
        for idx, record in enumerate(released_inmates):
            # Alternate row colors
            if idx % 2 == 0:
                pdf.set_fill_color(245, 245, 245)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            # Format dates
            arrest_date = record.arrest_date_time.strftime('%m/%d/%Y') if record.arrest_date_time else ''
            release_date = record.release_date_time.strftime('%m/%d/%Y %H:%M') if record.release_date_time else ''
            
            # Truncate long text
            charges = (record.charges or '')[:35] + '...' if record.charges and len(record.charges) > 35 else (record.charges or '')
            notes = (record.holders_notes or '')[:20] + '...' if record.holders_notes and len(record.holders_notes) > 20 else (record.holders_notes or '')
            
            # Row data
            row_data = [
                record.jail_location or '',
                record.cell or '',
                record.name or '',
                arrest_date,
                release_date,
                charges,
                notes
            ]
            
            for i, data in enumerate(row_data):
                pdf.cell(col_widths_rel[i], 7, str(data), border=1, align='L', fill=True)
            pdf.ln()
    
    # Footer
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, 'This document is confidential and for official use only.', ln=True, align='C')
    pdf.cell(0, 5, 'Shaker Heights Police Department - Jail Management System', ln=True, align='C')
    
    # Return PDF as bytes
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    else:
        return bytes(pdf_output)  # Convert bytearray to bytes

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
    """Send roster as PDF via email using SendGrid."""
    try:
        data = request.get_json()
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({'error': 'Email address is required'}), 400
        
        # Get SendGrid API key and sender email from environment variables
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        sender_email = os.getenv('SENDER_EMAIL', 'jailroster@shakerpd.com')
        
        print(f"[EMAIL] SendGrid Config - Sender: {sender_email}, Recipient: {recipient_email}")
        
        if not sendgrid_api_key:
            return jsonify({'error': 'SendGrid API key not configured'}), 500
        
        # Generate PDF
        print("[EMAIL] Generating PDF...")
        records = Roster.query.all()
        pdf_data = generate_pdf_report(records)
        print(f"[EMAIL] PDF generated, size: {len(pdf_data)} bytes")
        
        # Encode PDF as base64
        encoded_pdf = base64.b64encode(pdf_data).decode()
        
        # Create email message
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = Mail(
            from_email=sender_email,
            to_emails=recipient_email,
            subject=f'Jail Roster Report - {current_date}',
            html_content=f'''
            <p>Dear Recipient,</p>
            <p>Please find attached the Jail Roster Report generated on {current_datetime}.</p>
            <p>This report contains all current inmate records in the system.</p>
            <p>Best regards,<br>Shaker Police Department</p>
            '''
        )
        
        # Attach PDF
        print("[EMAIL] Attaching PDF to email...")
        attachment = Attachment(
            FileContent(encoded_pdf),
            FileName(f'jail_roster_{current_date}.pdf'),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        message.attachment = attachment
        
        # Send email via SendGrid
        print("[EMAIL] Sending email via SendGrid...")
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        print(f"[EMAIL] SendGrid response - Status: {response.status_code}")
        print(f"[EMAIL] Email sent successfully to {recipient_email}")
        
        return jsonify({'message': 'Email sent successfully'}), 200
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

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
