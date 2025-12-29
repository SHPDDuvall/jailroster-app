from flask import Blueprint, request, jsonify, send_file
from functools import wraps
from datetime import datetime
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF

roster_bp = Blueprint('roster', __name__, url_prefix='/api/roster')

# In-memory data store (for development/testing)
roster_data = [
    {
        'id': '1',
        'jailLocation': 'Solon',
        'cell': 'SOL',
        'dayNumber': '1',
        'totalNumber': '100',
        'name': 'John Doe',
        'dob': '1990-01-15',
        'ssn': '123-45-6789',
        'sexM': True,
        'sexF': False,
        'ocaNumber': 'SHPD2025-001',
        'arrestDateTime': '2025-01-10T14:30:00',
        'misdemeanor': False,
        'felony': True,
        'charges': 'Felony Theft, Burglary',
        'courtPacket': 'CP-001',
        'inst': 'INST-001',
        'courtCaseTicket': 'CCT-001',
        'bondChangeNotice': False,
        'bond': '$50,000',
        'waiver': 'No',
        'courtDate': '2025-02-15',
        'releaseDateTime': '',
        'holdersNotes': 'High risk, monitor closely',
        'chargingDocs': 'Filed',
        'suspectPhotoBase64': ''
    },
    {
        'id': '2',
        'jailLocation': 'Solon',
        'cell': 'SOL-2',
        'dayNumber': '2',
        'totalNumber': '100',
        'name': 'Jane Smith',
        'dob': '1985-05-20',
        'ssn': '987-65-4321',
        'sexM': False,
        'sexF': True,
        'ocaNumber': 'SHPD2025-002',
        'arrestDateTime': '2025-01-12T10:15:00',
        'misdemeanor': True,
        'felony': False,
        'charges': 'DUI, Reckless Driving',
        'courtPacket': 'CP-002',
        'inst': 'INST-002',
        'courtCaseTicket': 'CCT-002',
        'bondChangeNotice': False,
        'bond': '$10,000',
        'waiver': 'Yes',
        'courtDate': '2025-02-20',
        'releaseDateTime': '2025-01-20T16:45:00',
        'holdersNotes': 'Released on own recognizance',
        'chargingDocs': 'Filed',
        'suspectPhotoBase64': ''
    }
]

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'user' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@roster_bp.route('', methods=['GET'])
@require_auth
def get_roster():
    """Get all roster records"""
    return jsonify(roster_data), 200

@roster_bp.route('/<record_id>', methods=['GET'])
@require_auth
def get_record(record_id):
    """Get a specific roster record"""
    record = next((r for r in roster_data if r['id'] == record_id), None)
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(record), 200

@roster_bp.route('', methods=['POST'])
@require_auth
def create_record():
    """Create a new roster record"""
    data = request.get_json()
    
    # Remove the 'new-' prefix from the ID for storage
    new_id = str(int(datetime.now().timestamp() * 1000))
    
    new_record = {
        'id': new_id,
        'jailLocation': data.get('jailLocation', 'Solon'),
        'cell': data.get('cell', ''),
        'dayNumber': data.get('dayNumber', ''),
        'totalNumber': data.get('totalNumber', ''),
        'name': data.get('name', ''),
        'dob': data.get('dob', ''),
        'ssn': data.get('ssn', ''),
        'sexM': data.get('sexM', False),
        'sexF': data.get('sexF', False),
        'ocaNumber': data.get('ocaNumber', ''),
        'arrestDateTime': data.get('arrestDateTime', ''),
        'misdemeanor': data.get('misdemeanor', False),
        'felony': data.get('felony', False),
        'charges': data.get('charges', ''),
        'courtPacket': data.get('courtPacket', ''),
        'inst': data.get('inst', ''),
        'courtCaseTicket': data.get('courtCaseTicket', ''),
        'bondChangeNotice': data.get('bondChangeNotice', False),
        'bond': data.get('bond', ''),
        'waiver': data.get('waiver', ''),
        'courtDate': data.get('courtDate', ''),
        'releaseDateTime': data.get('releaseDateTime', ''),
        'holdersNotes': data.get('holdersNotes', ''),
        'chargingDocs': data.get('chargingDocs', ''),
        'suspectPhotoBase64': data.get('suspectPhotoBase64', '')
    }
    
    roster_data.append(new_record)
    return jsonify(new_record), 201

