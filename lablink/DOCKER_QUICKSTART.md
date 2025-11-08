# LabLink Docker Quick Start Guide

This guide will help you get the LabLink system running using Docker and Docker Compose.

## Why Use Docker?

**Docker is the recommended approach for local development** because:

✅ **No PostgreSQL installation needed** - PostgreSQL runs in a container  
✅ **Consistent environment** - Same setup for all developers  
✅ **Easy cleanup** - Remove everything with one command  
✅ **Isolated** - Doesn't affect your system  
✅ **Quick setup** - Running in under 2 minutes  

**For AWS deployment**, you can use:
- Docker containers on EC2/ECS
- AWS RDS for PostgreSQL (managed database)

See [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md) for AWS deployment options.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher

### Installing Docker

**Windows/Mac:**
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## Quick Start

### 1. Set up environment variables

Copy the example environment file:

```bash
cp .env.docker .env
```

For development, the default values in `.env.docker` will work. For production, make sure to:
- Change `SECRET_KEY` and `JWT_SECRET_KEY` to strong random values
- Set `FLASK_ENV=production`
- Update `POSTGRES_PASSWORD` to a strong password
- Configure specific `CORS_ORIGINS` (not `*`)

### 2. Build and start the containers

```bash
docker-compose up -d
```

This will:
- Build the Flask backend container
- Pull the PostgreSQL 14 image
- Create and start both containers
- Initialize the database with schema and seed data
- Set up networking between containers

### 3. Verify the deployment

Check that containers are running:

```bash
docker-compose ps
```

Check backend health:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "LabLink API",
  "database": "connected"
}
```

### 4. Access the application

- **Frontend:** Open `frontend/login.html` in your browser
- **API:** http://localhost:5000
- **Database:** localhost:5432

### Default Credentials

The seed data creates two default users:

**Faculty User:**
- Username: `faculty`
- Password: `faculty123`

**Student User:**
- Username: `student`
- Password: `student123`

## Common Commands

### View logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f db
```

### Stop the application

```bash
docker-compose down
```

### Stop and remove all data

```bash
docker-compose down -v
```

### Rebuild containers

```bash
docker-compose up -d --build
```

### Access database directly

```bash
docker-compose exec db psql -U lablink_user -d lablink
```

### Access backend shell

```bash
docker-compose exec backend /bin/bash
```

## Troubleshooting

### Port already in use

If port 5000 or 5432 is already in use, change the ports in `.env`:

```bash
BACKEND_PORT=5001
POSTGRES_PORT=5433
```

### Database connection errors

Wait for the database to be fully initialized (about 10-15 seconds on first run):

```bash
docker-compose logs db
```

Look for: `database system is ready to accept connections`

### Permission errors

If you encounter permission errors, ensure Docker has proper permissions:

```bash
# Linux only
sudo usermod -aG docker $USER
# Log out and back in
```

### Reset everything

To start fresh:

```bash
docker-compose down -v
docker-compose up -d --build
```

## Production Deployment

For production deployment:

1. Update `.env` with production values
2. Set `FLASK_ENV=production`
3. Use strong passwords and secret keys
4. Configure specific CORS origins
5. Consider using AWS RDS instead of containerized database
6. Set up SSL/TLS certificates
7. Configure proper firewall rules
8. Enable monitoring and logging

See `deployment/README.md` for detailed production deployment instructions.

## Next Steps

- Read the API documentation in the main README
- Explore the frontend dashboards
- Review the transaction logs
- Customize component types and inventory

## Support

For issues or questions, refer to:
- Main README.md
- API documentation
- Design document in `.kiro/specs/lablink-system/design.md`
