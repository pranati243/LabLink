# LabLink Frontend

## Student Interface Files

### Pages
- **login.html** - Login page for all users (students and faculty)
- **student_dashboard.html** - Student dashboard for browsing components and managing requests

### JavaScript Modules
- **api.js** - API client with JWT authentication handling and endpoint wrappers
- **utils.js** - Common UI utility functions (alerts, date formatting, status badges)
- **student_dashboard.js** - Student dashboard functionality
- **faculty_dashboard.js** - Faculty dashboard functionality

## Features Implemented

### Login Page (login.html)
- Username and password input fields
- Form submission to `/api/auth/login`
- JWT token storage in localStorage
- Role-based redirect (student → student_dashboard.html, faculty → faculty_dashboard.html)
- Error message display for failed login attempts

### Student Dashboard (student_dashboard.html + student_dashboard.js)
- **Navigation Bar**: Displays username and logout button
- **Component Listing**:
  - Grid view of all available components
  - Search by component name
  - Filter by component type
  - Filter to show only available components (quantity > 0)
  - Component cards show image, name, type, description, quantity, and location
- **Request Submission**:
  - Click on component card to open request modal
  - Validates requested quantity against available quantity
  - Prevents requests for out-of-stock components
  - Submits request via POST `/api/requests`
- **My Requests Section**:
  - Table view of all user's requests
  - Shows request ID, component name, quantity, status, and date
  - Color-coded status badges (Pending=yellow, Approved=green, Rejected=red, Returned=gray)
  - View rejection reason button for rejected requests
- **Real-time Updates**:
  - Polls for request status updates every 10 seconds
  - Updates UI without page refresh
  - Shows notifications when request status changes
  - Displays rejection reasons in notifications

### API Client (api.js)
- Centralized API request handling
- Automatic JWT token inclusion in headers
- Token refresh on expiration (401 errors trigger automatic refresh and retry)
- Automatic logout on authentication failure
- Comprehensive error handling with user-friendly messages
- Wrapper functions for all endpoints:
  - **AuthAPI**: login, register
  - **ComponentAPI**: getAll, getById, create, update, delete
  - **RequestAPI**: getAll, getById, create, approve, reject, markReturned
  - **TransactionAPI**: getAll

### Utility Functions (utils.js)
- **Alert Messages**:
  - `showAlert(message, type, duration)` - Display Bootstrap alerts with auto-dismiss
  - `showSuccess(message)` - Display success message
  - `showError(message)` - Display error message
  - `showWarning(message)` - Display warning message
  - `showInfo(message)` - Display info message
- **Date Formatting**:
  - `formatDate(date)` - Format date as localized string (e.g., "Nov 8, 2025")
  - `formatDateTime(date)` - Format date and time (e.g., "Nov 8, 2025, 10:30 AM")
  - `formatRelativeTime(date)` - Format as relative time (e.g., "2 hours ago")
- **Status Formatting**:
  - `getStatusClass(status)` - Get CSS class for request status
  - `getStatusBadgeClass(status)` - Get Bootstrap badge class for status
  - `formatStatusBadge(status)` - Generate HTML for colored status badge
- **Validation**:
  - `isValidEmail(email)` - Validate email format
  - `isPositiveInteger(value)` - Validate positive integer
  - `isNonNegativeInteger(value)` - Validate non-negative integer
- **UI Helpers**:
  - `escapeHtml(text)` - Prevent XSS attacks by escaping HTML
  - `truncateText(text, maxLength)` - Truncate long text with ellipsis
  - `formatNumber(num)` - Format numbers with thousands separator
  - `debounce(func, wait)` - Debounce function calls
  - `showLoading(element, message)` - Display loading spinner
  - `showEmptyState(element, message)` - Display empty state message
  - `disableButton(button, loadingText)` - Disable button with loading state

## Usage

### Testing the Student Interface

1. **Start the backend server**:
   ```bash
   cd backend
   python app.py
   ```

2. **Open login page**:
   - Open `frontend/login.html` in a web browser
   - Or serve via a local web server

3. **Login as student**:
   - Username: `student`
   - Password: `student123`
   - (Or use credentials from seed data)

4. **Test features**:
   - Browse components
   - Use search and filters
   - Click on a component to request it
   - View your requests in "My Requests" section
   - Wait for status updates (or have faculty approve/reject via API)

## API Configuration

The frontend is configured to connect to the backend at:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

Update this in `api.js` if your backend runs on a different host/port.

## Browser Compatibility

- Requires modern browser with ES6+ support
- Uses Bootstrap 5.3.0 for UI components
- Uses localStorage for JWT token storage

## Security Notes

- JWT tokens stored in localStorage
- Automatic token refresh on expiration
- Role-based access control enforced
- XSS prevention via HTML escaping
