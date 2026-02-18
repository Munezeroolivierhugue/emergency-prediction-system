# Emergency Severity Prediction System - Backend

## Project Overview
AI-powered emergency incident severity prediction system that helps dispatchers optimize resource allocation and improve response times. Built with Django REST Framework and machine learning.

Dataset: [Kaggle 911 Calls - Montgomery County, PA](https://www.kaggle.com/mchirico/montgomery-county-911-state-pa)

---

## Backend Team

| Role | Developer | Responsibilities | Primary Branch | Task Cards |
|------|-----------|------------------|----------------|-----------|
| Backend Lead | Joseph Manizabayo | Core API, ML integration, prediction endpoint | `feature/model-api-endpoint` | CARD-07, CARD-11 |
| Developer 1 | Henriette Kayitesi | Analytics endpoints, dashboard data, resource optimization | `feature/historical-data-api` | CARD-12 |
| Developer 2 | Gloria Mukundente | Authentication, deployment, data pipeline | `chore/database-setup` | CARD-16 |

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Virtual environment tool (`venv` recommended)
- PostgreSQL (recommended for current backend settings)

### Initial Setup (Detailed)

1. Clone repository:
```bash
git clone https://github.com/Munezeroolivierhugue/emergency-prediction-system/tree/backend 
cd emergency-prediction-system/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows PowerShell
venv\Scripts\activate

# Windows Command Prompt
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` in `backend/`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL defaults in settings.py)
DB_NAME=emergency_severity_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# ML model path
ML_MODEL_PATH=ml_models/severity_model.pkl
```

5. Confirm required backend packages (from project setup requirements):
- `django`
- `djangorestframework`
- `djangorestframework-simplejwt`
- `django-cors-headers`
- `django-filter`
- `python-decouple`
- `psycopg2-binary`
- `scikit-learn`, `xgboost`, `pandas`, `numpy`, `joblib`

6. Database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create superuser (optional but recommended for admin access):
```bash
python manage.py createsuperuser
```

8. Start server:
```bash
python manage.py runserver
```

Server: `http://127.0.0.1:8000/`

### Current Core Configuration (from codebase)
- `rest_framework`, `rest_framework_simplejwt`, `corsheaders`, `django_filters` are configured in `INSTALLED_APPS`.
- JWT authentication is configured in `REST_FRAMEWORK` defaults.
- CORS middleware and CORS settings are configured.
- PostgreSQL is the default database backend.
- Static serving includes WhiteNoise middleware.

---

## Git Workflow (Team Standard)

### Branching Strategy

Main branches:
- `main`: production-ready code (protected)
- `develop`: optional integration branch

Feature/task branches:
- `chore/backend-setup` (CARD-07)
- `feature/model-api-endpoint` (CARD-11)
- `feature/historical-data-api` (CARD-12)
- `chore/database-setup` (CARD-16)
- `feature/auth-deployment`

### First-Time Workflow
```bash
git clone https://github.com/Munezeroolivierhugue/emergency-prediction-system/tree/backend 
cd emergency-prediction-system/backend
git checkout -b feature/your-feature-name
```

Examples:
```bash
# CARD-11
git checkout -b feature/model-api-endpoint

# CARD-12
git checkout -b feature/historical-data-api

# CARD-16
git checkout -b chore/database-setup
```

### Daily Workflow
Before coding:
```bash
git checkout feature/your-feature-name
git fetch origin
git pull origin main
```

After coding:
```bash
git status
git add .
git commit -m "feat: short description (CARD-ID)"
git push origin feature/your-feature-name
```

### Pull Request Workflow
1. Push latest branch changes.
2. Open GitHub/GitLab and create PR.
3. Set base: `main`, compare: `feature/your-feature-name`.
4. Use detailed PR description.
5. Request review.
6. Merge only after approval.

PR template example:
```text
Title: [CARD-11] Add prediction API endpoint

Description:
- Implemented POST prediction endpoint
- Added model loading and inference
- Added validation and error handling

Task Card: CARD-11

Files Changed:
- predictions/views.py
- predictions/serializers.py
- predictions/ml_service.py

Testing:
- [x] Valid payload returns prediction
- [x] Invalid payload rejected
- [x] Missing model handled safely
```

### Git Rules
Do:
- Work only in assigned branch.
- Reference CARD IDs in commits/PRs.
- Commit frequently and clearly.
- Pull from `main` before pushing.
- Test before PR.

Do not:
- Commit directly to `main`.
- Push secrets (`.env`, credentials, keys).
- Push knowingly broken code.
- Merge own PR without review.

