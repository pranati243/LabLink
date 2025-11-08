/**
 * API Client for LabLink System
 * Handles all API requests with JWT authentication
 */

const API_BASE_URL = 'http://localhost:5000';

/**
 * Get JWT token from localStorage
 */
function getAccessToken() {
    return localStorage.getItem('access_token');
}

/**
 * Get refresh token from localStorage
 */
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Clear authentication data and redirect to login
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!getAccessToken();
}

/**
 * Make an authenticated API request
 */
async function apiRequest(endpoint, options = {}) {
    const token = getAccessToken();
    
    if (!token) {
        logout();
        throw new Error('Not authenticated');
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        // Handle token expiration
        if (response.status === 401) {
            // Try to refresh token
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Retry the request with new token
                headers.Authorization = `Bearer ${getAccessToken()}`;
                const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
                    ...options,
                    headers
                });
                return retryResponse;
            } else {
                logout();
                throw new Error('Session expired');
            }
        }

        // Handle other HTTP errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`;
            throw new Error(errorMessage);
        }

        return response;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

/**
 * Refresh access token using refresh token
 */
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${refreshToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

/**
 * API Methods
 */

// Authentication API
const AuthAPI = {
    /**
     * Login with username and password
     */
    async login(username, password) {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Login failed');
        }

        const data = await response.json();
        
        // Store tokens and user info
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        return data;
    },

    /**
     * Register new user
     */
    async register(username, email, password, role = 'student') {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password, role })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Registration failed');
        }

        return response.json();
    }
};

// Component API
const ComponentAPI = {
    /**
     * Get all components with optional filters
     */
    async getAll(filters = {}) {
        const params = new URLSearchParams();
        if (filters.type) params.append('type', filters.type);
        if (filters.search) params.append('search', filters.search);
        if (filters.available_only !== undefined) params.append('available_only', filters.available_only);

        const queryString = params.toString();
        const endpoint = `/api/components${queryString ? '?' + queryString : ''}`;
        
        const response = await apiRequest(endpoint);
        return response.json();
    },

    /**
     * Get component by ID
     */
    async getById(id) {
        const response = await apiRequest(`/api/components/${id}`);
        return response.json();
    },

    /**
     * Create new component (Faculty only)
     */
    async create(componentData) {
        const response = await apiRequest('/api/components', {
            method: 'POST',
            body: JSON.stringify(componentData)
        });
        return response.json();
    },

    /**
     * Update component (Faculty only)
     */
    async update(id, componentData) {
        const response = await apiRequest(`/api/components/${id}`, {
            method: 'PUT',
            body: JSON.stringify(componentData)
        });
        return response.json();
    },

    /**
     * Delete component (Faculty only)
     */
    async delete(id) {
        const response = await apiRequest(`/api/components/${id}`, {
            method: 'DELETE'
        });
        return response.json();
    }
};

// Request API
const RequestAPI = {
    /**
     * Get all requests (filtered by role)
     */
    async getAll(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);

        const queryString = params.toString();
        const endpoint = `/api/requests${queryString ? '?' + queryString : ''}`;
        
        const response = await apiRequest(endpoint);
        return response.json();
    },

    /**
     * Get request by ID
     */
    async getById(id) {
        const response = await apiRequest(`/api/requests/${id}`);
        return response.json();
    },

    /**
     * Create new request (Student only)
     */
    async create(requestData) {
        const response = await apiRequest('/api/requests', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
        return response.json();
    },

    /**
     * Approve request (Faculty only)
     */
    async approve(id) {
        const response = await apiRequest(`/api/requests/${id}/approve`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * Reject request (Faculty only)
     */
    async reject(id, rejectionReason = null) {
        const response = await apiRequest(`/api/requests/${id}/reject`, {
            method: 'POST',
            body: JSON.stringify({ rejection_reason: rejectionReason })
        });
        return response.json();
    },

    /**
     * Mark request as returned (Faculty only)
     */
    async markReturned(id) {
        const response = await apiRequest(`/api/requests/${id}/return`, {
            method: 'POST'
        });
        return response.json();
    }
};

// Transaction API
const TransactionAPI = {
    /**
     * Get all transactions (Faculty only)
     */
    async getAll(filters = {}) {
        const params = new URLSearchParams();
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        if (filters.user_id) params.append('user_id', filters.user_id);
        if (filters.action_type) params.append('action_type', filters.action_type);
        if (filters.search) params.append('search', filters.search);

        const queryString = params.toString();
        const endpoint = `/api/transactions${queryString ? '?' + queryString : ''}`;
        
        const response = await apiRequest(endpoint);
        return response.json();
    }
};
