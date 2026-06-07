# BodyOps — Setup Guide

Complete this in order. Each section depends on the previous one.

---

## Prerequisites — Install These First

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 20+ | https://nodejs.org |
| Python | 3.12 | https://python.org |
| Git | any | https://git-scm.com |
| Vercel CLI | latest | `npm i -g vercel` |

---

## Step 1 — Azure OpenAI

You need an Azure subscription for this.

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search **"Azure OpenAI"** → click **Create**
3. Fill in:
   - Subscription: your subscription
   - Resource group: create new → `bodyops-rg`
   - Region: pick one close to you (e.g. `East US`)
   - Name: `bodyops-openai`
   - Pricing tier: `Standard S0`
4. Click **Review + Create** → **Create** (takes ~2 min)
5. Once deployed, go to the resource → **Keys and Endpoint** (left sidebar)
6. Copy and save:
   - `KEY 1` → this is your `AZURE_OPENAI_API_KEY`
   - `Endpoint` → this is your `AZURE_OPENAI_ENDPOINT` (looks like `https://bodyops-openai.openai.azure.com/`)
7. Now deploy a model: left sidebar → **Model deployments** → **Manage Deployments**
8. Click **+ Deploy model** → select `gpt-4o`
9. Deployment name: `gpt-4o` (or any name you want — this is your `AZURE_OPENAI_DEPLOYMENT`)
10. Click **Deploy**

**Save these 4 values:**
```
AZURE_OPENAI_API_KEY=<KEY 1 from step 6>
AZURE_OPENAI_ENDPOINT=<Endpoint from step 6>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

---

## Step 2 — Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Top bar → click the project dropdown → **New Project**
   - Name: `BodyOps`
   - Click **Create**
3. Make sure the new project is selected in the dropdown

### Enable APIs

4. Left sidebar → **APIs & Services** → **Library**
5. Search **"Google Sheets API"** → click it → **Enable**
6. Search **"Google Drive API"** → click it → **Enable**

### Create Service Account

7. Left sidebar → **APIs & Services** → **Credentials**
8. Click **+ Create Credentials** → **Service Account**
9. Name: `bodyops-service`
10. Click **Create and Continue** → skip role → **Done**
11. Click the service account email in the list to open it
12. Tab → **Keys** → **Add Key** → **Create new key** → JSON → **Create**
13. A JSON file downloads — keep it safe, you'll need its contents

**Save from the JSON file:**
```
GOOGLE_SERVICE_ACCOUNT_EMAIL=bodyops-service@bodyops-<id>.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_JSON=<entire contents of the downloaded JSON file>
```

### Create an API Key (for Auth Sheet access)

14. Left sidebar → **APIs & Services** → **Credentials**
15. Click **+ Create Credentials** → **API Key**
16. Copy the key → click **Edit API key**
17. Under **API restrictions** → select **Restrict key** → tick **Google Sheets API**
18. Click **Save**

**Save:**
```
GOOGLE_SHEETS_API_KEY=<API key from step 16>
```

---

## Step 3 — Google Drive Folder

1. Go to [drive.google.com](https://drive.google.com)
2. Click **+ New** → **New Folder** → name it `BodyOps Meal Images`
3. Right-click the folder → **Share**
4. Paste the service account email (`bodyops-service@...`) → role: **Editor** → **Send**
5. Click the folder to open it → look at the URL:
   `https://drive.google.com/drive/folders/1ABC123XYZ...`
6. Copy the ID after `/folders/`

**Save:**
```
GOOGLE_DRIVE_FOLDER_ID=1ABC123XYZ...
```

---

## Step 4 — Google Sheets (3 Spreadsheets)

### Sheet 1: Main Data Sheet

