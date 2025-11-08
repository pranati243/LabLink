# LabLink System - Run Commands

## Quick Start Commands

### Option 1: Using Docker (Recommended)
This runs both PostgreSQL database and the backend in containers:

```bash
# Start all services (database + backend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Access the application:**
- Backend API: http://localhost:5000
- Frontend: Open `frontend/login.html` in your browser
- Health Check: http://localhost:5000/health

---

### Option 2: Run Backend Locally (with Docker PostgreSQL)

**Prerequisites:**
- PostgreSQL running in Docker: `docker-compose up -d db`
- Python virtual environment activated

**Step 1: Set environment variables**
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://lablink_user:lablink_password@localhost:5432/lablink"
$env:JWT_SECRET_KEY="dev-jwt-secret-for-testing"
$env:FLASK_ENV="development"

# Linux/Mac
export DATABASE_URL="postgresql://lablink_user:lablink_password@localhost:5432/lablink"
export JWT_SECRET_KEY="dev-jwt-secret-for-testing"
export FLASK_ENV="development"
```

**Step 2: Run the backend**
```bash
# Using the startup script
python run.py

# OR using Flask directly
python backend/app.py
```

**Backend will be available at:** http://localhost:5000

---

### Option 3: Run Backend with SQLite (No Docker)

**Step 1: Set environment variables**
```bash
# Windows PowerShell
$env:DATABASE_URL="sqlite:///lablink.db"
$env:JWT_SECRET_KEY="dev-jwt-secret-for-testing"
$env:FLASK_ENV="development"

# Linux/Mac
export DATABASE_URL="sqlite:///lablink.db"
export JWT_SECRET_KEY="dev-jwt-secret-for-testing"
export FLASK_ENV="development"
```

**Step 2: Initialize database**
```bash
python backend/init_db.py init
python backend/seed_data.py
```

**Step 3: Run the backend**
```bash
python run.py
```

---

## Frontend Setup

The frontend is a static HTML/JavaScript application. You have several options:

### Option 1: Open directly in browser
```bash
# Simply open the file in your browser
start frontend/login.html  # Windows
open frontend/login.html   # Mac
xdg-open frontend/login.html  # Linux
```

### Option 2: Use Python HTTP server
```bash
# From the project root
python -m http.server 8000

# Then open: http://localhost:8000/frontend/login.html
```

### Option 3: Use Live Server (VS Code extension)
- Install "Live Server" extension in VS Code
- Right-click on `frontend/login.html`
- Select "Open with Live Server"

---

## Default Credentials

After seeding the database, use these credentials:

**Faculty Account:**
- Username: `faculty`
- Password: `faculty123`

**Student Account:**
- Username: `student`
- Password: `student123`

---

## API Endpoints

Once the backend is running, you can test the API:

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

**Get Components (requires authentication):**
```bash
curl http://localhost:5000/api/components \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Troubleshooting

### Backend won't start
1. Check if PostgreSQL is running: `docker ps`
2. Verify DATABASE_URL is correct
3. Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
1. Verify backend is running: `curl http://localhost:5000/health`
2. Check CORS settings in backend config
3. Open browser console (F12) to see error messages

### Database connection errors
1. Ensure PostgreSQL container is running: `docker-compose up -d db`
2. Wait for database to be healthy: `docker-compose ps`
3. Check credentials match docker-compose.yml

---

## Development Workflow

**Terminal 1 - Backend:**
```bash
# Start PostgreSQL
docker-compose up -d db

# Run backend
python run.py
```

**Terminal 2 - Frontend:**
```bash
# Serve frontend
python -m http.server 8000
```

**Browser:**
- Open http://localhost:8000/frontend/login.html
- Backend API at http://localhost:5000

---

## Production Deployment

For production deployment, see:
- `DEPLOYMENT_AWS.md` - AWS deployment guide
- `AWS_QUICKSTART.md` - Quick AWS setup
- `docker-compose.yml` - Container orchestration

**Quick production start:**
```bash
# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY="your-secure-secret-key"
export JWT_SECRET_KEY="your-secure-jwt-key"

# Start with docker-compose
docker-compose up -d
```
