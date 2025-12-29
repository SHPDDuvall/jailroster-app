from flask import Blueprint, request, jsonify, send_file, current_app
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from .auth import require_auth, require_role

from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont

roster_bp = Blueprint('roster', __name__)

# In-memory storage for demo purposes
roster_data = []
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --------------------------------------------------------------------
# ROSTER LIST – TEMPORARILY OPEN (NO AUTH CHECK)
# --------------------------------------------------------------------
@roster_bp.route('/', methods=['GET'])
def get_roster():
    """
    Get all roster records.

    NOTE: This endpoint is intentionally left open (no @require_auth)
    so the frontend can load data without hitting a 401 while we finish
    deployment and debug auth/session behavior.
    """
    return jsonify(roster_data)


@roster_bp.route('/', methods=['POST'])
@require_auth
def add_roster_record():
    """Add a new roster record"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Add timestamp and ID if not provided
        if 'id' not in data:
            data['id'] = str(len(roster_data) + 1)

        roster_data.append(data)
        return jsonify({'message': 'Record added successfully', 'record': data}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@roster_bp.route('/<record_id>', methods=['PUT'])
@require_auth
def update_roster_record(record_id):
    """Update an existing roster record"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Find and update the record
        for i, record in enumerate(roster_data):
            if record.get('id') == record_id:
                roster_data[i] = {**record, **data}
                return jsonify({'message': 'Record updated successfully', 'record': roster_data[i]})

        return jsonify({'error': 'Record not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@roster_bp.route('/<record_id>', methods=['DELETE'])
@require_role('supervisor')
def delete_roster_record(record_id):
    """Delete a roster record"""
    try:
        global roster_data
        roster_data = [record for record in roster_data if record.get('id') != record_id]
        return jsonify({'message': 'Record deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@roster_bp.route('/import', methods=['POST'])
@require_role('supervisor')
def import_excel():
    """Import data from Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload an Excel file.'}), 400

        # Read Excel file
        try:
            # Try reading with header=1 and skip the first data row which contains column names
            df = pd.read_excel(file, header=1)
            df = df.iloc[1:]  # Skip the first row which contains the actual column names

            # Manually set column names based on our analysis
            expected_columns = [
                'CELL', 'Day #', 'Total #', 'NAME', 'DOB', 'SSN', 'Sex_M', 'Sex_F', 'OCA #',
                'Arrest Date/Time', 'Mis', 'Fel', 'Charge(s)', 'Court Packet', 'INST',
                'Court Case Ticket #', 'Bond Chng Notice Y', 'Bond', 'Waiver', 'Court Date',
                'Release Date/Time', 'Holders / Notes', 'Charging Docs filed with Court'
            ]

            # Ensure we have the right number of columns
            if len(df.columns) >= len(expected_columns):
                df.columns = expected_columns[:len(df.columns)]

            # Convert DataFrame to our format
            imported_records = []
            for index, row in df.iterrows():
                if pd.isna(row.get('NAME')) or row.get('NAME') == 'NAME':
                    continue  # Skip empty or header rows

                record = {
                    'id': str(len(roster_data) + len(imported_records) + 1),
                    'cell': str(row.get('CELL', '')).strip() if pd.notna(row.get('CELL')) else '',
                    'dayNumber': str(row.get('Day #', '')).strip() if pd.notna(row.get('Day #')) else '',
                    'totalNumber': str(row.get('Total #', '')).strip() if pd.notna(row.get('Total #')) else '',
                    'name': str(row.get('NAME', '')).strip() if pd.notna(row.get('NAME')) else '',
                    'dob': str(row.get('DOB', '')).strip() if pd.notna(row.get('DOB')) else '',
                    'ssn': str(row.get('SSN', '')).strip() if pd.notna(row.get('SSN')) else '',
                    'sexM': str(row.get('Sex_M', '')).strip().upper() == 'X',
                    'sexF': str(row.get('Sex_F', '')).strip().upper() == 'X',
                    'ocaNumber': str(row.get('OCA #', '')).strip() if pd.notna(row.get('OCA #')) else '',
                    'arrestDateTime': str(row.get('Arrest Date/Time', '')).strip() if pd.notna(row.get('Arrest Date/Time')) else '',
                    'misdemeanor': str(row.get('Mis', '')).strip().upper() == 'X',
                    'felony': str(row.get('Fel', '')).strip().upper() == 'X',
                    'charges': str(row.get('Charge(s)', '')).strip() if pd.notna(row.get('Charge(s)')) else '',
                    'courtPacket': str(row.get('Court Packet', '')).strip() if pd.notna(row.get('Court Packet')) else '',
                    'inst': str(row.get('INST', '')).strip() if pd.notna(row.get('INST')) else '',
                    'courtCaseTicket': str(row.get('Court Case Ticket #', '')).strip() if pd.notna(row.get('Court Case Ticket #')) else '',
                    'bondChangeNotice': str(row.get('Bond Chng Notice Y', '')).strip().upper() == 'Y',
                    'bond': str(row.get('Bond', '')).strip() if pd.notna(row.get('Bond')) else '',
                    'waiver': str(row.get('Waiver', '')).strip() if pd.notna(row.get('Waiver')) else '',
                    'courtDate': str(row.get('Court Date', '')).strip() if pd.notna(row.get('Court Date')) else '',
                    'releaseDateTime': str(row.get('Release Date/Time', '')).strip() if pd.notna(row.get('Release Date/Time')) else '',
                    'holdersNotes': str(row.get('Holders / Notes', '')).strip() if pd.notna(row.get('Holders / Notes')) else '',
                    'chargingDocs': str(row.get('Charging Docs filed with Court', '')).strip() if pd.notna(row.get('Charging Docs filed with Court')) else ''
                }
                imported_records.append(record)

            # Add imported records to roster_data
            roster_data.extend(imported_records)

            return jsonify({
                'message': f'Successfully imported {len(imported_records)} records',
                'imported_count': len(imported_records),
                'total_records': len(roster_data)
            })

        except Exception as e:
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@roster_bp.route('/export', methods=['GET'])
@require_auth
def export_excel():
    """Export data to Excel file"""
    try:
        if not roster_data:
            return jsonify({'error': 'No data to export'}), 400

        # Convert roster data to DataFrame
        export_data = []
        for record in roster_data:
            export_row = {
                'CELL': record.get('cell', ''),
                'Day #': record.get('dayNumber', ''),
                'Total #': record.get('totalNumber', ''),
                'NAME': record.get('name', ''),
                'DOB': record.get('dob', ''),
                'SSN': record.get('ssn', ''),
                'Sex_M': 'X' if record.get('sexM') else '',
                'Sex_F': 'X' if record.get('sexF') else '',
                'OCA #': record.get('ocaNumber', ''),
                'Arrest Date/Time': record.get('arrestDateTime', ''),
                'Mis': 'X' if record.get('misdemeanor') else '',
                'Fel': 'X' if record.get('felony') else '',
                'Charge(s)': record.get('charges', ''),
                'Court Packet': record.get('courtPacket', ''),
                'INST': record.get('inst', ''),
                'Court Case Ticket #': record.get('courtCaseTicket', ''),
                'Bond Chng Notice Y': 'Y' if record.get('bondChangeNotice') else '',
                'Bond': record.get('bond', ''),
                'Waiver': record.get('waiver', ''),
                'Court Date': record.get('courtDate', ''),
                'Release Date/Time': record.get('releaseDateTime', ''),
                'Holders / Notes': record.get('holdersNotes', ''),
                'Charging Docs filed with Court': record.get('chargingDocs', '')
            }
            export_data.append(export_row)

        df = pd.DataFrame(export_data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Add header rows similar to original format
            header_df = pd.DataFrame([
                ['Master Jail Roster', f'Date: {datetime.now().strftime("%A, %B %d, %Y")}'] + [''] * (len(df.columns) - 2),
                df.columns.tolist()
            ])
            header_df.to_excel(writer, sheet_name='Jail Roster', index=False, header=False)

            # Add the actual data starting from row 3
            df.to_excel(writer, sheet_name='Jail Roster', index=False, header=False, startrow=2)

        output.seek(0)

        filename = f"jail_roster_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
@roster_bp.route('/<record_id>/photo', methods=['POST'])
@require_auth
def upload_mugshot(record_id):
    """Upload and watermark a mugshot for a roster record"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use PNG or JPG.'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        return jsonify({'error': 'Upload folder not configured'}), 500

    os.makedirs(upload_folder, exist_ok=True)

    # Make a safe filename, tied to the record id
    filename = secure_filename(f"{record_id}_{file.filename}")
    save_path = os.path.join(upload_folder, filename)

    # Save original
    file.save(save_path)

    # Open and apply watermark
    try:
        img = Image.open(save_path).convert("RGBA")
    except Exception as e:
        return jsonify({'error': f'Error processing image: {e}'}), 400

    width, height = img.size

    watermark_text = "SHAKER HEIGHTS POLICE"
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Simple font; default built-in
    font_size = max(18, width // 30)
    try:
        # If you later add a TTF, you can use ImageFont.truetype(...)
        font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(watermark_text, font=font)
    x = (width - text_width) / 2
    y = height - text_height - 10

    draw.text((x, y), watermark_text, fill=(255, 255, 255, 160), font=font)
    watermarked = Image.alpha_composite(img, overlay).convert("RGB")
    watermarked.save(save_path, "JPEG", quality=85)

    # Attach to the in-memory record
    for record in roster_data:
        if record.get('id') == record_id:
            record['photoFilename'] = filename
            record['photoUrl'] = f"/api/roster/{record_id}/photo"
            break

    return jsonify({'message': 'Photo uploaded successfully'}), 200


@roster_bp.route('/<record_id>/photo', methods=['GET'])
@require_auth
def get_mugshot(record_id):
    """Return the mugshot image file for a record"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        return jsonify({'error': 'Upload folder not configured'}), 500

    filename = None
    for record in roster_data:
        if record.get('id') == record_id:
            filename = record.get('photoFilename')
            break

    if not filename:
        return jsonify({'error': 'Photo not found'}), 404

    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Photo file missing on server'}), 404

    return send_file(file_path, mimetype='image/jpeg')


@roster_bp.route('/clear', methods=['POST'])
@require_role('administrator')
def clear_roster():
    """Clear all roster data"""
    try:
        global roster_data
        roster_data = []
        return jsonify({'message': 'All records cleared successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