### Merge Conflict Handling
```bash
git pull origin main
# resolve conflicts manually
# remove conflict markers

git add .
git commit -m "fix: resolve merge conflicts with main"
git push origin feature/your-feature-name
```

---

## Project Structure

### Current Backend (implemented directories)
```text
backend/
+-- emergency_system/         # Django project settings and root URLs
+-- incidents/                # Incident domain app
+-- predictions/              # Prediction domain app
+-- analytics/                # Analytics domain app
+-- users/                    # Authentication domain app
+-- ml_models/                # ML model files
+-- logs/
+-- media/
+-- static/
+-- manage.py
+-- requirements.txt
+-- README.md
```

### Expected Monorepo Context (cross-team)
```text
emergency-prediction-system/
+-- backend/
+-- frontend/
+-- data/
�   +-- raw/
�   +-- processed/
+-- notebooks/
```

---

## Task Assignments (Detailed)

### CARD-07: Backend Setup
Status: Completed in planning scope
Branch: `chore/backend-setup`
Owner: Backend Lead

Acceptance criteria:
- Django project and app scaffolding created.
- DRF and CORS setup configured.
- Environment configuration pattern established.
- Basic health/system readiness support documented.

---

### CARD-11: Model API Endpoint
Priority: MVP
Branch: `feature/model-api-endpoint`
Owner: Joseph Manizabayo

Files:
- `predictions/views.py`
- `predictions/serializers.py` (to be created if missing)
- `predictions/ml_service.py` (to be created if missing)
- `predictions/urls.py`

Tasks:
1. Create prediction endpoint.
2. Validate required fields (`type`, `hour`, `day`, `lat`, `lng`).
3. Load ML model from configured model path.
4. Run inference and confidence extraction.
5. Return standardized response payload.

Target request:
```json
{
  "type": "Fire",
  "hour": 14,
  "day": "Mon",
  "lat": 40.1,
  "lng": -75.3
}
```

Target response:
```json
{
  "severity": "High",
  "confidence": 0.85
}
```

Acceptance criteria:
- [ ] Endpoint accepts valid POST payloads.
- [ ] Model loads successfully.
- [ ] Severity class returned (`Low`, `Medium`, `High`, `Critical`).
- [ ] Confidence score returned (`0.0` to `1.0`).
- [ ] Graceful error handling for bad input/missing model.

Example commit messages:
- `feat: add prediction endpoint (CARD-11)`
- `feat: integrate ML model loading (CARD-11)`
- `fix: handle missing model file gracefully (CARD-11)`

---

### CARD-12: Historical Data API
Priority: Enhancement
Branch: `feature/historical-data-api`
Owner: Henriette Kayitesi

Files:
- `incidents/models.py`
- `incidents/views.py`
- `incidents/serializers.py` (to be created if missing)
- `analytics/views.py`
- `analytics/urls.py`

Tasks:
1. Confirm/extend incident model fields for API needs.
2. Add migrations if schema changes.
3. Create paginated list endpoint for incidents.
4. Create aggregated statistics endpoint by type and severity.

Target statistics response:
```json
{
  "by_type": {
    "EMS": 150,
    "Fire": 45,
    "Traffic": 200
  },
  "by_severity": {
    "Low": 100,
    "Medium": 150,
    "High": 100,
    "Critical": 45
  }
}
```

Acceptance criteria:
- [ ] Incident API payload structure is documented and consistent.
- [ ] Migrations run successfully.
- [ ] `GET /api/incidents/` is paginated.
- [ ] Aggregated statistics endpoint returns expected format.

Example commit messages:
- `feat: add incident list endpoint (CARD-12)`
- `feat: implement statistics endpoint (CARD-12)`
- `perf: optimize incident analytics queries (CARD-12)`

---

### CARD-16: Database Setup and Data Loading
Priority: Enhancement
Branch: `chore/database-setup`
Owner: Developer 2

Files:
- `incidents/management/commands/load_incidents.py` (to be created)
- Database and import-related settings

Tasks:
1. Create command `python manage.py load_incidents`.
2. Read from `data/processed/incidents_cleaned.csv`.
3. Parse and insert incident records.
4. Handle duplicates and malformed records safely.
5. Ensure command is idempotent.

Acceptance criteria:
- [ ] Command exists and runs.
- [ ] CSV path handling is correct.
- [ ] Records inserted as expected.
- [ ] Progress logging included.
- [ ] Error handling included.
- [ ] Re-run does not duplicate records.

