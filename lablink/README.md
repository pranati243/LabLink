# LabLink - Laboratory Component Management System

LabLink is a full-stack web application designed to help educational institutions manage electronic components inventory (Arduino boards, sensors, modules, cables). The system enables students to view and request components while allowing faculty to manage inventory, approve requests, and track all transactions.

## Features

### For Students
- 🔍 **Browse Components** - View all available laboratory components with search and filter capabilities
- 📝 **Submit Requests** - Request components with quantity validation
- 📊 **Track Requests** - Monitor request status in real-time (Pending, Approved, Rejected, Returned)
- 🔔 **Status Updates** - Receive automatic notifications when request status changes
- 📱 **Responsive Interface** - Clean, modern UI built with Bootstrap 5

### For Faculty
- ➕ **Manage Inventory** - Add, edit, and delete components with full CRUD operations
- ✅ **Approve Requests** - Review and approve student component requests
- ❌ **Reject Requests** - Reject requests with optional reason
- 🔄 **Track Returns** - Mark components as returned and update inventory
- 📋 **Transaction Log** - View complete audit trail of all system activities
- 🔎 **Advanced Filtering** - Filter transactions by date, user, action type, and component

### System Features
- 🔐 **Secure Authentication** - JWT-based authentication with role-based access control
- 📦 **Inventory Management** - Real-time quantity tracking with validation
- 📝 **Audit Trail** - Complete transaction logging for accountability
- 🐳 **Docker Support** - Easy deployment with Docker and Docker Compose
- ☁️ **Cloud Ready** - Deployment guides for AWS EC2 and RDS

## Technology Stack

### Backend
- **Framework**: Python Flask 3.0+
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **Password Hashing**: bcrypt
- **Server**: Gunicorn (production)

### Frontend
- **HTML5** with semantic markup
- **Bootstrap 5.3** for responsive UI
- **Vanilla JavaScript** (ES6+)
- **LocalStorage** for JWT token management

### DevOps
- **Containerization**: Docker & Docker Compose
- **Cloud**: AWS EC2, AWS RDS, AWS S3 (optional)
- **Database**: PostgreSQL with connection pooling

## Setup Options

> **❓ Do I need to install PostgreSQL?**  
> **NO** if you use Docker (recommended) - PostgreSQL runs in a container!  
> See [DO_I_NEED_POSTGRESQL.md](DO_I_NEED_POSTGRESQL.md) for details.

Choose the setup method that works best for you:

| Method | PostgreSQL | Setup Time | Best For |
|--------|-----------|------------|----------|
| **Docker** ✅ | Included in container | 2 minutes | Quick start, no local PostgreSQL needed |
| **Local** | Install separately | 15-30 minutes | Custom development environment |
| **AWS** | Use RDS (managed) | Varies | Production deployment |

## Quick Start

### Option 1: Docker (Recommended) 🐳

**No PostgreSQL installation needed** - everything runs in containers:

The fastest way to get started:

```bash
# 1. Clone the repository
git clone <repository-url>
cd lablink

# 2. Copy environment file
cp .env.docker .env

# 3. Start with Docker Compose
docker-compose up -d

# 4. Access the application
# Open frontend/login.html in your browser
```

**Default Credentials:**
- Faculty: `faculty` / `faculty123`
- Student: `student` / `student123`

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for detailed Docker instructions.

### Option 2: Local Development

For local development without Docker:

```bash
# 1. Install Python 3.11+
python --version

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL database
# Install PostgreSQL 14+ and create database
createdb lablink

# 5. Configure environment
export DATABASE_URL="postgresql://username:password@localhost:5432/lablink"
export JWT_SECRET_KEY="your-secret-key-here"

# 6. Initialize database
cd backend
python init_db.py init
python seed_data.py

# 7. Run the application
python app.py

# 8. Open frontend/login.html in your browser
```

