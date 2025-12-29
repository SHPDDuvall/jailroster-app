# Render Deployment Guide for Jail Roster Application

This guide provides step-by-step instructions to deploy your jail roster application to **Render**, a modern cloud platform that supports full-stack applications.

## Prerequisites

1. **Render Account**: Create a free account at https://render.com
2. **GitHub Account**: Your project must be hosted on GitHub
3. **Git Installed**: Git must be installed on your local machine
4. **PowerShell or Terminal**: For running commands

## Step 1: Prepare Your Project for Git

### 1.1 Extract the Archive

Extract the `jailroster-shakerpd-updated.zip` file on your local machine:

```powershell
# PowerShell
Expand-Archive -Path "C:\Users\YourUser\Downloads\jailroster-shakerpd-updated.zip" -DestinationPath .
cd jailroster.shakerpd.com
```

### 1.2 Initialize Git Repository

```powershell
git init
git add .
git commit -m "Initial commit: Jail Roster Application with database support"
```

### 1.3 Create a GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `jail-roster-app`
3. **Do NOT initialize with README, .gitignore, or license** (you already have these)
4. Click **Create repository**

### 1.4 Push to GitHub

Copy the commands from your newly created GitHub repository and run them in PowerShell:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/jail-roster-app.git
git branch -M main
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username.

## Step 2: Create PostgreSQL Database on Render

1. **Log in** to your Render dashboard at https://dashboard.render.com
2. Click **New +** → **PostgreSQL**
3. Fill in the following details:

| Field | Value | Notes |
| :--- | :--- | :--- |
| **Name** | `jail-roster-db` | Any name you prefer |
| **Database** | `jailroster` | Database name |
| **User** | `jailroster` | Database user |
| **Region** | Same as your web service | Choose a region close to you |
| **PostgreSQL Version** | 15 | Latest stable version |

4. Click **Create Database**
5. **IMPORTANT**: Copy the **Internal Database URL** (it will look like `postgresql://user:password@host:5432/database`)
   - You will need this in the next step

## Step 3: Create Web Service on Render

1. Click **New +** → **Web Service**
2. **Connect your GitHub repository**:
   - Click **Connect account** if you haven't already
   - Select your `jail-roster-app` repository
   - Click **Connect**

3. **Configure the Web Service**:

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Name** | `jail-roster-backend` | |
| **Environment** | `Python 3` | |
| **Region** | Same as database | For optimal performance |
| **Branch** | `main` | |
| **Root Directory** | `jail-roster-backend` | Leave blank if not needed |
| **Build Command** | `pip install -r requirements.txt` | |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT src.main:app` | |

4. **Set Environment Variables** (Crucial):

Click **Advanced** and add the following environment variables:

```
DATABASE_URL = postgresql://user:password@host:5432/jailroster
SECRET_KEY = your-random-secret-key-here
PYTHON_VERSION = 3.11
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SENDER_EMAIL = your-email@gmail.com
SENDER_PASSWORD = your-app-password
```

**Important Notes:**
- **DATABASE_URL**: Paste the Internal Database URL from Step 2
- **SECRET_KEY**: Generate a random string (at least 32 characters). You can use: `python -c "import secrets; print(secrets.token_hex(32))"`
- **SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD**: Configure for email functionality (see Email Setup section below)

5. **Plan Selection**:
   - Select **Free** for testing (limited resources)
   - Select **Starter** or higher for production

6. Click **Create Web Service**

Render will now build and deploy your application. This may take 5-10 minutes.

## Step 4: Verify Deployment

1. Once the deployment is complete, Render will provide you with a public URL (e.g., `https://jail-roster-backend.onrender.com`)
2. Visit the URL in your browser
3. Log in with the demo credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

## Step 5: Configure Email (Optional but Recommended)

### Using Gmail

1. **Enable 2-Factor Authentication** on your Google Account:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password

3. **Update Render Environment Variables**:
   - Go to your Web Service settings on Render
   - Update the following variables:
     ```
     SMTP_SERVER = smtp.gmail.com
     SMTP_PORT = 587
     SENDER_EMAIL = your-email@gmail.com
     SENDER_PASSWORD = your-16-character-app-password
     ```

