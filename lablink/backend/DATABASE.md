# Database Setup Guide

## Prerequisites

- PostgreSQL 14 or higher installed
- Python 3.11 or higher
- Virtual environment activated

## Quick Start

### 1. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE lablink;
CREATE USER lablink WITH PASSWORD 'lablink';
GRANT ALL PRIVILEGES ON DATABASE lablink TO lablink;
\q
```

### 2. Set Environment Variable

```bash
# Linux/Mac
export DATABASE_URL="postgresql://lablink:lablink@localhost:5432/lablink"

# Windows (CMD)
set DATABASE_URL=postgresql://lablink:lablink@localhost:5432/lablink

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://lablink:lablink@localhost:5432/lablink"
```

### 3. Initialize Database

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database tables
cd backend
python init_db.py init
```

## Using Flask-Migrate

Flask-Migrate provides database migration support for SQLAlchemy.

### Setup Migrations

```bash
cd backend
python init_db.py setup-migrations
```

### Create a Migration

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

## Using Raw SQL Schema

If you prefer to use the raw SQL schema:

```bash
psql -U lablink -d lablink -f backend/schema.sql
```

## Database Structure

### Tables

- **users**: User accounts (students and faculty)
- **components**: Laboratory component inventory
- **requests**: Component borrowing requests
- **transactions**: Audit log for all system actions

### Indexes

Performance indexes are automatically created on:
- Foreign keys
- Search fields (name, type)
- Status fields
- Timestamp fields

## Troubleshooting

### Connection Issues

If you can't connect to the database:

1. Check PostgreSQL is running: `pg_isready`
2. Verify credentials in DATABASE_URL
3. Check PostgreSQL allows local connections in `pg_hba.conf`

### Permission Issues

If you get permission errors:

```sql
-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE lablink TO lablink;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lablink;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lablink;
```

### Reset Database

To completely reset the database:

```bash
cd backend
python init_db.py drop
python init_db.py init
```

## Production Considerations

For production deployment:

1. Use strong passwords
2. Enable SSL connections
3. Use connection pooling
4. Set up regular backups
5. Monitor database performance
6. Use environment variables for credentials (never hardcode)
