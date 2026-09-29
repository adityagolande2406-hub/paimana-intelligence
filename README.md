# PAIMANA Intelligence 📊

An infrastructure project risk & schedule monitoring intelligence system built for high-transparency project oversight, deterministic risk indicators, and historical trend analytics.

---

## 🚀 Quick Start (Local)

### 1. Prerequisites
- Python 3.10+ installed

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
Open your browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## ☁️ 1-Click Hosting on Render

PAIMANA Intelligence is fully configured for deployment on **Render** (Free Tier):

1. Push this repository to **GitHub**.
2. Go to [render.com](https://render.com) and sign in.
3. Click **New +** > **Web Service**.
4. Connect your GitHub repository.
5. Render will automatically detect the settings from `render.yaml` or use:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy Web Service** — your app will be live with a free HTTPS URL in minutes!

---

## 🛠️ Project Architecture

- **Backend:** FastAPI (Python), Pandas, Uvicorn
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (natively served via `/static` and `/`)
- **Data Engine:** Deterministic rule-based expert system with historical snapshot storage in `/data`
- **Docker Ready:** Includes `Dockerfile` and `Procfile` for containerized hosting

---

## 📡 Key API Endpoints

- `GET /` — Interactive Web Dashboard
- `GET /health` — Service health check
- `GET /summary` — Aggregate portfolio statistics
- `GET /projects` — Filtered & paginated project records
- `GET /projects/{project_code}/risk` — Multi-dimensional rule-based risk evaluation
- `GET /projects/{project_code}/remediation` — Actionable mitigation strategies
- `GET /analytics` — High-level analytics distributions
- `GET /history/{project_code}` — Chronological snapshot tracking
