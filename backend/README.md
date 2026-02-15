# Emergency Severity Prediction System - Backend

## 🎯 Project Overview
AI-powered emergency incident severity prediction system that helps dispatchers optimize resource allocation and improve response times. Built with Django REST Framework and Machine Learning.

---

## 👥 Backend Team

| Role | Developer | Responsibilities |
|------|-----------|------------------|
| **Backend Lead** | Joseph Manizabayo | Core API, ML Integration, Prediction Endpoint |
| **Developer 1** | Henriette Kayitesi | Analytics Endpoints, Dashboard Data, Resource Optimization |
| **Developer 2** | [Name] | Authentication, Deployment, Data Pipeline |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- Virtual environment tool

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Munezeroolivierhugue/emergency-prediction-system/tree/backend

   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Windows PowerShell)
   venv\Scripts\activate
   
   # Activate (Windows Command Prompt)
   venv\Scripts\activate.bat
   
   # Activate (macOS/Linux)
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Create a `.env` file in the root directory
   - Copy the content from `.env.example` or use these settings:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (Postgres or SQLite for development)
   # DB_NAME=emergency_severity_db
   # DB_USER=postgres
   # DB_PASSWORD=Joseph123
   # DB_HOST=localhost
   # DB_PORT=5432
   
   # CORS Settings
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```
   
   Server will start at: `http://127.0.0.1:8000/`

---

## 🔄 Git Workflow (IMPORTANT - READ CAREFULLY)

### Branching Strategy

**Main Branches:**
- `main` - Production-ready code (protected)
- `develop` - Integration branch for features

**Feature Branches:**
- `feature/prediction-api` - Joseph's work
- `feature/analytics` - Henriette's work
- `feature/auth-deployment` - Developer 2's work

### Step-by-Step Workflow

#### 1. First Time Setup
```bash
# Clone the repository
git clone https://github.com/Munezeroolivierhugue/emergency-prediction-system/tree/backend

cd backend

# Create your feature branch
git checkout -b feature/your-feature-name

# Example:
# Joseph: git checkout -b feature/prediction-api
# Henriette: git checkout -b feature/analytics
# Developer 2: git checkout -b feature/auth-deployment
```

#### 2. Daily Workflow

**Before starting work each day:**
```bash
# Make sure you're on your branch
git checkout feature/your-feature-name

# Pull latest changes from main
git fetch origin
git pull origin main

# If there are conflicts, resolve them before continuing
```

**While working:**
```bash
# Check what files you've changed
git status

# Add your changes
git add .

# Commit with a clear message
git commit -m "Add prediction endpoint with ML model integration"

# Push to your branch
git push origin feature/your-feature-name
```

#### 3. Creating a Pull Request (PR)

When your feature is ready:

1. **Push your latest changes**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Go to GitHub/GitLab repository**

3. **Click "New Pull Request"**

4. **Set the following:**
   - Base branch: `main`
   - Compare branch: `feature/your-feature-name`

5. **Write a clear PR description:**
   ```
   Title: Add prediction API endpoint
   
   Description:
   - Implemented POST /api/predictions/predict endpoint
   - Integrated ML model loading and inference
   - Added input validation and error handling
   - Tested with sample data
   
   Files Changed:
   - predictions/views.py
   - predictions/serializers.py
   - predictions/ml_service.py
   ```

6. **Request review from team lead (Joseph)**

7. **Wait for approval and merge**

#### 4. Important Git Rules

✅ **DO:**
- Work only in your assigned feature branch
- Commit frequently with clear messages
- Pull from main before pushing your changes
- Test your code before creating a PR
- Write descriptive commit messages

❌ **DON'T:**
- Never commit directly to `main`
- Don't work on other people's feature branches
- Don't push broken code
- Don't commit sensitive data (API keys, passwords)
- Don't merge your own PRs without review

#### 5. Handling Merge Conflicts

If you get conflicts when pulling from main:

```bash
# Pull latest changes
git pull origin main

# Git will tell you which files have conflicts
# Open those files and look for:
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> main

# Manually resolve by choosing which code to keep
# Remove the conflict markers (<<<<<<, =======, >>>>>>>)

# After resolving, add and commit
git add .
git commit -m "Resolve merge conflicts with main"
git push origin feature/your-feature-name
```

---

## 📁 Project Structure

```
backend/
├── emergency_system/       # Main project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py
├── incidents/             # Incidents app (Joseph)
│   ├── models.py         # Incident, Location models
│   ├── views.py          # Incident CRUD views
│   ├── serializers.py    # DRF serializers
│   └── urls.py           # Incident endpoints
├── predictions/          # Predictions app (Joseph)
│   ├── models.py         # Prediction model
│   ├── views.py          # Prediction endpoint
│   ├── serializers.py    # Prediction serializers
│   ├── ml_service.py     # ML model integration
│   └── urls.py           # Prediction endpoints
├── analytics/            # Analytics app (Henriette)
│   ├── views.py          # Analytics endpoints
│   ├── utils.py          # Aggregation logic
│   └── urls.py           # Analytics endpoints
├── users/                # Authentication app (Developer 2)
│   ├── views.py          # Auth endpoints
│   ├── serializers.py    # User serializers
│   └── urls.py           # Auth endpoints
├── ml_models/            # ML model files
│   └── severity_model.pkl
├── media/                # User uploads
├── static/               # Static files
├── logs/                 # Application logs
├── .env                  # Environment variables (not in git)
├── .gitignore
├── requirements.txt      # Python dependencies
├── README.md
└── manage.py
```

