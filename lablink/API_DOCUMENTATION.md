# LabLink API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Authentication Endpoints](#authentication-endpoints)
4. [Component Endpoints](#component-endpoints)
5. [Request Endpoints](#request-endpoints)
6. [Transaction Endpoints](#transaction-endpoints)
7. [Error Codes and Messages](#error-codes-and-messages)

---

## Overview

The LabLink API is a RESTful API for managing laboratory components, student requests, and transaction logs. All endpoints return JSON responses and use JWT (JSON Web Token) for authentication.

### Base URL

```
http://localhost:5000/api
```

### Content Type

All requests and responses use `application/json` content type.

### Authentication

Most endpoints require authentication using JWT tokens. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Response Format

All responses follow a consistent JSON format:

**Success Response:**
```json
{
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

**Error Response:**
```json
{
  "error": "Error type",
  "message": "Human-readable error message"
}
```

---

## Authentication

### Authentication Requirements

| Endpoint | Authentication Required | Role Required |
|----------|------------------------|---------------|
| POST /api/auth/register | No | None |
| POST /api/auth/login | No | None |
| POST /api/auth/refresh | Yes (Refresh Token) | None |
| GET /api/components | Yes | Any |
| POST /api/components | Yes | Faculty |
| GET /api/components/:id | Yes | Any |
| PUT /api/components/:id | Yes | Faculty |
| DELETE /api/components/:id | Yes | Faculty |
| POST /api/requests | Yes | Student |
| GET /api/requests | Yes | Any |
| GET /api/requests/:id | Yes | Any |
| POST /api/requests/:id/approve | Yes | Faculty |
| POST /api/requests/:id/reject | Yes | Faculty |
| POST /api/requests/:id/return | Yes | Faculty |
| GET /api/transactions | Yes | Faculty |

### Token Types

**Access Token:**
- Used for authenticating API requests
- Expires after 1 hour
- Include in Authorization header: `Bearer <access_token>`

**Refresh Token:**
- Used to obtain new access tokens
- Expires after 30 days
- Include in Authorization header when calling `/api/auth/refresh`

---

## Authentication Endpoints

### POST /api/auth/register

Register a new user account.

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "student"
}
```

**Request Fields:**
- `username` (string, required): Unique username (3-80 characters)
- `email` (string, required): Unique email address
- `password` (string, required): Password (minimum 6 characters)
- `role` (string, required): User role - either "student" or "faculty"

**Success Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "student",
    "created_at": "2025-11-08T10:30:00Z"
  }
}
```

**Error Responses:**

*400 Bad Request - Missing fields:*
```json
{
  "error": "Validation error",
  "message": "Missing required fields: username, password"
}
```

*400 Bad Request - Username exists:*
```json
{
  "error": "Validation error",
  "message": "Username already exists"
}
```

*400 Bad Request - Email exists:*
```json
{
  "error": "Validation error",
  "message": "Email already exists"
}
```

*400 Bad Request - Invalid role:*
```json
{
  "error": "Validation error",
  "message": "Role must be either \"student\" or \"faculty\""
}
```

*400 Bad Request - Password too short:*
```json
{
  "error": "Validation error",
  "message": "Password must be at least 6 characters long"
}
```

---

### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123"
}
```

**Request Fields:**
- `username` (string, required): User's username
- `password` (string, required): User's password

**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "student",
    "created_at": "2025-11-08T10:30:00Z"
  }
}
```

**Error Responses:**

*400 Bad Request - Missing credentials:*
```json
{
  "error": "Validation error",
  "message": "Username and password are required"
}
```

*401 Unauthorized - Invalid credentials:*
```json
{
  "error": "Authentication failed",
  "message": "Invalid username or password"
}
```

---

### POST /api/auth/refresh

Refresh an expired access token using a refresh token.

**Authentication:** Required (Refresh Token)

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "message": "Token refreshed successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Responses:**

*401 Unauthorized - Invalid or expired token:*
```json
{
  "error": "Authentication failed",
  "message": "Invalid or expired refresh token"
}
```

*401 Unauthorized - User not found:*
```json
{
  "error": "Authentication failed",
  "message": "User not found"
}
```

---

## Component Endpoints

### GET /api/components

Retrieve all components with optional filtering and search.

**Authentication:** Required (Any role)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `type` (string, optional): Filter by component type
- `search` (string, optional): Search by component name (case-insensitive)
- `available_only` (boolean, optional): Show only components with quantity > 0

**Example Request:**
```
GET /api/components?type=Microcontroller&available_only=true
```

**Success Response (200 OK):**
```json
{
  "components": [
    {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 15,
      "description": "ATmega328P based microcontroller board",
      "image_url": "https://example.com/arduino-uno.jpg",
      "location": "Rack A, Shelf 2",
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-08T14:30:00Z"
    },
    {
      "id": 2,
      "name": "Arduino Mega 2560",
      "type": "Microcontroller",
      "quantity": 8,
      "description": "ATmega2560 based board with more I/O pins",
      "image_url": "https://example.com/arduino-mega.jpg",
      "location": "Rack A, Shelf 2",
      "created_at": "2025-11-01T10:05:00Z",
      "updated_at": "2025-11-08T14:30:00Z"
    }
  ],
  "total": 2
}
```

**Error Responses:**

*401 Unauthorized - Missing or invalid token:*
```json
{
  "error": "Authentication failed",
  "message": "Missing or invalid authentication token"
}
```

---

### POST /api/components

Create a new component in the inventory.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Arduino Uno R3",
  "type": "Microcontroller",
  "quantity": 15,
  "description": "ATmega328P based microcontroller board",
  "image_url": "https://example.com/arduino-uno.jpg",
  "location": "Rack A, Shelf 2"
}
```

