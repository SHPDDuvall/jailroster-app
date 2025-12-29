# Photo Management Integration Guide

This guide explains how to integrate the photo management feature into your jail roster application.

## Overview

The photo management feature allows you to:
- Upload suspect photos during record creation or editing
- Display photo thumbnails in the main roster table
- View full-size photos in a modal by clicking on thumbnails
- Store photos as Base64-encoded strings in the database

## Files to Update

### 1. Frontend: `jail-roster-app/src/App.jsx`

**Replace the entire `App.jsx` file with `App_with_photos.jsx`**

Key changes:
- Added `selectedPhotoRecord` state for photo modal management
- Added `expandedRecordId` state for expanding row details
- Added photo column to the main table with thumbnail display
- Implemented photo modal for full-size viewing
- Updated `EditRecordForm` component with photo upload functionality
- Added Base64 photo preview in the form

### 2. Backend: `jail-roster-backend/src/routes/roster_simple.py`

**Replace the entire `roster_simple.py` file with `roster_simple_with_photos.py`**

Key changes:
- Added `suspectPhotoBase64` field to the data model
- Updated all CRUD operations to handle photo data
- Photos are stored as Base64-encoded strings in memory
- No external file storage needed (can be upgraded to S3 later)

## Installation Steps

1. **Extract the project archive**
   ```bash
   unzip jail-roster-system-source.zip
   cd jail-roster-backend
   ```

2. **Update the frontend**
   ```bash
   cp App_with_photos.jsx jail-roster-app/src/App.jsx
   ```

3. **Update the backend**
   ```bash
   cp roster_simple_with_photos.py src/routes/roster_simple.py
   ```

4. **Rebuild the frontend**
   ```bash
   cd jail-roster-app
   pnpm install
   pnpm run build
   cd ..
   cp -r jail-roster-app/dist/* src/static/
   ```

5. **Install backend dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Run the application**
   ```bash
   python src/main.py
   ```

## Features

### Photo Upload
- Click the photo upload area in the Add/Edit form
- Select an image file from your computer
- The image is converted to Base64 and stored with the record

### Photo Display
- Thumbnails appear in the first column of the roster table
- Hover over a thumbnail to see a zoom icon
- Click the thumbnail to view the full-size photo in a modal

### Photo Storage
- Photos are stored as Base64-encoded strings
- This approach works well for the demo and development
- For production, consider upgrading to S3 or local file storage

## Future Enhancements

### Option 1: Local File Storage
Replace Base64 storage with local file uploads:
```python
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# In the update_record route:
if 'photo' in request.files:
    file = request.files['photo']
    if file and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(f"{record_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        record['photo_path'] = f"/uploads/photos/{filename}"
```

### Option 2: AWS S3 Storage
Upload photos to S3 for scalable cloud storage:
```python
import boto3

s3 = boto3.client('s3')

def upload_photo_to_s3(file, record_id):
    key = f"photos/{record_id}/{file.filename}"
    s3.upload_fileobj(file, 'your-bucket-name', key)
    return f"https://your-bucket-name.s3.amazonaws.com/{key}"
```

### Option 3: Database BLOB Storage
Store photos directly in the database:
```python
# Using SQLAlchemy
from sqlalchemy import LargeBinary

class RosterRecord(db.Model):
    id = db.Column(db.String, primary_key=True)
    photo_data = db.Column(LargeBinary)
    # ... other fields
```

## Troubleshooting

### Photos not displaying
- Ensure the Base64 string is properly formatted: `data:image/jpeg;base64,...`
- Check browser console for errors

### Large file sizes
- Consider compressing images before upload
- Implement image resizing on the backend

### Performance issues
- If storing many large photos, consider lazy loading
- Implement pagination for the roster table

## Support

For issues or questions about the photo management feature, refer to the main `DEPLOYMENT_README.md` for general deployment instructions.
