# LabLink Backend

Flask-based REST API for the LabLink Laboratory Component Management System.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Set Up Database

```bash
# Set database URL (adjust credentials as needed)
export DATABASE_URL="postgresql://lablink:lablink@localhost:5432/lablink"

# Initialize database tables
python init_db.py init

# Seed with sample data
python seed_data.py
```

### 3. Run the Application

```bash
python app.py
```

## Database Management

### Initialize Database

Creates all tables and indexes:

```bash
python init_db.py init
```

### Seed Sample Data

Adds default users, components, and sample requests:

```bash
python seed_data.py
```

Default credentials:
- Faculty: `faculty` / `faculty123`
- Student: `student` / `student123`

### Clear All Data

Remove all data from database:

```bash
python seed_data.py clear
```

### Drop All Tables

Completely remove all tables:

```bash
python init_db.py drop
```

### Using Flask-Migrate

Set up migrations:

```bash
python init_db.py setup-migrations
```

Create a migration:

```bash
flask db migrate -m "Description"
```

Apply migrations:

```bash
flask db upgrade
```

## Project Structure

```
backend/
├── models.py           # SQLAlchemy database models
├── init_db.py          # Database initialization script
├── seed_data.py        # Sample data seeding script
├── schema.sql          # Raw SQL schema (alternative)
├── seed_data.sql       # Raw SQL seed data (alternative)
├── DATABASE.md         # Detailed database documentation
└── README.md           # This file
```

## Database Models

- **User**: Student and faculty accounts
- **Component**: Laboratory inventory items
- **Request**: Component borrowing requests
- **Transaction**: Audit log for all actions

See `DATABASE.md` for detailed schema documentation.

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (required)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (required for auth)
- `FLASK_ENV`: Environment mode (development/production)

## Next Steps

After setting up the database:

1. Implement authentication endpoints (Task 3)
2. Implement component management endpoints (Task 4)
3. Implement request management endpoints (Task 5)
4. Build frontend interfaces (Tasks 8-9)

## Troubleshooting

### Database Connection Issues

If you can't connect to PostgreSQL:

1. Ensure PostgreSQL is running
2. Verify credentials in `DATABASE_URL`
3. Check `pg_hba.conf` allows local connections

### Import Errors

If you get import errors:

```bash
# Make sure you're in the backend directory
cd backend

# Or add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

See `DATABASE.md` for more troubleshooting tips.
