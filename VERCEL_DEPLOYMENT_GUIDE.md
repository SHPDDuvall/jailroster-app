# Vercel Deployment Guide for Jail Roster Application

This guide provides step-by-step instructions to deploy your jail roster application to **Vercel**, a modern serverless platform.

## ⚠️ Important: Database Requirement

**Vercel is a serverless platform**, which means:
- The Flask backend runs as **serverless functions** (no persistent processes)
- The in-memory data store **will NOT work** on Vercel
- **You MUST connect a persistent database** (PostgreSQL, MySQL, MongoDB, etc.)

Recommended options:
1. **Vercel Postgres** (easiest, integrated with Vercel)
2. **Supabase** (PostgreSQL with free tier)
3. **PlanetScale** (MySQL with free tier)
4. **MongoDB Atlas** (NoSQL with free tier)

## Prerequisites

1. **Vercel Account**: Create a free account at https://vercel.com
2. **GitHub Account**: Your project must be on GitHub
3. **Git Installed**: On your local machine
4. **Database Account**: PostgreSQL, MySQL, or MongoDB (see options above)

## Step 1: Prepare the Project for GitHub

### 1.1 Extract the Archive

Extract the `jailroster-render-ready.zip` on your local machine:

```powershell
# PowerShell
Expand-Archive -Path "C:\Users\YourUser\Downloads\jailroster-render-ready.zip" -DestinationPath .
cd jailroster.shakerpd.com
```

### 1.2 Restructure for Vercel

Vercel expects the backend to be in an `api` folder. Restructure the project:

```powershell
# Create the api folder
mkdir api

# Move the backend into the api folder
Move-Item jail-roster-backend\* api\

# Remove the empty directory
Remove-Item jail-roster-backend -Force

# Keep the frontend at the root
# (jail-roster-app remains at root)
```

### 1.3 Create vercel.json

Create a `vercel.json` file in the root directory:

```json
{
  "version": 2,
  "buildCommand": "cd jail-roster-app && npm install && npm run build",
  "outputDirectory": "jail-roster-app/dist",
  "env": {
    "PYTHON_VERSION": "3.11"
  },
  "functions": {
    "api/src/main.py": {
      "runtime": "python3.11",
      "memory": 1024
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/src/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "jail-roster-app/dist/index.html"
    }
  ]
}
```

### 1.4 Update .gitignore

Create or update `.gitignore` in the root:

```
node_modules/
venv/
__pycache__/
*.pyc
.env.local
.DS_Store
dist/
.vercel
```

### 1.5 Initialize Git and Push to GitHub

```powershell
git init
git add .
git commit -m "Initial commit: Jail Roster Application for Vercel"

# Create a new repository on GitHub (https://github.com/new)
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/jail-roster-app.git
git branch -M main
git push -u origin main
```

## Step 2: Set Up a Database

### Option A: Vercel Postgres (Recommended)

1. Go to https://vercel.com/dashboard
2. Click **Storage** → **Create Database** → **Postgres**
3. Follow the prompts to create a PostgreSQL database
4. Copy the **POSTGRES_URL_NON_POOLING** connection string
5. You will use this in Step 3

### Option B: Supabase (Free PostgreSQL)

1. Go to https://supabase.com
2. Create a new project
3. Go to **Project Settings** → **Database**
4. Copy the **Connection String** (PostgreSQL URI)
5. You will use this in Step 3

### Option C: PlanetScale (Free MySQL)

1. Go to https://planetscale.com
2. Create a new database
3. Go to **Connect** → **Python**
4. Copy the connection string
5. You will use this in Step 3

## Step 3: Deploy to Vercel

### 3.1 Connect GitHub to Vercel

1. Go to https://vercel.com/dashboard
2. Click **Add New...** → **Project**
3. Click **Import Git Repository**
4. Select your `jail-roster-app` repository
5. Click **Import**

### 3.2 Configure Environment Variables

1. In the **Configure Project** screen, go to **Environment Variables**
2. Add the following variables:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `DATABASE_URL` | Your database connection string | From Step 2 |
| `SECRET_KEY` | A random 32+ character string | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SMTP_SERVER` | `smtp.gmail.com` | For email functionality |
| `SMTP_PORT` | `587` | Standard SMTP port |
| `SENDER_EMAIL` | Your email address | For sending reports |
| `SENDER_PASSWORD` | Your app password | Gmail app password (see email setup below) |

3. Click **Deploy**

Vercel will now build and deploy your application. This may take 5-10 minutes.

### 3.3 Wait for Deployment

- Monitor the deployment progress in the Vercel dashboard
- Once complete, you will receive a public URL (e.g., `https://jail-roster-app.vercel.app`)

## Step 4: Configure Your Custom Domain

To use your custom domain (`jailroster.shakerpd.com`):

