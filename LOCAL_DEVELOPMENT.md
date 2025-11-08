# Local Development Setup Guide

This guide provides detailed instructions for setting up the LabLink system for local development.

## Quick Start with Docker (Recommended)

**The easiest way to run LabLink locally is using Docker**, which includes PostgreSQL and doesn't require installing it on your machine.

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for Docker setup instructions.

---

## Manual Setup (Without Docker)

If you prefer not to use Docker, follow the instructions below to set up everything manually.

## Prerequisites

### Required Software

- **Python 3.11 or higher**
- **PostgreSQL 14 or higher**
- **pip** (Python package manager)
- **Git**
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Optional Tools

- **pgAdmin** - GUI for PostgreSQL management
- **Postman** or **curl** - For API testing
- **VS Code** or **PyCharm** - Recommended IDEs

## Installation Instructions

### 1. Install Python

#### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS

Using Homebrew (recommended):
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify installation
python3 --version
pip3 --version
```

Or download from [python.org](https://www.python.org/downloads/)

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and related tools
sudo apt install python3.11 python3.11-venv python3-pip python3.11-dev

# Verify installation
python3.11 --version
pip3 --version
```

#### Linux (Fedora/RHEL)

```bash
# Install Python
sudo dnf install python3.11 python3-pip python3-devel

# Verify installation
python3.11 --version
pip3 --version
```

### 2. Install PostgreSQL

#### Windows

1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer
3. During installation:
   - Remember the password you set for the `postgres` user
   - Default port is 5432 (keep default)
   - Install pgAdmin 4 (optional but recommended)
4. Verify installation:
   ```cmd
   psql --version
   ```

#### macOS

Using Homebrew:
```bash
# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Verify installation
psql --version
```

