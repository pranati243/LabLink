# LabLink Setup Guide - Choose Your Path

This guide helps you choose the best setup method for your needs.

## 🎯 Quick Decision Guide

**Want to start immediately without installing PostgreSQL?**  
→ Use **Docker** (see below)

**Need a custom development environment?**  
→ Use **Local Setup** (install PostgreSQL manually)

**Deploying to production?**  
→ Use **AWS** with RDS (managed PostgreSQL)

---

## Option 1: Docker Setup (Recommended) 🐳

### What You Get
- ✅ PostgreSQL runs in a container (no local installation)
- ✅ Backend runs in a container
- ✅ Everything isolated and easy to remove
- ✅ Same environment for all developers

### What You Need
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- 2 minutes of your time

### Quick Start

```bash
# 1. Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# 2. Clone and start
git clone <repository-url>
cd lablink
cp .env.docker .env
docker-compose up -d

# 3. Open frontend/login.html in your browser
# Login: faculty/faculty123 or student/student123
```

### How It Works

```
┌─────────────────────────────────────┐
│         Your Computer               │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Docker Container 1         │  │
│  │   PostgreSQL Database        │  │
│  │   Port: 5432                 │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Docker Container 2         │  │
│  │   Flask Backend              │  │
│  │   Port: 5000                 │  │
│  └──────────────────────────────┘  │
│                                     │
│  Frontend files (HTML/JS)           │
│  Open directly in browser           │
└─────────────────────────────────────┘
```

**Full Guide:** [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

---

## Option 2: Local Setup (Manual)

### What You Get
- ✅ Full control over your environment
- ✅ Direct access to PostgreSQL
- ✅ No Docker required

### What You Need
- Python 3.11+
- PostgreSQL 14+ (you install this)
- 15-30 minutes for setup

### Quick Start

```bash
# 1. Install PostgreSQL
# Windows: Download from postgresql.org
# Mac: brew install postgresql@14
# Linux: sudo apt install postgresql

# 2. Create database
createdb lablink

# 3. Set up Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure environment
export DATABASE_URL="postgresql://user:pass@localhost:5432/lablink"
export JWT_SECRET_KEY="your-secret-key"

# 5. Initialize and run
cd backend
python init_db.py init
python seed_data.py
python app.py

# 6. Open frontend/login.html in browser
```

### How It Works

```
┌─────────────────────────────────────┐
│         Your Computer               │
│                                     │
│  PostgreSQL (installed locally)     │
│  Port: 5432                         │
│                                     │
│  Python Virtual Environment         │
│  Flask Backend                      │
│  Port: 5000                         │
│                                     │
│  Frontend files (HTML/JS)           │
│  Open directly in browser           │
└─────────────────────────────────────┘
```

**Full Guide:** [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)

---

## Option 3: AWS Deployment (Production)

### What You Get
- ✅ Managed PostgreSQL (AWS RDS)
- ✅ Scalable infrastructure
- ✅ Production-ready
- ✅ Optional S3 for images

### What You Need
- AWS Account
- Basic AWS knowledge
- 30-60 minutes for setup

### Architecture

```
┌─────────────────────────────────────────────┐
│              AWS Cloud                      │
│                                             │
│  ┌──────────────┐      ┌──────────────┐   │
│  │   EC2        │      │   RDS        │   │
│  │   Instance   │─────▶│  PostgreSQL  │   │
│  │   (Backend)  │      │   (Managed)  │   │
│  └──────────────┘      └──────────────┘   │
│         │                                   │
│         │                                   │
│  ┌──────▼───────┐      ┌──────────────┐   │
│  │   S3 Bucket  │      │  CloudFront  │   │
│  │   (Images)   │◀─────│     (CDN)    │   │
│  └──────────────┘      └──────────────┘   │
└─────────────────────────────────────────────┘
```

**Full Guide:** [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md)

---

## Comparison Table

| Feature | Docker | Local | AWS |
|---------|--------|-------|-----|
| **PostgreSQL Installation** | Not needed | Required | Managed (RDS) |
| **Setup Time** | 2 min | 15-30 min | 30-60 min |
| **Isolation** | Full | None | Full |
| **Easy Cleanup** | Yes | No | Varies |
| **Cost** | Free | Free | Paid |
| **Best For** | Development | Custom dev | Production |
| **Database Access** | Via Docker | Direct | Via RDS |
| **Scalability** | Limited | Limited | High |

---

## Frequently Asked Questions

### Can I use Docker locally and AWS for production?
**Yes!** This is the recommended approach:
- Use Docker for local development (fast, isolated)
- Deploy to AWS for production (scalable, managed)

### Do I need to install PostgreSQL if I use Docker?
**No!** PostgreSQL runs inside a Docker container. You don't need to install it on your machine.

### Can I switch between Docker and local setup?
**Yes!** Just make sure to:
1. Stop Docker containers: `docker-compose down`
2. Update your `DATABASE_URL` to point to local PostgreSQL
3. Run the backend locally

### Which option should I choose?
- **Just want to try it?** → Docker
- **Developing a feature?** → Docker
- **Need custom PostgreSQL config?** → Local
- **Deploying for users?** → AWS

---

## Next Steps

After choosing your setup method:

1. **Complete the setup** using the appropriate guide
2. **Login** with default credentials (faculty/faculty123 or student/student123)
3. **Explore** the student and faculty dashboards
4. **Read** the [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
5. **Review** the design in [.kiro/specs/lablink-system/design.md](.kiro/specs/lablink-system/design.md)

---

## Getting Help

- **Docker issues?** → [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **Local setup issues?** → [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **AWS deployment?** → [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md)
- **API questions?** → [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## Summary

**For most users, Docker is the best choice** because:
- No PostgreSQL installation needed
- Quick setup (2 minutes)
- Easy to remove everything
- Same environment for everyone

**Use local setup** if you need custom PostgreSQL configuration or prefer not to use Docker.

**Use AWS** when you're ready to deploy for production use.