1. Go to [sheets.google.com](https://sheets.google.com) → click **+** to create new spreadsheet
2. Rename it (top left): `BodyOps - Data`
3. Click **Share** (top right)
4. Paste the service account email → role: **Editor** → **Send**
5. Copy the spreadsheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/1ABC123.../edit`
   The ID is the long string between `/d/` and `/edit`

**Save:**
```
GOOGLE_SPREADSHEET_ID=<ID from step 5>
```

### Sheet 2: Auth Sheet

1. Create another new spreadsheet → rename it `BodyOps - Auth`
2. **Do NOT share this with the service account**
3. In cell A1 type: `email`
4. In cell B1 type: `password`
5. In cell A2 type: your login email (e.g. `jaspal@example.com`)
6. In cell B2 type: your chosen password (plain text)
7. Copy the spreadsheet ID from the URL

**Save:**
```
GOOGLE_AUTH_SHEET_ID=<ID from step 7>
```

### Sheet 3: Chat History Sheet

1. Create another new spreadsheet → rename it `BodyOps - Chat History`
2. Share with the service account email → role: **Editor**
3. Copy the spreadsheet ID from the URL

**Save:**
```
GOOGLE_CHAT_HISTORY_SHEET_ID=<ID from step 3>
```

---

## Step 5 — Python Backend (Local)

### Create env file

In the `api/` folder, create a file called `.env` and paste all saved values:

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":...}
GOOGLE_SPREADSHEET_ID=
GOOGLE_CHAT_HISTORY_SHEET_ID=
GOOGLE_AUTH_SHEET_ID=
GOOGLE_SHEETS_API_KEY=
GOOGLE_DRIVE_FOLDER_ID=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
JWT_SECRET=<generate a random 32+ char string — e.g. run: python -c "import secrets; print(secrets.token_hex(32))">
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
```

> For `GOOGLE_SERVICE_ACCOUNT_JSON`: open the downloaded JSON file, copy the entire contents as a single line string. On Windows you can run:
> `(Get-Content service-account.json -Raw) -replace "`n","" | Set-Clipboard`

### Install dependencies and run setup

```bash
# from repo root
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -e ".[dev]"

# Bootstrap all sheet tabs
python scripts/setup.py
```

`setup.py` will print something like:
```
✓ WeightLogs    — created
✓ Meals         — created
✓ MealItems     — created
...
✓ ChatHistory   — created (in Chat History Sheet)
Setup complete.
```

### Start the API locally

```bash
uvicorn api.main:app --reload --port 8000
```

Verify: open `http://localhost:8000/health` — should return `{"ok":true,"sheets":true,"drive":true}`

---

## Step 6 — Next.js Frontend (Local)

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
```

Open `http://localhost:3000` — you should see the login page.

Test login with the email/password you entered in the Auth Sheet.

---

## Step 7 — Deploy Backend to Hugging Face Spaces

1. Go to [huggingface.co](https://huggingface.co) → sign in (or create a free account — no credit card required)
2. Click **+ New Space** (top right)
3. Configure:
   - **Space name**: `bodyops-api`
   - **License**: MIT
   - **SDK**: **Docker**
   - **Hardware**: CPU Basic (free)
   - **Visibility**: Private (recommended)
4. Click **Create Space**

### Add secrets

In the Space page → **Settings** → **Variables and secrets** → **New secret**, add each env var:

| Secret name | Value |
|-------------|-------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | full JSON contents as a single line |
| `GOOGLE_SPREADSHEET_ID` | … |
| `GOOGLE_CHAT_HISTORY_SHEET_ID` | … |
| `GOOGLE_AUTH_SHEET_ID` | … |
| `GOOGLE_SHEETS_API_KEY` | … |
| `GOOGLE_DRIVE_FOLDER_ID` | … |
| `AZURE_OPENAI_API_KEY` | … |
| `AZURE_OPENAI_ENDPOINT` | … |
| `AZURE_OPENAI_DEPLOYMENT` | gpt-4o |
| `AZURE_OPENAI_API_VERSION` | 2024-08-01-preview |
| `JWT_SECRET` | … |
| `JWT_ALGORITHM` | HS256 |
| `JWT_EXPIRE_MINUTES` | 10080 |

### Deploy

HF Spaces deploys via git push. Add the Space as a remote and push the `api/` folder:

```bash
# Replace <username> with your Hugging Face username
git remote add hf https://huggingface.co/spaces/<username>/bodyops-api

# Push api/ as the Space root
git subtree push --prefix=api hf main
```

HF will build the Docker image and start the container. Watch progress in the Space's **Logs** tab.

Verify once the build is green:
```bash
curl https://<username>-bodyops-api.hf.space/health
```

> **Note:** Free tier Spaces sleep after ~48h of inactivity and take ~30s to wake on first request. Fine for a personal app you use daily.

---

## Step 8 — Deploy Frontend to Vercel

```bash
cd frontend
vercel
```

When prompted:
- Link to existing project? **No** → create new
- Project name: `bodyops`
- Framework: **Next.js** (auto-detected)
- Root directory: `./` (you're already in `frontend/`)

After first deploy, set the environment variable in Vercel:

```bash
vercel env add NEXT_PUBLIC_API_URL production
# enter value: https://<username>-bodyops-api.hf.space
```

Then redeploy to pick up the env var:
```bash
vercel --prod
```

Your app is now live at `https://bodyops.vercel.app` (or your custom domain).

---

## Step 9 — Point CORS at Vercel URL

In `api/main.py`, update the CORS origins to include your Vercel URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://bodyops.vercel.app",   # ← your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the API:
```bash
git subtree push --prefix=api hf main
```

---

## Final Checklist

- [ ] Azure OpenAI endpoint responding (test in Azure portal → Playground)
- [ ] Service account JSON downloaded and saved
- [ ] All 3 Google Sheets created and shared correctly
- [ ] Auth Sheet has email + password in row 2
- [ ] `python scripts/setup.py` ran without errors — all tabs created
- [ ] `uvicorn api.main:app --reload` starts locally → `/health` returns ok
- [ ] `npm run dev` starts locally → login works with Auth Sheet credentials
- [ ] HF Spaces build succeeded → `https://<username>-bodyops-api.hf.space/health` returns ok
- [ ] `vercel --prod` succeeded → login works on production URL
- [ ] CORS updated for production Vercel URL and redeployed (`git subtree push --prefix=api hf main`)

---

## Quick Reference — Useful Commands

| Task | Command |
|------|---------|
| Run backend locally | `uvicorn api.main:app --reload --port 8000` |
| Run frontend locally | `cd frontend && npm run dev` |
| Re-run sheet setup | `python scripts/setup.py` |
| Deploy backend | `git subtree push --prefix=api hf main` |
| Deploy frontend | `cd frontend && vercel --prod` |
| View backend logs | HF Spaces → Logs tab |
| Update a secret | HF Spaces → Settings → Variables and secrets |
| Update Vercel env var | `vercel env add VAR_NAME production` |
| Run tests | `pytest tests/` |
