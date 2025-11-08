# LabLink System Design Document

## Overview

LabLink is a full-stack web application for managing laboratory electronic components. The system uses a Flask REST API backend with JWT authentication, a PostgreSQL database, and a Bootstrap-based frontend. The application is containerized using Docker and can be deployed locally or on AWS EC2 with RDS.

### Technology Stack

- **Backend**: Python Flask with Flask-RESTful, Flask-JWT-Extended, Flask-SQLAlchemy
- **Database**: PostgreSQL 14+
- **Frontend**: HTML5, Bootstrap 5, JavaScript (Vanilla)
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Containerization**: Docker and Docker Compose
- **Cloud**: AWS EC2, AWS RDS, AWS S3 (optional)

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A[Student Dashboard]
        B[Faculty Dashboard]
    end
    
    subgraph "Application Layer"
        C[Flask REST API]
        D[JWT Auth Middleware]
        E[Business Logic Layer]
    end
    
    subgraph "Data Layer"
        F[PostgreSQL Database]
        G[Transaction Log]
    end
    
    subgraph "External Services"
        H[AWS S3 - Optional Images]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    E -.-> H
```

### Deployment Architecture

```mermaid
graph LR
    subgraph "Docker Compose - Local"
        A[Flask Container]
        B[PostgreSQL Container]
        A --> B
    end
    
    subgraph "AWS Cloud - Production"
        C[EC2 Instance]
        D[RDS PostgreSQL]
        E[S3 Bucket]
        C --> D
        C -.-> E
    end
```

## Components and Interfaces

### Backend Components

#### 1. Application Entry Point (`app.py`)
- Initialize Flask application
- Configure CORS, JWT, SQLAlchemy
- Register blueprints for routes
- Set up error handlers

#### 2. Authentication Module (`auth.py`)
- `/api/auth/register` - POST: Register new users (admin only for production)
- `/api/auth/login` - POST: Authenticate and return JWT token
- `/api/auth/refresh` - POST: Refresh expired JWT token
- Password hashing using bcrypt
- JWT token generation and validation

#### 3. Component Management Module (`components.py`)
- `/api/components` - GET: List all components (with filters)
- `/api/components` - POST: Create new component (faculty only)
- `/api/components/<id>` - GET: Get component details
- `/api/components/<id>` - PUT: Update component (faculty only)
- `/api/components/<id>` - DELETE: Delete component (faculty only)
- `/api/components/search` - GET: Search components by name/type

#### 4. Request Management Module (`requests.py`)
- `/api/requests` - GET: List requests (filtered by role)
- `/api/requests` - POST: Create new request (student only)
- `/api/requests/<id>` - GET: Get request details
- `/api/requests/<id>/approve` - POST: Approve request (faculty only)
- `/api/requests/<id>/reject` - POST: Reject request (faculty only)
- `/api/requests/<id>/return` - POST: Mark as returned (faculty only)

#### 5. Transaction Log Module (`transactions.py`)
- `/api/transactions` - GET: List all transactions (faculty only)
- `/api/transactions/search` - GET: Search/filter transactions
- Automatic logging for all CRUD operations

#### 6. Database Models (`models.py`)
- User model
- Component model
- Request model
- Transaction model

#### 7. Middleware (`middleware.py`)
- JWT authentication decorator
- Role-based access control decorator
- Request validation decorator

### Frontend Components

#### 1. Authentication Pages
- `login.html` - Login form for all users
- Client-side JWT storage in localStorage
- Automatic redirect based on user role

#### 2. Student Dashboard (`student_dashboard.html`)
- Component listing with search/filter
- Request submission form
- My requests view with status
- Real-time status updates

#### 3. Faculty Dashboard (`faculty_dashboard.html`)
- Component management (CRUD operations)
- Pending requests queue
- Request approval/rejection interface
- Return marking interface
- Transaction log viewer

#### 4. Shared Components
- `navbar.html` - Navigation component
- `api.js` - API client wrapper with JWT handling
- `utils.js` - Common utility functions

## Data Models

### User Model

```python
class User:
    id: Integer (Primary Key)
    username: String(80) (Unique, Not Null)
    email: String(120) (Unique, Not Null)
    password_hash: String(255) (Not Null)
    role: Enum('student', 'faculty') (Not Null)
    created_at: DateTime (Default: now)
    
    # Relationships
    requests: One-to-Many with Request
    transactions: One-to-Many with Transaction