Example commit messages:
- `feat: add load_incidents command (CARD-16)`
- `fix: make data loader idempotent (CARD-16)`
- `chore: add CSV import logging (CARD-16)`

---

## API Endpoints

### Current Routes Wired in Root URL (`emergency_system/urls.py`)
- `api/auth/` -> `users.urls`
- `api/incidents/` -> `incidents.urls`
- `api/predictions/` -> `predictions.urls`
- `api/analytics/` -> `analytics.urls`

### Authentication
- `POST /api/auth/login/` (implemented)
- `POST /api/auth/token/refresh/` (implemented)
- `POST /api/auth/register/` (planned)

### Incidents (planned targets)
- `GET /api/incidents/`
- `POST /api/incidents/`
- `GET /api/incidents/{id}/`
- `PUT /api/incidents/{id}/`
- `DELETE /api/incidents/{id}/`

### Predictions (planned target)
- `POST /api/predictions/predict/`

### Analytics (planned targets)
- `GET /api/analytics/statistics/`
- `GET /api/analytics/severity-distribution/`
- `GET /api/analytics/time-series/`
- `GET /api/analytics/location-heatmap/`
- `GET /api/analytics/recommendations/{severity}/`

---

## Testing Guide

### Basic Django Checks
```bash
python manage.py check
python manage.py test
```

### JWT Authentication Check (currently available)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your-user","password":"your-password"}'
```

### Planned Endpoint Test Examples
```bash
# Prediction (CARD-11 target)
curl -X POST http://127.0.0.1:8000/api/predictions/predict/ \
  -H "Content-Type: application/json" \
  -d '{"type":"Fire","hour":14,"day":"Mon","lat":40.1,"lng":-75.3}'

# Incidents list (CARD-12 target)
curl http://127.0.0.1:8000/api/incidents/

# Analytics statistics (CARD-12 target)
curl http://127.0.0.1:8000/api/analytics/statistics/
```

Optional quality tools:
```bash
flake8 .
black .
```

---

## Common Issues and Solutions

### Import or module errors
Activate virtual environment before running commands:
```bash
venv\Scripts\activate
```

### Database connection errors
Verify `.env` database values (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) and that PostgreSQL is running.

### Migration failures
```bash
python manage.py makemigrations
python manage.py migrate
```

### Model file not found
Verify model exists and path matches `.env`:
```bash
ML_MODEL_PATH=ml_models/severity_model.pkl
```

### Port already in use
```bash
python manage.py runserver 8080
```

### CSV loading issues
Check dataset path relative to backend command context:
```bash
../data/processed/incidents_cleaned.csv
```

### Git conflicts
Resolve conflict markers, then commit and push again.

---

## Communication and Collaboration

### Daily Standup Format
1. What I completed yesterday
2. What I am working on today
3. Blockers requiring team help

### Code Review Checklist
- [ ] Aligns with Django and DRF best practices
- [ ] Meets task card acceptance criteria
- [ ] Endpoints tested manually
- [ ] No secrets committed
- [ ] Commit and PR messages reference CARD IDs
- [ ] Documentation updated where needed

---

## Sprint Timeline (1 Week)

| Day | Focus | Task Cards |
|-----|-------|-----------|
| Day 1 | Setup and planning | CARD-07 |
| Day 2-3 | Core development | CARD-11, CARD-12 |
| Day 4 | Data loading and validation | CARD-16 |
| Day 5 | PR reviews and integration | All active cards |
| Day 6 | Bug fixes and polish | Testing and fixes |
| Day 7 | Final integration and demo prep | Integration cards |

---

## Helpful Commands Reference

### Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
venv\Scripts\activate.bat
deactivate
```

### Django
```bash
python manage.py runserver
python manage.py runserver 8080
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
python manage.py check
python manage.py test
```

### Git
```bash
git status
git add .
git commit -m "feat: short description (CARD-ID)"
git push origin branch-name
git pull origin main
git checkout -b feature/name
git branch
```

### Dependencies
```bash
pip install package-name
pip freeze > requirements.txt
pip list
```

---

## Task Card Checklist

### Sprint 1: Foundation
- [x] CARD-07: Backend setup (Django, DRF, CORS baseline)

### Sprint 2: Core Features
- [ ] CARD-11: Model API endpoint
- [ ] CARD-12: Historical data API
- [ ] CARD-16: Database setup and data loading

### Sprint 3: Integration
- [ ] Frontend-backend integration
- [ ] Testing and bug fixes
- [ ] Deployment

---

## Notes
- Keep `.env` private and never commit it.
- Test before pushing.
- Use clear commit messages with task card references.
- Update this README as tasks evolve.
