# Emergency Severity Prediction System

A full-stack application that predicts the severity of 911 emergency calls using machine learning (XGBoost/LightGBM). Built with a Django REST API backend and a React + Vite frontend.

---

## Prerequisites

Make sure you have the following installed before starting:

- **Python 3.10+** → [python.org](https://python.org)
- **Node.js 18+** → [nodejs.org](https://nodejs.org)
- **Git** → [git-scm.com](https://git-scm.com)
- **macOS only:** `brew install libomp` (required for XGBoost)

---

## 1. Clone the Repository

```bash
git clone https://github.com/Munezeroolivierhugue/emergency-prediction-system.git
cd emergency-prediction-system
git checkout dev
```

---

## 2. Backend Setup (Django)

### Navigate to the backend folder

```bash
cd backend
```

### Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run database migrations

```bash
python manage.py migrate
```

### Create a superuser (optional, for admin panel)

```bash
python manage.py createsuperuser
```

### Start the backend server

```bash
python manage.py runserver
```

The backend will be running at **http://localhost:8000**

> **Note:** The ML model file (`backend/ml_models/best_advanced_model.pkl`) is included in the repo. The backend will load it automatically on startup.

---

## 3. Frontend Setup (React + Vite)

Open a **new terminal** (keep the backend running), then:

### Navigate to the frontend folder

```bash
cd frontend/emergency-prediction-frontend
```

### Install dependencies

```bash
npm install
```

### Start the frontend dev server

```bash
npm run dev
```

The frontend will be running at **http://localhost:5173**

---

## 4. Testing the App

With both servers running, open your browser and go to:

```
http://localhost:5173
```

You can test:
- **Dashboard** — live analytics and charts
- **Predictions** — submit an emergency incident and get a severity score from the ML model
- **Incidents** — browse historical emergency calls
- **Admin panel** — http://localhost:8000/admin (requires superuser)
- **API docs** — http://localhost:8000/api/schema/swagger-ui/

---

## Project Structure

```
emergency-prediction-system/
├── backend/                  # Django REST API
│   ├── ml_models/            # Trained ML model (.pkl files)
│   ├── predictions/          # Prediction endpoints & ML service
│   ├── incidents/            # Incident data endpoints
│   ├── analytics/            # Analytics endpoints
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   └── emergency-prediction-frontend/   # React + Vite app
│       └── src/
│           ├── pages/        # Dashboard, Predictions, Incidents
│           └── utils/        # API service layer
│
├── notebook/
│   └── train_model.py        # ML model training script
│
└── data/                     # Training data (sample included)
```

---

## Retraining the Model (Optional)

If you want to retrain the ML model from scratch:

```bash
cd notebook
python train_model.py
```

This will train an XGBoost/LightGBM model using K-Fold cross-validation and save the best model directly to `backend/ml_models/best_advanced_model.pkl`.

> Requires `data/911.csv` or `data/sample_911.csv` to be present.

---

## Common Issues

| Problem | Fix |
|---|---|
| `libomp.dylib` not found (macOS) | Run `brew install libomp` then restart the server |
| `ModuleNotFoundError` on runserver | Make sure your venv is **activated** before running |
| Frontend can't reach backend | Confirm backend is running on port 8000 |
| `No module named 'drf_spectacular'` | Re-run `pip install -r requirements.txt` inside the venv |