```

### Component Model

```python
class Component:
    id: Integer (Primary Key)
    name: String(100) (Not Null)
    type: String(50) (Not Null)
    quantity: Integer (Not Null, Default: 0)
    description: Text
    image_url: String(255) (Nullable)
    location: String(100) (Not Null)
    created_at: DateTime (Default: now)
    updated_at: DateTime (Default: now, onupdate: now)
    
    # Relationships
    requests: One-to-Many with Request
    transactions: One-to-Many with Transaction
```

### Request Model

```python
class Request:
    id: Integer (Primary Key)
    student_id: Integer (Foreign Key -> User.id, Not Null)
    component_id: Integer (Foreign Key -> Component.id, Not Null)
    quantity: Integer (Not Null)
    status: Enum('Pending', 'Approved', 'Rejected', 'Returned') (Default: 'Pending')
    rejection_reason: Text (Nullable)
    requested_at: DateTime (Default: now)
    processed_at: DateTime (Nullable)
    processed_by: Integer (Foreign Key -> User.id, Nullable)
    returned_at: DateTime (Nullable)
    
    # Relationships
    student: Many-to-One with User
    component: Many-to-One with Component
    processor: Many-to-One with User
    transactions: One-to-Many with Transaction
```

### Transaction Model

```python
class Transaction:
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> User.id, Not Null)
    action_type: Enum('CREATE', 'UPDATE', 'DELETE', 'REQUEST', 'APPROVE', 'REJECT', 'RETURN') (Not Null)
    entity_type: Enum('Component', 'Request', 'User') (Not Null)
    entity_id: Integer (Not Null)
    details: JSON (Nullable)
    timestamp: DateTime (Default: now)
    
    # Relationships
    user: Many-to-One with User