@roster_bp.route('/<record_id>', methods=['PUT'])
@require_auth
def update_record(record_id):
    """Update an existing roster record"""
    record = next((r for r in roster_data if r['id'] == record_id), None)
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    data = request.get_json()
    
    # Update all fields
    record.update({
        'jailLocation': data.get('jailLocation', record.get('jailLocation')),
        'cell': data.get('cell', record.get('cell')),
        'dayNumber': data.get('dayNumber', record.get('dayNumber')),
        'totalNumber': data.get('totalNumber', record.get('totalNumber')),
        'name': data.get('name', record.get('name')),
        'dob': data.get('dob', record.get('dob')),
        'ssn': data.get('ssn', record.get('ssn')),
        'sexM': data.get('sexM', record.get('sexM')),
        'sexF': data.get('sexF', record.get('sexF')),
        'ocaNumber': data.get('ocaNumber', record.get('ocaNumber')),
        'arrestDateTime': data.get('arrestDateTime', record.get('arrestDateTime')),
        'misdemeanor': data.get('misdemeanor', record.get('misdemeanor')),
        'felony': data.get('felony', record.get('felony')),
        'charges': data.get('charges', record.get('charges')),
        'courtPacket': data.get('courtPacket', record.get('courtPacket')),
        'inst': data.get('inst', record.get('inst')),
        'courtCaseTicket': data.get('courtCaseTicket', record.get('courtCaseTicket')),
        'bondChangeNotice': data.get('bondChangeNotice', record.get('bondChangeNotice')),
        'bond': data.get('bond', record.get('bond')),
        'waiver': data.get('waiver', record.get('waiver')),
        'courtDate': data.get('courtDate', record.get('courtDate')),
        'releaseDateTime': data.get('releaseDateTime', record.get('releaseDateTime')),
        'holdersNotes': data.get('holdersNotes', record.get('holdersNotes')),
        'chargingDocs': data.get('chargingDocs', record.get('chargingDocs')),
        'suspectPhotoBase64': data.get('suspectPhotoBase64', record.get('suspectPhotoBase64'))
    })
    
    return jsonify(record), 200

@roster_bp.route('/<record_id>', methods=['DELETE'])
@require_auth
def delete_record(record_id):
    """Delete a roster record"""
    global roster_data
    record = next((r for r in roster_data if r['id'] == record_id), None)
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    roster_data = [r for r in roster_data if r['id'] != record_id]
    return jsonify({'message': 'Record deleted'}), 200

@roster_bp.route('/clear', methods=['POST'])
@require_auth
def clear_roster():
    """Clear all roster records (admin only)"""
    from flask import session
    if session.get('user', {}).get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    
    global roster_data
    roster_data = []
    return jsonify({'message': 'Roster cleared'}), 200

def generate_pdf_report(records, title="Jail Roster Report"):
    """Generate a PDF report from roster records"""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    
    # Report date
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='R')
    pdf.ln(5)
    
    # Table header
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(200, 200, 200)
    
    col_widths = [15, 12, 20, 15, 20, 25, 15, 15, 15, 15]
    headers = ['Location', 'Cell', 'Name', 'OCA #', 'Arrest Date', 'Charges', 'Bond', 'Court Date', 'Release Date', 'Status']
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
    pdf.ln()
    
    # Table data
    pdf.set_font('Arial', '', 8)
    for record in records:
        pdf.set_fill_color(245, 245, 245)
        
        # Determine status
        if record.get('releaseDateTime'):
            status = 'Released'
        elif record.get('courtDate'):
            status = 'Pending'
        else:
            status = 'In Custody'
        
        row_data = [
            record.get('jailLocation', ''),
            record.get('cell', ''),
            record.get('name', ''),
            record.get('ocaNumber', ''),
            record.get('arrestDateTime', ''),
            record.get('charges', '')[:20],  # Truncate long charges
            record.get('bond', ''),
            record.get('courtDate', ''),
            record.get('releaseDateTime', ''),
            status
        ]
        
        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 8, str(data)[:15], border=1, fill=True, align='L')
        pdf.ln()
    
    # Return PDF as bytes
    pdf_bytes = io.BytesIO()
    pdf_output = pdf.output()
    pdf_bytes.write(pdf_output)
    pdf_bytes.seek(0)
    
    return pdf_bytes

@roster_bp.route('/export/pdf', methods=['GET', 'POST'])
@require_auth
def export_pdf():
    """Export roster records as PDF"""
    try:
        # Get records to export (all or filtered)
        records = roster_data
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(records, "Jail Roster Report")
        
        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'jail_roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@roster_bp.route('/export/pdf/email', methods=['POST'])
@require_auth
def export_pdf_email():
    """Export roster records as PDF and send via email"""
    try:
        data = request.get_json()
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({'error': 'Email address required'}), 400
        
        # Email configuration (set these in environment variables or config)
        SENDER_EMAIL = data.get('senderEmail', 'noreply@shakerpd.com')
        SENDER_PASSWORD = data.get('senderPassword', '')  # Should come from environment
        SMTP_SERVER = data.get('smtpServer', 'smtp.gmail.com')
        SMTP_PORT = data.get('smtpPort', 587)
        
        if not SENDER_PASSWORD:
            return jsonify({'error': 'Email credentials not configured'}), 500
        
        # Generate PDF
        records = roster_data
        pdf_bytes = generate_pdf_report(records, "Jail Roster Report")
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f'Jail Roster Report - {datetime.now().strftime("%Y-%m-%d")}'
        
        # Email body
        body = f"""
        Dear Recipient,
        
        Please find attached the Jail Roster Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
        
        This report contains current inmate information and status.
        
        Best regards,
        Jail Roster Management System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(pdf_bytes.getvalue())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename= jail_roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return jsonify({'message': 'Email sent successfully'}), 200
    
    except smtplib.SMTPAuthenticationError:
        return jsonify({'error': 'Email authentication failed. Check credentials.'}), 401
    except smtplib.SMTPException as e:
        return jsonify({'error': f'Email sending failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