**Request Fields:**
- `name` (string, required): Component name
- `type` (string, required): Component type/category
- `quantity` (integer, required): Available quantity (must be positive)
- `description` (string, optional): Component description
- `image_url` (string, optional): URL to component image
- `location` (string, required): Storage location

**Success Response (201 Created):**
```json
{
  "message": "Component created successfully",
  "component": {
    "id": 1,
    "name": "Arduino Uno R3",
    "type": "Microcontroller",
    "quantity": 15,
    "description": "ATmega328P based microcontroller board",
    "image_url": "https://example.com/arduino-uno.jpg",
    "location": "Rack A, Shelf 2",
    "created_at": "2025-11-08T10:30:00Z",
    "updated_at": "2025-11-08T10:30:00Z"
  }
}
```

**Error Responses:**

*400 Bad Request - Missing required field:*
```json
{
  "error": "Validation error",
  "message": "Missing required field: name"
}
```

*400 Bad Request - Invalid quantity:*
```json
{
  "error": "Validation error",
  "message": "Quantity must be a positive integer"
}
```

*403 Forbidden - Insufficient permissions:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

---

### GET /api/components/:id

Retrieve details of a specific component.

**Authentication:** Required (Any role)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Component ID

**Example Request:**
```
GET /api/components/1
```

**Success Response (200 OK):**
```json
{
  "component": {
    "id": 1,
    "name": "Arduino Uno R3",
    "type": "Microcontroller",
    "quantity": 15,
    "description": "ATmega328P based microcontroller board",
    "image_url": "https://example.com/arduino-uno.jpg",
    "location": "Rack A, Shelf 2",
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-08T14:30:00Z"
  }
}
```

**Error Responses:**

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Component with ID 1 not found"
}
```

---

### PUT /api/components/:id

Update an existing component.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Component ID

**Request Body:**
```json
{
  "name": "Arduino Uno R3 (Updated)",
  "quantity": 20,
  "description": "Updated description"
}
```

**Request Fields (all optional):**
- `name` (string): Component name
- `type` (string): Component type/category
- `quantity` (integer): Available quantity (must be non-negative)
- `description` (string): Component description
- `image_url` (string): URL to component image
- `location` (string): Storage location

**Success Response (200 OK):**
```json
{
  "message": "Component updated successfully",
  "component": {
    "id": 1,
    "name": "Arduino Uno R3 (Updated)",
    "type": "Microcontroller",
    "quantity": 20,
    "description": "Updated description",
    "image_url": "https://example.com/arduino-uno.jpg",
    "location": "Rack A, Shelf 2",
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-08T15:45:00Z"
  }
}
```

**Error Responses:**

*400 Bad Request - Invalid quantity:*
```json
{
  "error": "Validation error",
  "message": "Quantity must be a positive integer"
}
```

*403 Forbidden - Insufficient permissions:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Component with ID 1 not found"
}
```

