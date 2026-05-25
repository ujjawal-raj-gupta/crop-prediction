## Bihar Agriculture Platform (Government-grade)

This folder contains the **new rebuilt platform**:

- **Frontend**: React 18 + Vite + Tailwind + React Router + React Query + Recharts/ApexCharts
- **Backend**: FastAPI (`/api/v1/...`) with clean route modules and schemas

### Run (dev)

### Prerequisites (Windows)

- Python 3.10+ installed
- **Node.js LTS installed** (must include `npm`)

#### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.main:app --reload --host 127.0.0.1 --port 8001
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend expects backend at `http://127.0.0.1:8001`.

### One-command dev launcher (recommended)

From `bihar-agriculture-platform/`:

```powershell
.\run-dev.ps1
```