Or download Postgres.app from [postgresapp.com](https://postgresapp.com/)

#### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

#### Linux (Fedora/RHEL)

```bash
# Install PostgreSQL
sudo dnf install postgresql-server postgresql-contrib postgresql-devel

# Initialize database
sudo postgresql-setup --initdb

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

### 3. Configure PostgreSQL

#### Create Database and User

**Windows:**
```cmd
# Open Command Prompt as Administrator
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE lablink;
CREATE USER lablink_user WITH PASSWORD 'lablink_password';
GRANT ALL PRIVILEGES ON DATABASE lablink TO lablink_user;
\q
```

**macOS/Linux:**
```bash
# Switch to postgres user (Linux)
sudo -u postgres psql

# Or connect directly (macOS)
psql postgres

# In PostgreSQL prompt:
CREATE DATABASE lablink;
CREATE USER lablink_user WITH PASSWORD 'lablink_password';
GRANT ALL PRIVILEGES ON DATABASE lablink TO lablink_user;
\q
```

#### Configure Authentication (Linux only)

Edit `pg_hba.conf` to allow password authentication:

```bash
# Find pg_hba.conf location
sudo -u postgres psql -c "SHOW hba_file;"

# Edit the file
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Change this line:
# local   all             all                                     peer
# To:
# local   all             all                                     md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Test Database Connection

```bash
# Test connection
psql -U lablink_user -d lablink -h localhost

# If successful, you'll see:
# lablink=>

# Exit with:
\q
```

## Project Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd lablink

# Or if you already have the code
cd path/to/lablink
```

### 2. Create Virtual Environment

A virtual environment isolates project dependencies from system Python packages.

**Windows:**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

**Deactivating:**
```bash
# When you're done working
deactivate
```

### 3. Install Python Dependencies

With the virtual environment activated:

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages:**
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Flask-Migrate
- psycopg2-binary
- bcrypt
- gunicorn
- pytest (for testing)

### 4. Configure Environment Variables

#### Option 1: Using .env file (Recommended)

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your settings
# Windows: notepad .env
# macOS/Linux: nano .env
```

Edit `.env`:
```bash
DATABASE_URL=postgresql://lablink_user:lablink_password@localhost:5432/lablink
JWT_SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True
CORS_ORIGINS=*
JWT_ACCESS_TOKEN_EXPIRES=1
```

#### Option 2: Export Environment Variables

**Windows (Command Prompt):**
```cmd
set DATABASE_URL=postgresql://lablink_user:lablink_password@localhost:5432/lablink
set JWT_SECRET_KEY=your-secret-key-here
set FLASK_ENV=development
```

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="postgresql://lablink_user:lablink_password@localhost:5432/lablink"
$env:JWT_SECRET_KEY="your-secret-key-here"
$env:FLASK_ENV="development"
```

**macOS/Linux:**
```bash
export DATABASE_URL="postgresql://lablink_user:lablink_password@localhost:5432/lablink"
export JWT_SECRET_KEY="your-secret-key-here"
export FLASK_ENV="development"

# Add to ~/.bashrc or ~/.zshrc to persist
echo 'export DATABASE_URL="postgresql://lablink_user:lablink_password@localhost:5432/lablink"' >> ~/.bashrc
```

### 5. Initialize Database

```bash
# Navigate to backend directory
cd backend

# Initialize database schema
python init_db.py init

# Expected output:
# Database initialized successfully!
# Tables created: users, components, requests, transactions
```

### 6. Load Sample Data

```bash
# Load seed data
python seed_data.py

# Expected output:
# Seed data loaded successfully!
# Created 2 users (faculty, student)
# Created 15 components
# Created 5 sample requests
```

**Default Users Created:**
- **Faculty**: username=`faculty`, password=`faculty123`
- **Student**: username=`student`, password=`student123`

### 7. Run the Application

```bash
# From backend directory
python app.py

# Expected output:
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

The API is now running at `http://localhost:5000`

### 8. Access the Frontend

#### Option 1: Direct File Access
```bash
# Simply open in browser
# Windows:
start ../frontend/login.html

# macOS:
open ../frontend/login.html

# Linux:
xdg-open ../frontend/login.html
```

#### Option 2: Local HTTP Server

```bash
# Open new terminal
cd frontend

# Python HTTP server
python -m http.server 8000

# Access at: http://localhost:8000/login.html
```

#### Option 3: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `frontend/login.html`
3. Select "Open with Live Server"

## Development Workflow

### Daily Development

```bash
# 1. Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. Start PostgreSQL (if not running)
# macOS:
brew services start postgresql@14
# Linux:
sudo systemctl start postgresql

# 3. Navigate to backend
cd backend

# 4. Run the application
python app.py

# 5. In another terminal, open frontend
cd frontend
python -m http.server 8000
```

### Database Management

#### View Database Contents

```bash
# Connect to database
psql -U lablink_user -d lablink -h localhost

# List tables
\dt

# View users
SELECT * FROM users;

# View components
SELECT * FROM components;

# View requests
SELECT * FROM requests;

# View transactions
SELECT * FROM transactions;

# Exit
\q
```

#### Reset Database

```bash
cd backend

# Clear all data (keeps tables)
python seed_data.py clear

# Drop all tables
python init_db.py drop

# Recreate everything
python init_db.py init
python seed_data.py
```

#### Database Migrations

```bash
cd backend

# Setup migrations (first time only)
python init_db.py setup-migrations

# Create a migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest test_auth.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### API Testing

#### Using curl

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'

# Get components (with token)
curl http://localhost:5000/api/components \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Using Postman

1. Import the API collection (if available)
2. Set base URL: `http://localhost:5000`
3. Login to get JWT token
4. Add token to Authorization header for protected routes

### Code Changes

#### Backend Changes

1. Edit Python files in `backend/`
2. Flask auto-reloads in debug mode
3. Check terminal for errors
4. Test changes via API or frontend

#### Frontend Changes

1. Edit HTML/JS files in `frontend/`
2. Refresh browser to see changes
3. Check browser console for errors
4. Use browser DevTools for debugging

#### Database Model Changes

1. Edit `backend/models.py`
2. Create migration:
   ```bash
   flask db migrate -m "Description"
   ```
3. Review migration file in `migrations/versions/`
4. Apply migration:
   ```bash
   flask db upgrade
   ```

## Troubleshooting

### Python Issues

**"python: command not found"**
```bash
# Try python3 instead
python3 --version

# Or add alias
alias python=python3
```

**"pip: command not found"**
```bash
# Use python -m pip
python -m pip install -r requirements.txt
```

**Import errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check you're in correct directory
pwd  # Should be in lablink root
```

### PostgreSQL Issues

**"psql: command not found"**
```bash
# Add PostgreSQL to PATH
# macOS:
export PATH="/usr/local/opt/postgresql@14/bin:$PATH"

# Linux: Usually already in PATH
# Windows: Add C:\Program Files\PostgreSQL\14\bin to PATH
```

**"Connection refused"**
```bash
# Check PostgreSQL is running
# macOS:
brew services list
brew services start postgresql@14

# Linux:
sudo systemctl status postgresql
sudo systemctl start postgresql

# Windows: Check Services app
```

**"Authentication failed"**
```bash
# Check password is correct
psql -U lablink_user -d lablink -h localhost

# Reset password if needed
sudo -u postgres psql
ALTER USER lablink_user WITH PASSWORD 'new_password';
```

**"Database does not exist"**
```bash
# Create database
psql -U postgres
CREATE DATABASE lablink;
GRANT ALL PRIVILEGES ON DATABASE lablink TO lablink_user;
```

### Application Issues

**"Port 5000 already in use"**
```bash
# Find process using port
# macOS/Linux:
lsof -i :5000
kill -9 <PID>

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py
app.run(port=5001)
```

**"Database connection error"**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Should be:
# postgresql://username:password@host:port/database

# Test connection
psql $DATABASE_URL
```

**"JWT decode error"**
```bash
# Check JWT_SECRET_KEY is set
echo $JWT_SECRET_KEY

# Clear browser localStorage
# Open browser console:
localStorage.clear()
```

**"CORS errors in browser"**
```bash
# Check CORS_ORIGINS in config
# For development, use:
CORS_ORIGINS=*

# Or specific origin:
CORS_ORIGINS=http://localhost:8000
```

### Frontend Issues

**"Failed to fetch"**
- Check backend is running on port 5000
- Check API_BASE_URL in `frontend/api.js`
- Check browser console for CORS errors
- Verify JWT token in localStorage

**"Unauthorized" errors**
- Login again to get fresh token
- Check token expiration
- Clear localStorage and login again

**"Components not loading"**
- Check backend logs for errors
- Verify database has data: `SELECT * FROM components;`
- Check browser Network tab for API responses

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- PostgreSQL
- Live Server
- ESLint
- Prettier

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### PyCharm

1. Open project folder
2. Configure Python interpreter:
   - File → Settings → Project → Python Interpreter
   - Add → Existing environment
   - Select `venv/bin/python`
3. Configure database:
   - View → Tool Windows → Database
   - Add PostgreSQL data source
   - Enter connection details

## Next Steps

After successful setup:

1. **Explore the application**
   - Login as student and faculty
   - Test all features
   - Review transaction logs

2. **Read the documentation**
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [backend/DATABASE.md](backend/DATABASE.md) - Database schema
   - [.kiro/specs/lablink-system/design.md](.kiro/specs/lablink-system/design.md) - System design

3. **Start developing**
   - Review existing code
   - Run tests
   - Make changes
   - Test thoroughly

4. **Deploy**
   - [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Docker deployment
   - [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md) - AWS deployment

## Getting Help

- Check existing documentation
- Review error messages carefully
- Search for similar issues online
- Check PostgreSQL and Flask documentation
- Create an issue with detailed information

## Best Practices

- Always activate virtual environment before working
- Keep dependencies updated: `pip install --upgrade -r requirements.txt`
- Run tests before committing: `pytest`
- Use meaningful commit messages
- Never commit `.env` file or secrets
- Keep database backed up during development
- Use migrations for schema changes
- Test in browser after backend changes
- Check browser console for frontend errors
- Use proper error handling in code