See detailed setup instructions in the [Local Development Setup](#local-development-setup) section below.

## Project Structure

```
lablink/
├── backend/                 # Flask REST API
│   ├── app.py              # Main application entry point
│   ├── models.py           # SQLAlchemy database models
│   ├── auth.py             # Authentication logic
│   ├── auth_routes.py      # Authentication endpoints
│   ├── component_routes.py # Component management endpoints
│   ├── request_routes.py   # Request management endpoints
│   ├── transaction_routes.py # Transaction log endpoints
│   ├── middleware.py       # JWT and role-based auth decorators
│   ├── config.py           # Configuration management
│   ├── init_db.py          # Database initialization script
│   ├── seed_data.py        # Sample data seeding
│   ├── schema.sql          # SQL schema definition
│   └── test_*.py           # Test files
├── frontend/               # Static web interface
│   ├── login.html          # Login page
│   ├── student_dashboard.html  # Student interface
│   ├── faculty_dashboard.html  # Faculty interface
│   ├── api.js              # API client with JWT handling
│   ├── utils.js            # Common utility functions
│   ├── student_dashboard.js    # Student dashboard logic
│   └── faculty_dashboard.js    # Faculty dashboard logic
├── deployment/             # Deployment configurations
├── .kiro/specs/           # Design and requirements documents
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Backend container definition
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (admin only)
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/refresh` - Refresh expired token

### Components
- `GET /api/components` - List all components (with filters)
- `POST /api/components` - Create component (faculty only)
- `GET /api/components/<id>` - Get component details
- `PUT /api/components/<id>` - Update component (faculty only)
- `DELETE /api/components/<id>` - Delete component (faculty only)

### Requests
- `GET /api/requests` - List requests (role-filtered)
- `POST /api/requests` - Create request (student only)
- `GET /api/requests/<id>` - Get request details
- `POST /api/requests/<id>/approve` - Approve request (faculty only)
- `POST /api/requests/<id>/reject` - Reject request (faculty only)
- `POST /api/requests/<id>/return` - Mark as returned (faculty only)

### Transactions
- `GET /api/transactions` - List all transactions (faculty only)

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API documentation with request/response examples.

## Documentation

### Setup Guides
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 🎯 **START HERE** - Choose your setup method (Docker/Local/AWS)
- **[DO_I_NEED_POSTGRESQL.md](DO_I_NEED_POSTGRESQL.md)** - ❓ **Common Question** - Do I need to install PostgreSQL?
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⚡ **Quick Commands** - Common commands and troubleshooting
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Quick start guide for Docker deployment (no PostgreSQL install needed)
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Manual setup guide (install PostgreSQL locally)
- **[AWS_QUICKSTART.md](AWS_QUICKSTART.md)** - 🚀 **Just got your EC2 key?** - Quick AWS deployment steps
- **[DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md)** - AWS EC2 and RDS deployment guide (comprehensive)

### Reference Documentation
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[AWS_S3_INTEGRATION.md](AWS_S3_INTEGRATION.md)** - Optional AWS S3 integration for component images
- **[backend/README.md](backend/README.md)** - Backend development guide
- **[backend/DATABASE.md](backend/DATABASE.md)** - Database schema documentation
- **[frontend/README.md](frontend/README.md)** - Frontend development guide

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

#### 1. Install Python

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### 2. Install PostgreSQL

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run installer and remember the password you set

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 3. Create Database

```bash
# Switch to postgres user (Linux only)
sudo -u postgres psql

# Or connect directly (Windows/Mac)
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE lablink;
CREATE USER lablink_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lablink TO lablink_user;
\q
```

#### 4. Clone and Setup Project

```bash
# Clone repository
git clone <repository-url>
cd lablink

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env

# Edit .env with your values
DATABASE_URL=postgresql://lablink_user:your_password@localhost:5432/lablink
JWT_SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
```

Or export directly:

```bash
export DATABASE_URL="postgresql://lablink_user:your_password@localhost:5432/lablink"
export JWT_SECRET_KEY="your-secret-key-here"
export FLASK_ENV="development"
```

#### 6. Initialize Database

```bash
cd backend

# Create tables
python init_db.py init

# Load sample data
python seed_data.py
```

This creates:
- Default faculty user: `faculty` / `faculty123`
- Default student user: `student` / `student123`
- Sample components (Arduino boards, sensors, etc.)
- Sample requests

#### 7. Run the Application

```bash
# From backend directory
python app.py
```

The API will be available at `http://localhost:5000`

#### 8. Access the Frontend

Open `frontend/login.html` in your web browser, or serve it with a local server:

```bash
# Option 1: Python HTTP server
cd frontend
python -m http.server 8000
# Open http://localhost:8000/login.html

# Option 2: Just open the file
# Open frontend/login.html directly in your browser
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest test_auth.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Docker Deployment

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for complete Docker deployment instructions.

### Quick Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Access database
docker-compose exec db psql -U lablink_user -d lablink
```

## AWS Deployment

See [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md) for complete AWS deployment guide including:
- EC2 instance setup
- RDS PostgreSQL configuration
- Security group configuration
- SSL/TLS setup
- Optional S3 integration for component images

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | - | Yes |
| `FLASK_ENV` | Environment mode | `development` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |
| `JWT_ACCESS_TOKEN_EXPIRES` | Token expiration (hours) | `1` | No |
| `AWS_S3_BUCKET` | S3 bucket for images | - | No |
| `AWS_ACCESS_KEY_ID` | AWS access key | - | No |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | No |

## Security Considerations

- **Passwords**: Hashed using bcrypt with cost factor 12
- **JWT Tokens**: 1-hour expiration with refresh token support
- **HTTPS**: Required in production (configure reverse proxy)
- **CORS**: Configure specific origins in production
- **SQL Injection**: Prevented via SQLAlchemy ORM
- **XSS**: Input sanitization and HTML escaping
- **Environment Variables**: Never commit secrets to version control

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
# Linux:
sudo systemctl status postgresql
# macOS:
brew services list
# Windows: Check Services app

# Test connection
psql -U lablink_user -d lablink -h localhost

# Check DATABASE_URL format
echo $DATABASE_URL
```

### Port Already in Use

```bash
# Find process using port 5000
# Linux/macOS:
lsof -i :5000
# Windows:
netstat -ano | findstr :5000

# Kill the process or change port in config
```

### Import Errors

```bash
# Ensure you're in the correct directory
cd backend

# Activate virtual environment
source ../venv/bin/activate  # macOS/Linux
..\venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r ../requirements.txt
```

### Docker Issues

```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build

# Check logs
docker-compose logs backend
docker-compose logs db
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- Review the documentation in the `docs/` directory
- Check existing issues on GitHub
- Create a new issue with detailed information

## Acknowledgments

Built with Flask, PostgreSQL, Bootstrap, and Docker.
