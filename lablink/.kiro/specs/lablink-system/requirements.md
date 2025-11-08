# Requirements Document

## Introduction

LabLink is a Laboratory Component Management System designed to help educational institutions manage electronic components inventory (Arduino boards, sensors, modules, cables). The system enables students to view and request components while allowing faculty to manage inventory, approve requests, and track all transactions. The system is built for beginner-level deployment using Docker containers and optional AWS cloud deployment without Kubernetes.

## Glossary

- **LabLink System**: The complete laboratory component management application
- **Student User**: A user with student role who can view components and submit requests
- **Faculty User**: A user with faculty role who can manage components and approve/reject requests
- **Component**: An electronic item in the laboratory inventory (e.g., Arduino board, sensor, cable)
- **Request**: A student's request to borrow one or more components
- **Transaction Log**: An audit trail recording all system actions
- **JWT**: JSON Web Token used for authentication
- **Docker Container**: A containerized deployment unit for the application
- **AWS EC2**: Amazon Web Services Elastic Compute Cloud instance
- **AWS RDS**: Amazon Web Services Relational Database Service

## Requirements

### Requirement 1

**User Story:** As a student user, I want to authenticate with my credentials, so that I can access the system securely

#### Acceptance Criteria

1. WHEN a student user submits valid credentials, THE LabLink System SHALL generate a JWT token and grant access to the student dashboard
2. WHEN a user submits invalid credentials, THE LabLink System SHALL reject the login attempt and display an error message
3. THE LabLink System SHALL hash all passwords using a secure hashing algorithm before storing them in the database
4. WHEN a JWT token expires, THE LabLink System SHALL require the user to re-authenticate
5. THE LabLink System SHALL validate JWT tokens on every protected API request

### Requirement 2

**User Story:** As a faculty user, I want to authenticate with my credentials, so that I can access administrative functions

#### Acceptance Criteria

1. WHEN a faculty user submits valid credentials, THE LabLink System SHALL generate a JWT token and grant access to the faculty dashboard
2. THE LabLink System SHALL restrict faculty-only operations to users with faculty role
3. WHEN a student user attempts to access faculty operations, THE LabLink System SHALL deny access and return an authorization error
4. THE LabLink System SHALL include the user role in the JWT token payload

### Requirement 3

**User Story:** As a faculty user, I want to add new components to the inventory, so that students can request them

#### Acceptance Criteria

1. WHEN a faculty user submits a new component with required fields, THE LabLink System SHALL create the component record in the database
2. THE LabLink System SHALL require the following fields for each component: name, type, quantity, description, location
3. THE LabLink System SHALL accept an optional image_url field for component visual reference
4. WHEN a component is created, THE LabLink System SHALL record the action in the transaction log
5. THE LabLink System SHALL validate that quantity is a positive integer before creating the component

### Requirement 4

**User Story:** As a faculty user, I want to update existing components, so that I can maintain accurate inventory information

#### Acceptance Criteria

1. WHEN a faculty user submits updated component information, THE LabLink System SHALL modify the component record in the database
2. THE LabLink System SHALL validate all updated fields before applying changes
3. WHEN a component is updated, THE LabLink System SHALL record the action in the transaction log with old and new values
4. THE LabLink System SHALL prevent quantity from being set to a negative value

### Requirement 5

**User Story:** As a faculty user, I want to delete components from the inventory, so that I can remove obsolete or damaged items

#### Acceptance Criteria

1. WHEN a faculty user requests to delete a component, THE LabLink System SHALL remove the component record from the database
2. WHEN a component is deleted, THE LabLink System SHALL record the action in the transaction log
3. WHEN a component with pending requests is deleted, THE LabLink System SHALL reject the deletion and display an error message
4. THE LabLink System SHALL require confirmation before deleting a component

### Requirement 6

**User Story:** As a student user, I want to view all available components, so that I can see what I can request

#### Acceptance Criteria

1. WHEN a student user accesses the component list, THE LabLink System SHALL display all components with quantity greater than zero
2. THE LabLink System SHALL display component name, type, quantity, description, image, and location for each item
3. THE LabLink System SHALL allow filtering components by type or category
4. THE LabLink System SHALL allow searching components by name
5. THE LabLink System SHALL update the component list in real-time when quantities change

### Requirement 7

**User Story:** As a student user, I want to request components, so that I can use them for my projects

#### Acceptance Criteria