---

### DELETE /api/components/:id

Delete a component from the inventory.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Component ID

**Example Request:**
```
DELETE /api/components/1
```

**Success Response (200 OK):**
```json
{
  "message": "Component deleted successfully"
}
```

**Error Responses:**

*400 Bad Request - Component has pending requests:*
```json
{
  "error": "Validation error",
  "message": "Cannot delete component with 3 pending request(s). Please process all pending requests first."
}
```

*403 Forbidden - Insufficient permissions:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Component with ID 1 not found"
}
```

---

## Request Endpoints

### POST /api/requests

Create a new component request.

**Authentication:** Required (Student only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "component_id": 1,
  "quantity": 2
}
```

**Request Fields:**
- `component_id` (integer, required): ID of the component to request
- `quantity` (integer, required): Quantity requested (must be positive)

**Success Response (201 Created):**
```json
{
  "message": "Request created successfully",
  "request": {
    "id": 1,
    "student_id": 5,
    "component_id": 1,
    "quantity": 2,
    "status": "Pending",
    "rejection_reason": null,
    "requested_at": "2025-11-08T10:30:00Z",
    "processed_at": null,
    "processed_by": null,
    "returned_at": null,
    "student": {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "student"
    },
    "component": {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 15
    }
  }
}
```

**Error Responses:**

*400 Bad Request - Missing field:*
```json
{
  "error": "Validation error",
  "message": "Missing required field: component_id"
}
```

*400 Bad Request - Invalid quantity:*
```json
{
  "error": "Validation error",
  "message": "Quantity must be a positive integer"
}
```

*400 Bad Request - Exceeds available quantity:*
```json
{
  "error": "Validation error",
  "message": "Requested quantity (20) exceeds available quantity (15)"
}
```

*400 Bad Request - Zero quantity component:*
```json
{
  "error": "Validation error",
  "message": "Cannot request components with zero quantity"
}
```

*403 Forbidden - Not a student:*
```json
{
  "error": "Insufficient permissions",
  "message": "Student role required for this operation"
}
```

*404 Not Found - Component not found:*
```json
{
  "error": "Not found",
  "message": "Component with ID 1 not found"
}
```

---

### GET /api/requests

Retrieve requests with role-based filtering.

**Authentication:** Required (Any role)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` (string, optional): Filter by status (Pending, Approved, Rejected, Returned)

**Role-Based Behavior:**
- **Students:** See only their own requests
- **Faculty:** See all requests from all students

**Example Request:**
```
GET /api/requests?status=Pending
```

**Success Response (200 OK):**
```json
{
  "requests": [
    {
      "id": 1,
      "student_id": 5,
      "component_id": 1,
      "quantity": 2,
      "status": "Pending",
      "rejection_reason": null,
      "requested_at": "2025-11-08T10:30:00Z",
      "processed_at": null,
      "processed_by": null,
      "returned_at": null,
      "student": {
        "id": 5,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "student"
      },
      "component": {
        "id": 1,
        "name": "Arduino Uno R3",
        "type": "Microcontroller",
        "quantity": 15
      }
    }
  ],
  "total": 1
}
```

**Error Responses:**

*400 Bad Request - Invalid status:*
```json
{
  "error": "Validation error",
  "message": "Invalid status: InvalidStatus. Valid values: Pending, Approved, Rejected, Returned"
}
```

---

### GET /api/requests/:id

Retrieve details of a specific request.

**Authentication:** Required (Any role)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Request ID

**Authorization Rules:**
- **Students:** Can only view their own requests
- **Faculty:** Can view all requests

**Example Request:**
```
GET /api/requests/1
```

**Success Response (200 OK):**
```json
{
  "request": {
    "id": 1,
    "student_id": 5,
    "component_id": 1,
    "quantity": 2,
    "status": "Approved",
    "rejection_reason": null,
    "requested_at": "2025-11-08T10:30:00Z",
    "processed_at": "2025-11-08T11:15:00Z",
    "processed_by": 2,
    "returned_at": null,
    "student": {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "student"
    },
    "component": {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 13
    },
    "processor": {
      "id": 2,
      "username": "prof_smith",
      "role": "faculty"
    }
  }
}
```

**Error Responses:**

*403 Forbidden - Student viewing another's request:*
```json
{
  "error": "Insufficient permissions",
  "message": "You can only view your own requests"
}
```

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Request with ID 1 not found"
}
```

