# LabLink Quick Reference

## 🚀 Getting Started in 3 Steps

### Using Docker (No PostgreSQL Install Needed)

```bash
# Step 1: Copy environment file
cp .env.docker .env

# Step 2: Start everything
docker-compose up -d

# Step 3: Open frontend/login.html in browser
# Login: faculty/faculty123 or student/student123
```

That's it! PostgreSQL and the backend are running in containers.

---

## 📋 Common Commands

### Docker Commands

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Stop and remove all data
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# Access database
docker-compose exec db psql -U lablink_user -d lablink

# Access backend shell
docker-compose exec backend /bin/bash
```

### Local Development Commands

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run backend
cd backend
python app.py

# Initialize database
python init_db.py init

# Load sample data
python seed_data.py

# Run tests
pytest
```

---

## 🔑 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Faculty | `faculty` | `faculty123` |
| Student | `student` | `student123` |

---

## 🌐 Access Points

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | `frontend/login.html` | Open directly in browser |
| Backend API | `http://localhost:5000` | REST API |
| Database | `localhost:5432` | PostgreSQL |
| Health Check | `http://localhost:5000/health` | API status |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Docker services configuration |
| `.env.docker` | Environment variables template |
| `backend/schema.sql` | Database schema |
| `backend/seed_data.sql` | Sample data |
| `backend/app.py` | Main Flask application |
| `frontend/login.html` | Login page |

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
POSTGRES_DB=lablink
POSTGRES_USER=lablink_user
POSTGRES_PASSWORD=lablink_password
POSTGRES_PORT=5432

# Backend
BACKEND_PORT=5000
FLASK_ENV=development

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production

# CORS
CORS_ORIGINS=*
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Change ports in .env
BACKEND_PORT=5001
POSTGRES_PORT=5433
```

### Database Connection Error

```bash
# Wait for database to initialize (10-15 seconds)
docker-compose logs db

# Look for: "database system is ready to accept connections"
```

### Reset Everything

```bash
# Remove all containers and data
docker-compose down -v

# Start fresh
docker-compose up -d --build
```

### Can't Access Frontend

```bash
# Option 1: Open file directly
# Just double-click frontend/login.html

# Option 2: Use Python HTTP server
cd frontend
python -m http.server 8000
# Then open: http://localhost:8000/login.html
```

---

## 📊 Database Schema

### Tables

- **users** - Student and faculty accounts
- **components** - Laboratory component inventory
- **requests** - Component borrowing requests
- **transactions** - Audit log of all actions

### Quick Database Access

```bash
# Using Docker
docker-compose exec db psql -U lablink_user -d lablink

# Common queries
SELECT * FROM users;
SELECT * FROM components;
SELECT * FROM requests;
SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 10;
```

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run specific test file
pytest test_auth.py

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## 📚 Documentation Links

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Choose your setup method
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Docker detailed guide
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Local setup guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
- **[DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md)** - AWS deployment

---

## 💡 Tips

1. **Use Docker for development** - No PostgreSQL installation needed
2. **Check logs first** - Most issues show up in `docker-compose logs`
3. **Reset when stuck** - `docker-compose down -v` gives you a fresh start
4. **Test API with curl** - Quick way to verify endpoints work
5. **Use browser DevTools** - Check Network tab for API errors

---

## 🎯 Next Steps

1. ✅ Start the application (Docker or local)
2. ✅ Login with default credentials
3. ✅ Explore student dashboard
4. ✅ Explore faculty dashboard
5. ✅ Read API documentation
6. ✅ Review database schema
7. ✅ Make your first code change
8. ✅ Deploy to AWS (when ready)

---

## 🆘 Getting Help

**Issue:** Can't start Docker containers  
**Solution:** Check Docker is running, ports are free

**Issue:** Database connection failed  
**Solution:** Wait 15 seconds for DB initialization

**Issue:** Frontend shows errors  
**Solution:** Check backend is running, check browser console

**Issue:** Can't login  
**Solution:** Check credentials, clear browser localStorage

**Issue:** API returns 401  
**Solution:** Token expired, login again

For more help, see the detailed guides in the Documentation section.