4. **Redeploy**: Render will automatically redeploy with the new environment variables

### Using Office 365

```
SMTP_SERVER = smtp.office365.com
SMTP_PORT = 587
SENDER_EMAIL = your-email@yourdomain.onmicrosoft.com
SENDER_PASSWORD = your-office-365-password
```

### Using Custom SMTP Server

```
SMTP_SERVER = your-smtp-server.com
SMTP_PORT = 587 (or 25, 465)
SENDER_EMAIL = your-email@yourdomain.com
SENDER_PASSWORD = your-password
```

## Step 6: Custom Domain (Optional)

To use a custom domain (e.g., `jailroster.shakerpd.com`):

1. In your Render Web Service settings, go to **Settings** → **Custom Domain**
2. Enter your domain name
3. Follow the DNS configuration instructions provided by Render
4. Update your domain's DNS records with the values Render provides

## Troubleshooting

### Application Not Starting

**Check the logs:**
1. Go to your Web Service on Render
2. Click **Logs** tab
3. Look for error messages

**Common issues:**
- **Missing dependencies**: Ensure `requirements.txt` is in the correct location
- **Database connection error**: Verify the `DATABASE_URL` environment variable is correct
- **Port binding error**: Ensure the start command includes `$PORT`

### Database Connection Issues

```
Error: could not translate host name "host" to address
```

**Solution:**
- Verify the `DATABASE_URL` is correct
- Ensure the database is in the same region as the web service
- Check that the database is not paused (Render pauses free databases after 7 days of inactivity)

### Email Not Sending

```
Error: Email authentication failed
```

**Solutions:**
- Verify SMTP credentials are correct
- For Gmail, ensure you're using an App Password (not your regular password)
- Check that 2-Factor Authentication is enabled on your Gmail account
- Verify the SMTP server and port are correct

### Static Files Not Loading

If the React frontend is not loading:
1. Ensure the React frontend was built and placed in `jail-roster-backend/src/static/`
2. Verify the Flask app is serving static files correctly
3. Check the browser console for 404 errors

## Database Migrations

If you need to modify the database schema:

1. **Update the model** in `src/models/roster.py`
2. **Commit and push** to GitHub:
   ```powershell
   git add .
   git commit -m "Update database schema"
   git push origin main
   ```
3. Render will automatically redeploy
4. The new tables will be created automatically on startup

## Monitoring and Maintenance

### View Logs

1. Go to your Web Service on Render
2. Click **Logs** to see real-time application logs

### Monitor Database

1. Go to your PostgreSQL database on Render
2. Click **Info** to see connection details and usage statistics

### Restart Service

If the application becomes unresponsive:
1. Go to your Web Service
2. Click **Manual Deploy** → **Deploy latest commit**

## Scaling and Performance

### For Production

1. **Upgrade the plan**: Free plans may be limited in resources
2. **Use a paid PostgreSQL plan**: Free databases have limitations
3. **Enable auto-scaling**: Configure auto-scaling in Web Service settings
4. **Use a CDN**: For static assets, consider using a CDN like Cloudflare

## Security Best Practices

1. **Change the SECRET_KEY**: Generate a new random key for production
2. **Use strong passwords**: For email and database credentials
3. **Enable HTTPS**: Render provides free HTTPS by default
4. **Restrict database access**: Only allow connections from your web service
5. **Regular backups**: Render provides automated backups for paid plans

## Useful Render Commands

### View Deployment Logs

```powershell
# Via Render Dashboard
# Go to Web Service → Logs
```

### Manual Redeploy

```powershell
# Via Render Dashboard
# Go to Web Service → Manual Deploy → Deploy latest commit
```

### Environment Variables

```powershell
# View in Render Dashboard
# Go to Web Service → Environment
```

## Support and Resources

- **Render Documentation**: https://render.com/docs
- **Render Support**: https://support.render.com
- **Flask Documentation**: https://flask.palletsprojects.com
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org

## Next Steps

1. Test all features (add records, upload photos, export PDF, send email)
2. Configure your custom domain
3. Set up monitoring and alerts
4. Plan for database backups
5. Document any custom configurations for your team

---

**Congratulations!** Your jail roster application is now deployed on Render with a persistent PostgreSQL database!