```

### Database Schema Diagram

```mermaid
erDiagram
    USER ||--o{ REQUEST : creates
    USER ||--o{ TRANSACTION : performs
    USER ||--o{ REQUEST : processes
    COMPONENT ||--o{ REQUEST : "requested in"
    COMPONENT ||--o{ TRANSACTION : "logged in"
    REQUEST ||--o{ TRANSACTION : "logged in"
    
    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        enum role
        datetime created_at
    }
    
    COMPONENT {
        int id PK
        string name
        string type
        int quantity
        text description
        string image_url
        string location
        datetime created_at
        datetime updated_at
    }
    
    REQUEST {
        int id PK
        int student_id FK
        int component_id FK
        int quantity
        enum status
        text rejection_reason
        datetime requested_at
        datetime processed_at
        int processed_by FK
        datetime returned_at
    }
    
    TRANSACTION {
        int id PK
        int user_id FK
        enum action_type
        enum entity_type
        int entity_id
        json details
        datetime timestamp
    }
```

## API Design

### Authentication Endpoints

#### POST /api/auth/register
```json
Request:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "student"
}

Response (201):
{
  "message": "User registered successfully",
  "user_id": 1
}
```

#### POST /api/auth/login
```json
Request:
{
  "username": "john_doe",
  "password": "SecurePass123"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "role": "student"
  }
}
```

### Component Endpoints

#### GET /api/components
```json
Query Parameters:
- type: string (optional)
- search: string (optional)
- available_only: boolean (optional)

Response (200):
{
  "components": [
    {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 15,
      "description": "ATmega328P based board",
      "image_url": "https://example.com/arduino.jpg",
      "location": "Rack A, Shelf 2"
    }
  ],
  "total": 1
}
```

#### POST /api/components (Faculty Only)
```json
Request:
{
  "name": "Arduino Uno R3",
  "type": "Microcontroller",
  "quantity": 15,
  "description": "ATmega328P based board",
  "image_url": "https://example.com/arduino.jpg",
  "location": "Rack A, Shelf 2"
}

Response (201):
{
  "message": "Component created successfully",
  "component": { /* component object */ }
}
```

### Request Endpoints

#### POST /api/requests (Student Only)
```json
Request:
{
  "component_id": 1,
  "quantity": 2
}

Response (201):
{
  "message": "Request created successfully",
  "request": {
    "id": 1,
    "component_id": 1,
    "quantity": 2,
    "status": "Pending",
    "requested_at": "2025-11-08T10:30:00Z"
  }
}
```

#### POST /api/requests/{id}/approve (Faculty Only)
```json
Response (200):
{
  "message": "Request approved successfully",
  "request": { /* updated request object */ }
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "status_code": 400
}
```

### Error Types

1. **Authentication Errors (401)**
   - Invalid credentials
   - Expired token
   - Missing token

2. **Authorization Errors (403)**
   - Insufficient permissions
   - Role mismatch

3. **Validation Errors (400)**
   - Missing required fields
   - Invalid data format
   - Business rule violations

4. **Not Found Errors (404)**
   - Resource not found

5. **Server Errors (500)**
   - Database connection errors
   - Unexpected exceptions

### Error Handling Strategy

- All exceptions caught by Flask error handlers
- Database transactions rolled back on errors
- Detailed logging for debugging
- User-friendly error messages
- No sensitive information in error responses

## Security Considerations

### Authentication & Authorization
- Passwords hashed using bcrypt (cost factor: 12)
- JWT tokens with 1-hour expiration
- Refresh tokens with 30-day expiration
- Role-based access control on all endpoints
- HTTPS required in production

### Input Validation
- All inputs validated before processing
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via input sanitization
- CSRF protection for state-changing operations

### Database Security
- Parameterized queries only
- Least privilege database user
- Connection pooling with limits
- Encrypted connections in production

### Environment Variables
- Sensitive configuration in environment variables
- No hardcoded credentials
- Different configs for dev/prod

## Testing Strategy

### Unit Tests
- Test all model methods
- Test authentication logic
- Test business logic functions
- Test utility functions
- Target: 80% code coverage

### Integration Tests
- Test API endpoints
- Test database operations
- Test authentication flow
- Test authorization rules

### Test Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_auth.py
│   └── test_utils.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_components_api.py
│   ├── test_requests_api.py
│   └── test_transactions_api.py
└── conftest.py (pytest fixtures)
```

### Testing Tools
- pytest for test framework
- pytest-flask for Flask testing
- pytest-cov for coverage reports
- Factory Boy for test data generation

## Deployment Configuration

### Docker Configuration

#### Dockerfile (Backend)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/lablink
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=lablink
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### AWS Deployment

#### EC2 Configuration
- Instance Type: t2.micro (Free Tier)
- OS: Ubuntu 22.04 LTS
- Security Group Rules:
  - SSH (22) from your IP
  - HTTP (80) from anywhere
  - HTTPS (443) from anywhere
  - Custom TCP (5000) from anywhere (or use nginx reverse proxy)

#### RDS Configuration
- Engine: PostgreSQL 14
- Instance Class: db.t3.micro (Free Tier)
- Storage: 20 GB SSD
- Security Group: Allow PostgreSQL (5432) from EC2 security group

#### Environment Variables (Production)
```bash
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/lablink
JWT_SECRET_KEY=<strong-random-key>
FLASK_ENV=production
AWS_S3_BUCKET=lablink-images (optional)
AWS_ACCESS_KEY_ID=<key> (optional)
AWS_SECRET_ACCESS_KEY=<secret> (optional)
```

## Performance Considerations

### Database Optimization
- Indexes on foreign keys
- Index on component.name for search
- Index on request.status for filtering
- Connection pooling (max 20 connections)

### Caching Strategy
- Cache component list (5-minute TTL)
- Cache user permissions
- No caching for request status (real-time required)

### API Response Optimization
- Pagination for large lists (default: 50 items)
- Selective field loading
- Compressed responses (gzip)

## Monitoring and Logging

### Application Logging
- Log all authentication attempts
- Log all database errors
- Log all API requests (with timing)
- Structured logging (JSON format)

### Log Levels
- DEBUG: Development only
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures requiring attention

### Monitoring Metrics
- Request rate and latency
- Error rate by endpoint
- Database connection pool usage
- JWT token validation failures