---

### POST /api/requests/:id/approve

Approve a pending request and decrease component quantity.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Request ID

**Request Body:** None

**Example Request:**
```
POST /api/requests/1/approve
```

**Success Response (200 OK):**
```json
{
  "message": "Request approved successfully",
  "request": {
    "id": 1,
    "student_id": 5,
    "component_id": 1,
    "quantity": 2,
    "status": "Approved",
    "rejection_reason": null,
    "requested_at": "2025-11-08T10:30:00Z",
    "processed_at": "2025-11-08T11:15:00Z",
    "processed_by": 2,
    "returned_at": null,
    "student": {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "student"
    },
    "component": {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 13
    }
  }
}
```

**Error Responses:**

*400 Bad Request - Invalid status:*
```json
{
  "error": "Validation error",
  "message": "Cannot approve request with status: Approved. Only Pending requests can be approved."
}
```

*400 Bad Request - Insufficient quantity:*
```json
{
  "error": "Validation error",
  "message": "Insufficient quantity. Available: 1, Requested: 2"
}
```

*403 Forbidden - Not faculty:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Request with ID 1 not found"
}
```

---

### POST /api/requests/:id/reject

Reject a pending request without modifying component quantity.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Request ID

**Request Body (optional):**
```json
{
  "rejection_reason": "Component currently unavailable for your project type"
}
```

**Request Fields:**
- `rejection_reason` (string, optional): Reason for rejection

**Example Request:**
```
POST /api/requests/1/reject
```

**Success Response (200 OK):**
```json
{
  "message": "Request rejected successfully",
  "request": {
    "id": 1,
    "student_id": 5,
    "component_id": 1,
    "quantity": 2,
    "status": "Rejected",
    "rejection_reason": "Component currently unavailable for your project type",
    "requested_at": "2025-11-08T10:30:00Z",
    "processed_at": "2025-11-08T11:20:00Z",
    "processed_by": 2,
    "returned_at": null,
    "student": {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "student"
    },
    "component": {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 15
    }
  }
}
```

**Error Responses:**

*400 Bad Request - Invalid status:*
```json
{
  "error": "Validation error",
  "message": "Cannot reject request with status: Approved. Only Pending requests can be rejected."
}
```

*403 Forbidden - Not faculty:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Request with ID 1 not found"
}
```

---

### POST /api/requests/:id/return

Mark an approved request as returned and increase component quantity.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer, required): Request ID

**Request Body:** None

**Example Request:**
```
POST /api/requests/1/return
```

**Success Response (200 OK):**
```json
{
  "message": "Request marked as returned successfully",
  "request": {
    "id": 1,
    "student_id": 5,
    "component_id": 1,
    "quantity": 2,
    "status": "Returned",
    "rejection_reason": null,
    "requested_at": "2025-11-08T10:30:00Z",
    "processed_at": "2025-11-08T11:15:00Z",
    "processed_by": 2,
    "returned_at": "2025-11-08T16:45:00Z",
    "student": {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "student"
    },
    "component": {
      "id": 1,
      "name": "Arduino Uno R3",
      "type": "Microcontroller",
      "quantity": 15
    }
  }
}
```

**Error Responses:**

*400 Bad Request - Invalid status:*
```json
{
  "error": "Validation error",
  "message": "Cannot mark request as returned with status: Pending. Only Approved requests can be returned."
}
```

*400 Bad Request - Already returned:*
```json
{
  "error": "Validation error",
  "message": "This request has already been marked as returned"
}
```

*403 Forbidden - Not faculty:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

*404 Not Found:*
```json
{
  "error": "Not found",
  "message": "Request with ID 1 not found"
}
```

---

## Transaction Endpoints

### GET /api/transactions

Retrieve transaction audit logs with filtering options.

