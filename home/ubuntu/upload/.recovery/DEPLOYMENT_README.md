# Jail Roster Management System - Deployment Guide

## System Overview
A secure web-based jail roster management system with role-based authentication, data correction capabilities, and Excel import/export functionality.

## Demo Credentials
- **Administrator**: `admin` / `admin123` (Full access)
- **Supervisor**: `supervisor` / `supervisor123` (Import/export, delete records)
- **Officer**: `officer` / `officer123` (View and edit records)

## Quick Start

### Frontend (React)
```bash
cd jail-roster-app
npm install
npm run dev
# Access at http://localhost:5173
```

### Backend (Flask)
```bash
cd jail-roster-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
# Access at http://localhost:5000
```

### Full-Stack Deployment
1. Build the React frontend:
   ```bash
   cd jail-roster-app
   npm run build
   ```

2. Copy build files to Flask static directory:
   ```bash
   cp -r dist/* ../jail-roster-backend/src/static/
   ```

3. Start Flask server:
   ```bash
   cd ../jail-roster-backend
   source venv/bin/activate
   python src/main.py
   ```

4. Access the application at `http://localhost:5000`

## Security Features
- Session-based authentication
- Role-based access control
- Password hashing
- Input validation and sanitization
- 8-hour session timeout

## Key Features
- **Secure Login**: Multi-role authentication system
- **Data Management**: CRUD operations for inmate records
- **Excel Integration**: Import/export capabilities
- **Search & Filter**: Real-time data filtering
- **Responsive Design**: Mobile and desktop compatible
- **Professional UI**: Law enforcement appropriate interface

## File Structure
```
jail-roster-app/          # React frontend
├── src/
│   ├── components/       # UI components
│   ├── App.jsx          # Main application
│   └── ...
├── package.json
└── ...

jail-roster-backend/      # Flask backend
├── src/
│   ├── routes/          # API endpoints
│   ├── models/          # Database models
│   ├── static/          # Frontend build files
│   └── main.py          # Flask application
├── requirements.txt
└── ...
```

## Production Considerations
- Change the Flask secret key in `src/main.py`
- Use a proper database (PostgreSQL/MySQL) instead of in-memory storage
- Implement proper password policies
- Add HTTPS/SSL certificates
- Configure proper logging and monitoring
- Set up backup procedures for data

## Support
This system is designed for internal/private network deployment with appropriate security measures for handling sensitive inmate data.
