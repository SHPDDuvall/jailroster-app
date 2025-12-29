"""
SQLAlchemy model for the Roster table.
This replaces the in-memory data store with a persistent PostgreSQL database.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Roster(db.Model):
    """Model for jail roster records."""
    
    __tablename__ = 'roster'
    
    # Primary key
    id = db.Column(db.String(50), primary_key=True)
    
    # Basic inmate information
    jail_location = db.Column(db.String(100), default='Solon', nullable=False)
    cell = db.Column(db.String(50), nullable=True)
    day_number = db.Column(db.String(10), nullable=True)
    total_number = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    ssn = db.Column(db.String(20), nullable=True)
    sex_m = db.Column(db.Boolean, default=False)
    sex_f = db.Column(db.Boolean, default=False)
    
    # Arrest and charges
    oca_number = db.Column(db.String(50), nullable=True)
    arrest_date_time = db.Column(db.DateTime, nullable=True)
    misdemeanor = db.Column(db.Boolean, default=False)
    felony = db.Column(db.Boolean, default=False)
    charges = db.Column(db.Text, nullable=True)
    
    # Court information
    court_packet = db.Column(db.String(100), nullable=True)
    inst = db.Column(db.String(100), nullable=True)
    court_case_ticket = db.Column(db.String(100), nullable=True)
    bond_change_notice = db.Column(db.Boolean, default=False)
    bond = db.Column(db.String(100), nullable=True)
    waiver = db.Column(db.String(100), nullable=True)
    court_date = db.Column(db.Date, nullable=True)
    
    # Release information
    release_date_time = db.Column(db.DateTime, nullable=True)
    holders_notes = db.Column(db.Text, nullable=True)
    charging_docs = db.Column(db.String(100), nullable=True)
    
    # Photo storage (Base64 encoded)
    suspect_photo_base64 = db.Column(db.LargeBinary, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert the model to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'jailLocation': self.jail_location,
            'cell': self.cell,
            'dayNumber': self.day_number,
            'totalNumber': self.total_number,
            'name': self.name,
            'dob': self.dob.isoformat() if self.dob else '',
            'ssn': self.ssn or '',
            'sexM': self.sex_m,
            'sexF': self.sex_f,
            'ocaNumber': self.oca_number or '',
            'arrestDateTime': self.arrest_date_time.isoformat() if self.arrest_date_time else '',
            'misdemeanor': self.misdemeanor,
            'felony': self.felony,
            'charges': self.charges or '',
            'courtPacket': self.court_packet or '',
            'inst': self.inst or '',
            'courtCaseTicket': self.court_case_ticket or '',
            'bondChangeNotice': self.bond_change_notice,
            'bond': self.bond or '',
            'waiver': self.waiver or '',
            'courtDate': self.court_date.isoformat() if self.court_date else '',
            'releaseDateTime': self.release_date_time.isoformat() if self.release_date_time else '',
            'holdersNotes': self.holders_notes or '',
            'chargingDocs': self.charging_docs or '',
            'suspectPhotoBase64': self.suspect_photo_base64.decode('utf-8') if self.suspect_photo_base64 else ''
        }
    
    @staticmethod
    def from_dict(data):
        """Create a model instance from a dictionary."""
        from datetime import datetime as dt
        
        # Helper function to parse ISO datetime strings
        def parse_datetime(dt_str):
            if not dt_str:
                return None
            try:
                return dt.fromisoformat(dt_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return None
        
        # Helper function to parse ISO date strings
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return dt.fromisoformat(date_str).date()
            except (ValueError, AttributeError):
                return None
        
        record = Roster(
            jail_location=data.get('jailLocation', 'Solon'),
            cell=data.get('cell', ''),
            day_number=data.get('dayNumber', ''),
            total_number=data.get('totalNumber', ''),
            name=data.get('name', ''),
            dob=parse_date(data.get('dob', '')),
            ssn=data.get('ssn', ''),
            sex_m=data.get('sexM', False),
            sex_f=data.get('sexF', False),
            oca_number=data.get('ocaNumber', ''),
            arrest_date_time=parse_datetime(data.get('arrestDateTime', '')),
            misdemeanor=data.get('misdemeanor', False),
            felony=data.get('felony', False),
            charges=data.get('charges', ''),
            court_packet=data.get('courtPacket', ''),
            inst=data.get('inst', ''),
            court_case_ticket=data.get('courtCaseTicket', ''),
            bond_change_notice=data.get('bondChangeNotice', False),
            bond=data.get('bond', ''),
            waiver=data.get('waiver', ''),
            court_date=parse_date(data.get('courtDate', '')),
            release_date_time=parse_datetime(data.get('releaseDateTime', '')),
            holders_notes=data.get('holdersNotes', ''),
            charging_docs=data.get('chargingDocs', ''),
        )
        
        # Handle photo data
        photo_data = data.get('suspectPhotoBase64', '')
        if photo_data:
            record.suspect_photo_base64 = photo_data.encode('utf-8') if isinstance(photo_data, str) else photo_data
        
        return record