**Authentication:** Required (Faculty only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date` (string, optional): Filter from this date (ISO format: YYYY-MM-DD)
- `end_date` (string, optional): Filter until this date (ISO format: YYYY-MM-DD)
- `user_id` (integer, optional): Filter by user ID
- `action_type` (string, optional): Filter by action (CREATE, UPDATE, DELETE, REQUEST, APPROVE, REJECT, RETURN)
- `component_name` (string, optional): Search by component name (case-insensitive)
- `limit` (integer, optional): Maximum results (default: 100, max: 1000)
- `offset` (integer, optional): Pagination offset (default: 0)

**Example Request:**
```
GET /api/transactions?start_date=2025-11-01&action_type=APPROVE&limit=50
```

**Success Response (200 OK):**
```json
{
  "transactions": [
    {
      "id": 15,
      "user_id": 2,
      "action_type": "APPROVE",
      "entity_type": "Request",
      "entity_id": 1,
      "details": {
        "component_name": "Arduino Uno R3",
        "component_id": 1,
        "quantity": 2,
        "student_username": "john_doe",
        "faculty_username": "prof_smith",
        "previous_component_quantity": 15,
        "new_component_quantity": 13
      },
      "timestamp": "2025-11-08T11:15:00Z",
      "user": {
        "id": 2,
        "username": "prof_smith",
        "role": "faculty"
      },
      "entity": {
        "type": "Request",
        "id": 1,
        "status": "Approved"
      }
    },
    {
      "id": 14,
      "user_id": 5,
      "action_type": "REQUEST",
      "entity_type": "Request",
      "entity_id": 1,
      "details": {
        "component_name": "Arduino Uno R3",
        "component_id": 1,
        "quantity": 2,
        "student_username": "john_doe"
      },
      "timestamp": "2025-11-08T10:30:00Z",
      "user": {
        "id": 5,
        "username": "john_doe",
        "role": "student"
      },
      "entity": {
        "type": "Request",
        "id": 1,
        "status": "Approved"
      }
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

**Error Responses:**

*400 Bad Request - Invalid date format:*
```json
{
  "error": "Validation error",
  "message": "Invalid start_date format. Use ISO format: YYYY-MM-DD"
}
```

*400 Bad Request - Invalid action type:*
```json
{
  "error": "Validation error",
  "message": "Invalid action_type: INVALID. Valid values: CREATE, UPDATE, DELETE, REQUEST, APPROVE, REJECT, RETURN"
}
```

*400 Bad Request - Invalid limit:*
```json
{
  "error": "Validation error",
  "message": "Limit must be between 1 and 1000"
}
```

*403 Forbidden - Not faculty:*
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

---

## Error Codes and Messages

### HTTP Status Codes

The API uses standard HTTP status codes to indicate success or failure:

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data or validation error |
| 401 | Unauthorized | Missing, invalid, or expired authentication token |
| 403 | Forbidden | Insufficient permissions for the requested operation |
| 404 | Not Found | Requested resource does not exist |
| 500 | Internal Server Error | Unexpected server error |

### Error Response Format

All error responses follow this consistent format:

```json
{
  "error": "Error type",
  "message": "Human-readable error message"
}
```

### Common Error Types

#### Authentication Errors (401)

**Missing Token:**
```json
{
  "error": "Authentication failed",
  "message": "Missing or invalid authentication token"
}
```

**Invalid Credentials:**
```json
{
  "error": "Authentication failed",
  "message": "Invalid username or password"
}
```

**Expired Token:**
```json
{
  "error": "Authentication failed",
  "message": "Token has expired"
}
```

**Invalid Token:**
```json
{
  "error": "Authentication failed",
  "message": "Invalid or malformed token"
}
```

#### Authorization Errors (403)

**Insufficient Permissions:**
```json
{
  "error": "Insufficient permissions",
  "message": "Faculty role required for this operation"
}
```

**Student Role Required:**
```json
{
  "error": "Insufficient permissions",
  "message": "Student role required for this operation"
}
```

**Access Denied:**
```json
{
  "error": "Insufficient permissions",
  "message": "You can only view your own requests"
}
```


#### Validation Errors (400)

**Missing Required Field:**
```json
{
  "error": "Validation error",
  "message": "Missing required field: component_id"
}
```

**Missing Multiple Fields:**
```json
{
  "error": "Validation error",
  "message": "Missing required fields: username, password"
}
```

**Invalid Data Type:**
```json
{
  "error": "Validation error",
  "message": "Quantity must be a valid integer"
}
```

**Invalid Value:**
```json
{
  "error": "Validation error",
  "message": "Quantity must be a positive integer"
}
```

**Duplicate Entry:**
```json
{
  "error": "Validation error",
  "message": "Username already exists"
}
```

**Business Rule Violation:**
```json
{
  "error": "Validation error",
  "message": "Cannot delete component with 3 pending request(s). Please process all pending requests first."
}
```

**Invalid Status Transition:**
```json
{
  "error": "Validation error",
  "message": "Cannot approve request with status: Approved. Only Pending requests can be approved."
}
```

**Insufficient Quantity:**
```json
{
  "error": "Validation error",
  "message": "Requested quantity (20) exceeds available quantity (15)"
}
```

**Invalid Enum Value:**
```json
{
  "error": "Validation error",
  "message": "Role must be either \"student\" or \"faculty\""
}
```

**Invalid Date Format:**
```json
{
  "error": "Validation error",
  "message": "Invalid start_date format. Use ISO format: YYYY-MM-DD"
}
```

#### Not Found Errors (404)

**Resource Not Found:**
```json
{
  "error": "Not found",
  "message": "Component with ID 1 not found"
}
```

```json
{
  "error": "Not found",
  "message": "Request with ID 1 not found"
}
```

```json
{
  "error": "Not found",
  "message": "User not found"
}
```

#### Server Errors (500)

**Generic Server Error:**
```json
{
  "error": "Server error",
  "message": "An unexpected error occurred"
}
```

**Database Error:**
```json
{
  "error": "Failed to create component",
  "message": "Database connection error"
}
```

**Operation Failed:**
```json
{
  "error": "Failed to retrieve transactions",
  "message": "Internal server error"
}
```

---

## Example Usage Scenarios

### Scenario 1: Student Requesting a Component

**Step 1: Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**Step 2: Browse Available Components**
```bash
curl -X GET "http://localhost:5000/api/components?available_only=true" \
  -H "Authorization: Bearer <access_token>"
```

**Step 3: Submit Request**
```bash
curl -X POST http://localhost:5000/api/auth/requests \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "component_id": 1,
    "quantity": 2
  }'
```

**Step 4: Check Request Status**
```bash
curl -X GET http://localhost:5000/api/requests \
  -H "Authorization: Bearer <access_token>"
```

---

### Scenario 2: Faculty Approving a Request

**Step 1: Login as Faculty**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "prof_smith",
    "password": "FacultyPass123"
  }'
```

**Step 2: View Pending Requests**
```bash
curl -X GET "http://localhost:5000/api/requests?status=Pending" \
  -H "Authorization: Bearer <access_token>"
```

**Step 3: Approve Request**
```bash
curl -X POST http://localhost:5000/api/requests/1/approve \
  -H "Authorization: Bearer <access_token>"
```

**Step 4: View Transaction Log**
```bash
curl -X GET "http://localhost:5000/api/transactions?action_type=APPROVE" \
  -H "Authorization: Bearer <access_token>"
```

---

### Scenario 3: Faculty Managing Components

**Step 1: Add New Component**
```bash
curl -X POST http://localhost:5000/api/components \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Raspberry Pi 4",
    "type": "Single Board Computer",
    "quantity": 10,
    "description": "4GB RAM model",
    "location": "Rack B, Shelf 1"
  }'
```

**Step 2: Update Component Quantity**
```bash
curl -X PUT http://localhost:5000/api/components/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 20
  }'
```

**Step 3: Search Components**
```bash
curl -X GET "http://localhost:5000/api/components?search=Arduino&type=Microcontroller" \
  -H "Authorization: Bearer <access_token>"
```

---

## Rate Limiting

Currently, the API does not implement rate limiting. In production environments, consider implementing rate limiting to prevent abuse.

## Versioning

The current API version is v1. The API version is not included in the URL path. Future versions may introduce versioning in the URL (e.g., `/api/v2/components`).

## Support

For issues, questions, or feature requests, please refer to the project repository or contact the development team.

---

**Last Updated:** November 8, 2025  
**API Version:** 1.0.0