---

## 🔧 Tasks

### Joseph Manizabayo (Backend Lead) - `feature/prediction-api`

**Files to work on:**
- `predictions/views.py`
- `predictions/serializers.py`
- `predictions/ml_service.py`
- `incidents/views.py`
- `incidents/serializers.py`
- `incidents/models.py`

**Tasks:**
1. Create prediction endpoint (`POST /api/predictions/predict`)
2. Integrate ML model (load .pkl file from ML team)
3. Implement incident CRUD endpoints
4. Create serializers for Incident and Prediction models
5. Add input validation

**Example commit messages:**
- `feat: add prediction endpoint`
- `feat: integrate ML model loading`
- `fix: handle missing model file gracefully`

---

### Henriette Kayitesi (Developer 1) - `feature/analytics`

**Files to work on:**
- `analytics/views.py`
- `analytics/utils.py`
- `analytics/urls.py`

**Tasks:**
1. Severity distribution endpoint (`GET /api/analytics/severity-distribution`)
2. Time-series analysis endpoint (`GET /api/analytics/time-series`)
3. Location heatmap data (`GET /api/analytics/location-heatmap`)
4. Resource recommendations (`GET /api/analytics/recommendations/{severity}`)
5. Add filtering (date range, severity, location)

**Example commit messages:**
- `feat: add severity distribution analytics`
- `feat: implement time-series endpoint`
- `perf: optimize analytics queries with indexes`

---

### Developer 2 - `feature/auth-deployment`

**Files to work on:**
- `users/views.py`
- `users/serializers.py`
- `users/urls.py`
- Deployment configuration files

**Tasks:**
1. JWT authentication setup (already configured, test it)
2. User registration endpoint (`POST /api/auth/register`)
3. Bulk data upload endpoint (`POST /api/incidents/bulk-upload`)
4. Model update endpoint (`POST /api/model/update`)
5. Prepare deployment configuration

**Example commit messages:**
- `feat: add user registration endpoint`
- `feat: implement bulk CSV upload`
- `chore: configure deployment settings`

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login/` - Get JWT token
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/register/` - Register new user

### Incidents
- `GET /api/incidents/` - List all incidents
- `POST /api/incidents/` - Create new incident
- `GET /api/incidents/{id}/` - Get incident details
- `PUT /api/incidents/{id}/` - Update incident
- `DELETE /api/incidents/{id}/` - Delete incident

### Predictions
- `POST /api/predictions/predict/` - Predict severity

### Analytics
- `GET /api/analytics/severity-distribution/` - Severity breakdown
- `GET /api/analytics/time-series/` - Historical trends
- `GET /api/analytics/location-heatmap/` - Location data
- `GET /api/analytics/recommendations/{severity}/` - Resource suggestions

---

## 🧪 Testing Your Code

Before creating a PR, test your endpoints:

```bash
# Run Django checks
python manage.py check

# Run tests (when we add them)
python manage.py test

# Test with curl
curl -X GET http://127.0.0.1:8000/api/incidents/

# Or use Postman/Thunder Client
```

---

## 🐛 Common Issues & Solutions

### Issue: Import errors
**Solution:** Make sure virtual environment is activated
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### Issue: Migration errors
**Solution:** Delete migrations and recreate
```bash
# Don't delete migrations in production!
# This is only for development
python manage.py makemigrations
python manage.py migrate
```

### Issue: Port already in use
**Solution:** Run on different port
```bash
python manage.py runserver 8080
```

### Issue: Git conflicts
**Solution:** See "Handling Merge Conflicts" section above

---

## 📞 Communication

- **Daily Standup:** Share what you worked on, what you're working on, and any blockers
- **Questions:** Ask in team chat or create a GitHub issue
- **Stuck?** Don't waste more than 30 minutes - ask for help!

---

## ⏰ Timeline (1 Week Sprint)

| Day | All Team Members |
|-----|------------------|
| Day 1 | Setup environment, create feature branch |
| Day 2-3 | Core development on assigned features |
| Day 4 | Continue development, start testing |
| Day 5 | Create PRs, code review, fixes |
| Day 6 | Integration testing, bug fixes |
| Day 7 | Final testing, demo preparation |

---

## 🎓 Helpful Commands Reference

```bash
# Virtual Environment
python -m venv venv                    # Create venv
venv\Scripts\activate                  # Activate (Windows)
deactivate                             # Deactivate

# Django
python manage.py runserver             # Start server
python manage.py makemigrations        # Create migrations
python manage.py migrate               # Apply migrations
python manage.py createsuperuser       # Create admin user
python manage.py shell                 # Django shell
python manage.py check                 # Check for issues

# Git
git status                             # Check status
git add .                              # Stage all changes
git commit -m "message"                # Commit
git push origin branch-name            # Push to remote
git pull origin main                   # Pull latest from main
git checkout -b feature/name           # Create new branch
git branch                             # List branches

# Dependencies
pip install package-name               # Install package
pip freeze > requirements.txt          # Update requirements
pip list                               # List installed packages
```

---

## 🚀 Ready to Code!

1. ✅ Set up your environment
2. ✅ Create your feature branch
3. ✅ Start working on your assigned tasks
4. ✅ Commit and push regularly
5. ✅ Create PR when ready
6. ✅ Help teammates when they need it

**Remember:** Communication is key! Ask questions, share progress, and help each other succeed! 💪

---

## 📝 Notes
- Keep `.env` file secret (never commit it)
- Test before pushing
- Write clear commit messages
- Comment complex code