1. WHEN a student user submits a component request, THE LabLink System SHALL create a request record with status "Pending"
2. THE LabLink System SHALL validate that the requested quantity does not exceed available quantity
3. WHEN a request is created, THE LabLink System SHALL record the action in the transaction log
4. THE LabLink System SHALL associate each request with the requesting student user
5. THE LabLink System SHALL prevent requests for components with zero quantity

### Requirement 8

**User Story:** As a student user, I want to view my request status, so that I know if my request was approved or rejected

#### Acceptance Criteria

1. WHEN a student user accesses their requests page, THE LabLink System SHALL display all requests submitted by that student
2. THE LabLink System SHALL display request status as "Pending", "Approved", "Rejected", or "Returned"
3. THE LabLink System SHALL display the component name, requested quantity, request date, and status for each request
4. THE LabLink System SHALL update request status in real-time when faculty takes action
5. WHEN a request status changes, THE LabLink System SHALL display the updated status without requiring page refresh

### Requirement 9

**User Story:** As a faculty user, I want to approve student requests, so that students can receive the components they need

#### Acceptance Criteria

1. WHEN a faculty user approves a request, THE LabLink System SHALL update the request status to "Approved"
2. WHEN a request is approved, THE LabLink System SHALL decrease the component quantity by the requested amount
3. WHEN a request is approved, THE LabLink System SHALL record the action in the transaction log
4. THE LabLink System SHALL prevent approval if the available quantity is less than the requested quantity
5. THE LabLink System SHALL display the approving faculty member in the transaction log

### Requirement 10

**User Story:** As a faculty user, I want to reject student requests, so that I can deny inappropriate or unavailable requests

#### Acceptance Criteria

1. WHEN a faculty user rejects a request, THE LabLink System SHALL update the request status to "Rejected"
2. WHEN a request is rejected, THE LabLink System SHALL not modify the component quantity
3. WHEN a request is rejected, THE LabLink System SHALL record the action in the transaction log
4. THE LabLink System SHALL allow faculty to provide a rejection reason
5. THE LabLink System SHALL display the rejection reason to the student user

### Requirement 11

**User Story:** As a faculty user, I want to mark components as returned, so that inventory quantities are updated when students return items

#### Acceptance Criteria

1. WHEN a faculty user marks a request as returned, THE LabLink System SHALL update the request status to "Returned"
2. WHEN a request is marked as returned, THE LabLink System SHALL increase the component quantity by the returned amount
3. WHEN a request is marked as returned, THE LabLink System SHALL record the action in the transaction log
4. THE LabLink System SHALL only allow marking approved requests as returned
5. THE LabLink System SHALL prevent marking the same request as returned multiple times

### Requirement 12

**User Story:** As a faculty user, I want to view the complete transaction log, so that I can audit all system activities

#### Acceptance Criteria

1. WHEN a faculty user accesses the transaction log, THE LabLink System SHALL display all recorded actions in chronological order
2. THE LabLink System SHALL record the following information for each transaction: timestamp, user, action type, component, and details
3. THE LabLink System SHALL allow filtering the transaction log by date range, user, or action type
4. THE LabLink System SHALL allow searching the transaction log by component name
5. THE LabLink System SHALL display the most recent transactions first

### Requirement 13

**User Story:** As a system administrator, I want to deploy the application using Docker containers, so that deployment is consistent and reproducible

#### Acceptance Criteria

1. THE LabLink System SHALL provide a Dockerfile that builds the backend application container
2. THE LabLink System SHALL provide a docker-compose.yml file that orchestrates backend and database containers
3. WHEN the docker-compose command is executed, THE LabLink System SHALL start all required services
4. THE LabLink System SHALL expose the backend API on a configurable port
5. THE LabLink System SHALL use environment variables for database connection configuration

### Requirement 14

**User Story:** As a system administrator, I want to deploy the application on AWS EC2, so that it is accessible over the internet

#### Acceptance Criteria

1. THE LabLink System SHALL provide deployment documentation for AWS EC2 instances
2. THE LabLink System SHALL support AWS RDS as the database backend
3. THE LabLink System SHALL use environment variables for AWS-specific configuration
4. THE LabLink System SHALL provide security group configuration instructions for EC2 instances
5. THE LabLink System SHALL support optional S3 integration for component images

### Requirement 15

**User Story:** As a developer, I want comprehensive API documentation, so that I can understand and integrate with the system

#### Acceptance Criteria

1. THE LabLink System SHALL provide documentation for all REST API endpoints
2. THE LabLink System SHALL document request and response formats for each endpoint
3. THE LabLink System SHALL document authentication requirements for protected endpoints
4. THE LabLink System SHALL provide example API requests and responses
5. THE LabLink System SHALL document all error codes and error messages