1. In your Vercel project, go to **Settings** → **Domains**
2. Click **Add Domain**
3. Enter `jailroster.shakerpd.com`
4. Follow the instructions to update your domain's DNS records
5. Vercel will provide the DNS records you need to add

## Step 5: Set Up Email (Optional)

### Using Gmail

1. **Enable 2-Factor Authentication**:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password

3. **Update Vercel Environment Variables**:
   - Go to your Vercel project → **Settings** → **Environment Variables**
   - Update:
     ```
     SENDER_EMAIL = your-email@gmail.com
     SENDER_PASSWORD = your-16-character-app-password
     ```

4. **Redeploy**:
   - Go to **Deployments** → **Redeploy** the latest commit

## Step 6: Test the Application

1. Visit your Vercel URL or custom domain
2. Log in with demo credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Test all features:
   - Add a new record
   - Upload a photo
   - Export to PDF
   - Send an email report

## Troubleshooting

### Application Not Loading

**Check the Vercel logs:**
1. Go to your Vercel project
2. Click **Deployments** → **Latest Deployment**
3. Click **Functions** to see backend logs
4. Look for error messages

**Common issues:**
- **Module not found**: Ensure `requirements.txt` is in the `api` folder
- **Database connection error**: Verify `DATABASE_URL` is correct
- **Port binding error**: Ensure the start command includes `$PORT`

### Database Connection Failed

```
Error: could not translate host name "host" to address
```

**Solutions:**
- Verify the database connection string is correct
- Ensure the database is running and accessible
- Check that your IP address is whitelisted (if required by your database provider)

### Email Not Sending

```
Error: Email authentication failed
```

**Solutions:**
- For Gmail: Use an App Password (not your regular password)
- Verify SMTP credentials are correct
- Check that 2-Factor Authentication is enabled (for Gmail)

### Static Files Not Loading

If the React frontend is not loading:
1. Ensure the React build was successful
2. Check that `jail-roster-app/dist/` contains the built files
3. Verify the `vercel.json` routes are correct

## Limitations of Serverless

### What Works
- ✅ API endpoints (CRUD operations)
- ✅ PDF generation
- ✅ Email sending
- ✅ Static file serving (React frontend)

### What Doesn't Work
- ❌ In-memory data storage (data is lost between requests)
- ❌ Long-running background jobs (12-second timeout)
- ❌ WebSocket connections (not supported)
- ❌ Persistent file uploads (use S3 or external storage)

### Workarounds
- **Use a persistent database** (PostgreSQL, MySQL, MongoDB)
- **Use external storage** (AWS S3, Google Cloud Storage)
- **Use external services** for long-running tasks (e.g., Stripe webhooks)

## Scaling and Performance

### For Production
1. **Upgrade the Vercel plan**: Free plans have limited resources
2. **Use a paid database plan**: Free databases may have limitations
3. **Enable automatic scaling**: Vercel handles this automatically
4. **Use a CDN**: Vercel includes Vercel Edge Network by default

### Monitoring
1. Go to your Vercel project → **Analytics**
2. Monitor:
   - Request count
   - Response time
   - Error rate
   - Bandwidth usage

## Database Migrations

If you need to modify the database schema:

1. **Update the model** in `api/src/models/roster.py`
2. **Commit and push** to GitHub:
   ```powershell
   git add .
   git commit -m "Update database schema"
   git push origin main
   ```
3. Vercel will automatically redeploy
4. The new tables will be created automatically on startup

## Useful Commands

### Local Testing

Before deploying to Vercel, test locally:

```powershell
# Install dependencies
pip install -r api/requirements.txt
npm install --prefix jail-roster-app

# Build the frontend
npm run build --prefix jail-roster-app

# Run the Flask app locally (set DATABASE_URL first)
$env:DATABASE_URL="postgresql://user:password@localhost/jailroster"
python api/src/main.py
```

### Vercel CLI

Install and use the Vercel CLI for local development:

```powershell
# Install Vercel CLI
npm install -g vercel

# Log in to Vercel
vercel login

# Deploy
vercel

# View logs
vercel logs
```

## Support and Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Support**: https://support.vercel.com
- **Flask Documentation**: https://flask.palletsprojects.com
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **Database Providers**:
  - Vercel Postgres: https://vercel.com/docs/storage/vercel-postgres
  - Supabase: https://supabase.com/docs
  - PlanetScale: https://planetscale.com/docs
  - MongoDB Atlas: https://www.mongodb.com/docs/atlas

## Next Steps

1. ✅ Extract the archive and restructure for Vercel
2. ✅ Create a GitHub repository
3. ✅ Set up a database
4. ✅ Deploy to Vercel
5. ✅ Configure your custom domain
6. ✅ Set up email
7. ✅ Test all features
8. ✅ Monitor and maintain

---

**Congratulations!** Your jail roster application is now deployed on Vercel with a persistent database!
