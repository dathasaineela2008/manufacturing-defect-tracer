# Deployment Guide — MDTPS

This guide explains how to deploy the **Manufacturing Defect Traceability and Prediction System (MDTPS)** to cloud hosting platforms.

The project is pre-configured with:
- [`vercel.json`](file:///f:/Desktop/2nd/project/cursor/vercel.json) — Vercel serverless functions configuration
- [`api/index.py`](file:///f:/Desktop/2nd/project/cursor/api/index.py) — Vercel serverless WSGI entrypoint with `/tmp` SQLite handling
- [`.vercelignore`](file:///f:/Desktop/2nd/project/cursor/.vercelignore) — Excludes `venv`, cache, and local files
- [`Procfile`](file:///f:/Desktop/2nd/project/cursor/Procfile) — Standard WSGI deployment file for Render, Railway, and Heroku

---

## Option 1: Deploy on Vercel (Recommended Cloud Serverless)

### Prerequisites
1. A free [GitHub](https://github.com) account.
2. A free [Vercel](https://vercel.com) account (Sign in with your GitHub account).

---

### Step-by-Step Deployment via GitHub & Vercel Dashboard

#### Step 1: Push your project to GitHub
Open PowerShell in the project directory:

```powershell
# 1. Initialize git if not already initialized
git init

# 2. Add all files
git add .

# 3. Commit the files
git commit -m "Initial MDTPS deployment commit"

# 4. Create a new repository on GitHub (e.g. named mdtps)
# 5. Link your local repo to GitHub and push:
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/mdtps.git
git push -u origin main
```

#### Step 2: Import into Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **"Add New..."** → **"Project"**.
3. Under **"Import Git Repository"**, find your `mdtps` repository and click **"Import"**.
4. Configure Project Settings:
   - **Framework Preset**: Select `Other` (Vercel automatically detects `@vercel/python` from [`vercel.json`](file:///f:/Desktop/2nd/project/cursor/vercel.json)).
   - **Root Directory**: `./` (leave default).
5. **Environment Variables** (Optional):
   Expand the **Environment Variables** section and add:
   - `SECRET_KEY`: `production-academic-key-12345`
   *(If using an external cloud MySQL database like Aiven or PlanetScale, also add `DB_ENGINE=mysql`, `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`). By default, SQLite works out of the box.*
6. Click **"Deploy"**.

#### Step 3: Access your Live App
- Vercel will build the Python environment and deploy the application in ~1-2 minutes.
- You will receive a live URL: `https://mdtps-xyz.vercel.app`.
- Sign in with:
  - **Username**: `admin`
  - **Password**: `Admin@123`

---

### Alternative: Deploy Using the Vercel CLI (Command Line)

If you have Node.js installed, you can deploy directly from your terminal:

```powershell
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Log in to Vercel
vercel login

# 3. Deploy to preview
vercel

# 4. Deploy to production
vercel --prod
```

---

## Option 2: Deploy on Render.com (Easiest Persistent Web Service)

Render provides an always-on web service with persistent disk support and automatic SSL.

1. Create a free account at [render.com](https://render.com).
2. Click **"New +"** → **"Web Service"**.
3. Connect your GitHub repository.
4. Fill in the service details:
   - **Name**: `mdtps-traceability`
   - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python -m app.seed && python ml/train_model.py`
   - **Start Command**: `gunicorn run:app`
5. Click **"Create Web Service"**.
6. Render deploys your app with a free `https://mdtps-traceability.onrender.com` URL.

---

## Option 3: Deploy on Railway.app

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **"New Project"** → **"Deploy from GitHub repo"**.
3. Select your `mdtps` repository.
4. Railway automatically detects `requirements.txt` and [`Procfile`](file:///f:/Desktop/2nd/project/cursor/Procfile).
5. Under service settings, click **"Generate Domain"** to get your public URL.

---

## Technical Notes for Cloud Deployments

1. **Database Handling on Serverless (Vercel)**:
   - Serverless functions (like AWS Lambda and Vercel) have a **read-only** root file system. Only the `/tmp` folder is writable.
   - [`api/index.py`](file:///f:/Desktop/2nd/project/cursor/api/index.py) automatically detects the Vercel serverless environment and copies the pre-seeded SQLite database to `/tmp/mdtps.sqlite3`, enabling both read operations and write operations (like registering a new product or defect) without errors.
2. **Switching to a Cloud MySQL Database**:
   - If you want persistent shared storage across all sessions, sign up for a free cloud MySQL database (such as **Aiven for MySQL**, **TiDB Cloud**, or **Railway MySQL**).
   - In your Vercel or Render dashboard, add the environment variables:
     ```ini
     DB_ENGINE=mysql
     MYSQL_HOST=your-cloud-host.com
     MYSQL_PORT=3306
     MYSQL_USER=your_user
     MYSQL_PASSWORD=your_password
     MYSQL_DATABASE=mdtps
     ```
   - The application automatically switches from SQLite to MySQL without changing any code.
