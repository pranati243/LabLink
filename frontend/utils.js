/**
 * Common UI Utility Functions for LabLink System
 * Provides reusable functions for displaying messages, formatting data, and handling common UI tasks
 */

/**
 * Show alert message with auto-dismiss
 * @param {string} message - The message to display
 * @param {string} type - Bootstrap alert type (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds before auto-dismiss (default: 5000)
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    
    if (!alertContainer) {
        console.error('Alert container not found. Add an element with id="alertContainer" to your HTML.');
        return;
    }
    
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-dismiss after specified duration
    if (duration > 0) {
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertElement);
                bsAlert.close();
            }
        }, duration);
    }
}

/**
 * Show success message
 * @param {string} message - The success message to display
 */
function showSuccess(message) {
    showAlert(message, 'success');
}

/**
 * Show error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    showAlert(message, 'danger');
}

/**
 * Show warning message
 * @param {string} message - The warning message to display
 */
function showWarning(message) {
    showAlert(message, 'warning');
}

/**
 * Show info message
 * @param {string} message - The info message to display
 */
function showInfo(message) {
    showAlert(message, 'info');
}

/**
 * Format date to localized date string
 * @param {string|Date} date - The date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
function formatDate(date, options = {}) {
    if (!date) return 'N/A';
    
    try {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        
        if (isNaN(dateObj.getTime())) {
            return 'Invalid Date';
        }
        
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        return dateObj.toLocaleDateString(undefined, { ...defaultOptions, ...options });
    } catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid Date';
    }
}

/**
 * Format date and time to localized string
 * @param {string|Date} date - The date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date and time string
 */
function formatDateTime(date, options = {}) {
    if (!date) return 'N/A';
    
    try {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        
        if (isNaN(dateObj.getTime())) {
            return 'Invalid Date';
        }
        
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return dateObj.toLocaleString(undefined, { ...defaultOptions, ...options });
    } catch (error) {
        console.error('Error formatting date/time:', error);
        return 'Invalid Date';
    }
}

/**
 * Format timestamp to relative time (e.g., "2 hours ago")
 * @param {string|Date} date - The date to format
 * @returns {string} Relative time string
 */
function formatRelativeTime(date) {
    if (!date) return 'N/A';
    
    try {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        
        if (isNaN(dateObj.getTime())) {
            return 'Invalid Date';
        }
        
        const now = new Date();
        const diffMs = now - dateObj;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);
        
        if (diffSec < 60) {
            return 'Just now';
        } else if (diffMin < 60) {
            return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
        } else if (diffHour < 24) {
            return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
        } else if (diffDay < 7) {
            return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
        } else {
            return formatDate(dateObj);
        }
    } catch (error) {
        console.error('Error formatting relative time:', error);
        return 'Invalid Date';
    }
}

/**
 * Get CSS class for request status
 * @param {string} status - The request status (Pending, Approved, Rejected, Returned)
 * @returns {string} CSS class name
 */
function getStatusClass(status) {
    const statusMap = {
        'Pending': 'status-pending',
        'Approved': 'status-approved',
        'Rejected': 'status-rejected',
        'Returned': 'status-returned'
    };
    return statusMap[status] || 'status-unknown';
}

/**
 * Get Bootstrap badge class for request status
 * @param {string} status - The request status
 * @returns {string} Bootstrap badge class
 */
function getStatusBadgeClass(status) {
    const statusMap = {
        'Pending': 'bg-warning text-dark',
        'Approved': 'bg-success',
        'Rejected': 'bg-danger',
        'Returned': 'bg-info'
    };
    return statusMap[status] || 'bg-secondary';
}

/**
 * Format request status with colored badge
 * @param {string} status - The request status
 * @returns {string} HTML string with formatted status badge
 */
function formatStatusBadge(status) {
    const badgeClass = getStatusBadgeClass(status);
    const statusClass = getStatusClass(status);
    return `<span class="badge badge-status ${badgeClass} ${statusClass}">${escapeHtml(status)}</span>`;
}

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} Escaped HTML string
 */
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - The function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Validate email format
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate positive integer
 * @param {any} value - Value to validate
 * @returns {boolean} True if valid positive integer
 */
function isPositiveInteger(value) {
    const num = parseInt(value);
    return !isNaN(num) && num > 0 && num === parseFloat(value);
}

/**
 * Validate non-negative integer
 * @param {any} value - Value to validate
 * @returns {boolean} True if valid non-negative integer
 */
function isNonNegativeInteger(value) {
    const num = parseInt(value);
    return !isNaN(num) && num >= 0 && num === parseFloat(value);
}

/**
 * Truncate text to specified length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength - 3) + '...';
}

/**
 * Format number with thousands separator
 * @param {number} num - Number to format
 * @returns {string} Formatted number string
 */
function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) {
        return 'N/A';
    }
    return num.toLocaleString();
}

/**
 * Confirm action with user
 * @param {string} message - Confirmation message
 * @returns {boolean} True if user confirmed
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Show loading spinner in element
 * @param {string|HTMLElement} element - Element ID or element object
 * @param {string} message - Optional loading message
 */
function showLoading(element, message = 'Loading...') {
    const el = typeof element === 'string' ? document.getElementById(element) : element;
    
    if (!el) {
        console.error('Element not found for loading spinner');
        return;
    }
    
    el.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">${escapeHtml(message)}</p>
        </div>
    `;
}

/**
 * Show empty state message in element
 * @param {string|HTMLElement} element - Element ID or element object
 * @param {string} message - Empty state message
 */
function showEmptyState(element, message = 'No data available') {
    const el = typeof element === 'string' ? document.getElementById(element) : element;
    
    if (!el) {
        console.error('Element not found for empty state');
        return;
    }
    
    el.innerHTML = `
        <div class="text-center py-4">
            <p class="text-muted">${escapeHtml(message)}</p>
        </div>
    `;
}

/**
 * Disable button with loading state
 * @param {string|HTMLElement} button - Button ID or button element
 * @param {string} loadingText - Text to show while loading
 * @returns {Function} Function to re-enable the button
 */
function disableButton(button, loadingText = 'Loading...') {
    const btn = typeof button === 'string' ? document.getElementById(button) : button;
    
    if (!btn) {
        console.error('Button not found');
        return () => {};
    }
    
    const originalText = btn.textContent;
    const wasDisabled = btn.disabled;
    
    btn.disabled = true;
    btn.textContent = loadingText;
    
    // Return function to re-enable button
    return () => {
        btn.disabled = wasDisabled;
        btn.textContent = originalText;
    };
}
