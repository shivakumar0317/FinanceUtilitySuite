# Finance Utility Suite Web v1.6.0

Included: React + Vite, Material UI dark dashboard, register/login, JWT protected routes, dashboard, portfolios, holdings.

## Setup

Copy this folder to `D:\FinanceUtilitySuite\web`.

Run FastAPI in one PowerShell window:

```powershell
cd D:\FinanceUtilitySuite
python -m uvicorn backend.main:app --reload
```

Run the web app in a second PowerShell window:

```powershell
cd D:\FinanceUtilitySuite\web
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

FastAPI `.env` must include:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Restart FastAPI after changing CORS.

Development note: JWT is stored in localStorage. For production, move to secure HttpOnly cookies and add refresh-token rotation and CSRF protection.
