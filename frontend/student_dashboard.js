/**
 * Student Dashboard JavaScript
 * Handles component browsing, request submission, and request status viewing
 */

// Global state
let allComponents = [];
let allRequests = [];
let componentTypes = new Set();
let requestModal;
let pollingInterval;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!isAuthenticated()) {
        logout();
        return;
    }

    // Check if user is a student
    const user = getCurrentUser();
    if (user.role !== 'student') {
        alert('Access denied. This page is for students only.');
        logout();
        return;
    }

    // Display username
    document.getElementById('username').textContent = user.username;

    // Initialize Bootstrap modal
    requestModal = new bootstrap.Modal(document.getElementById('requestModal'));

    // Set up event listeners
    setupEventListeners();

    // Load initial data
    await loadComponents();
    await loadRequests();

    // Start real-time polling for request status updates
    startPolling();
});

/**
 * Start periodic polling for request status updates
 */
function startPolling() {
    // Poll every 10 seconds
    pollingInterval = setInterval(async () => {
        await updateRequestStatus();
    }, 10000);
}

/**
 * Stop polling (cleanup)
 */
function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

/**
 * Update request status without full page refresh
 */
async function updateRequestStatus() {
    try {
        const data = await RequestAPI.getAll();
        const newRequests = data.requests || [];

        // Check for status changes
        const statusChanges = detectStatusChanges(allRequests, newRequests);

        // Update global state
        allRequests = newRequests;

        // Display updated requests
        displayRequests(allRequests);

        // Show notifications for status changes
        statusChanges.forEach(change => {
            showStatusChangeNotification(change);
        });

        // Also refresh components in case quantities changed
        await loadComponents();
    } catch (error) {
        console.error('Error updating request status:', error);
        // Don't show error alert for polling failures to avoid spam
    }
}

/**
 * Detect status changes between old and new requests
 */
function detectStatusChanges(oldRequests, newRequests) {
    const changes = [];

    newRequests.forEach(newReq => {
        const oldReq = oldRequests.find(r => r.id === newReq.id);
        
        if (oldReq && oldReq.status !== newReq.status) {
            changes.push({
                requestId: newReq.id,
                componentName: newReq.component?.name || 'Unknown',
                oldStatus: oldReq.status,
                newStatus: newReq.status,
                rejectionReason: newReq.rejection_reason
            });
        }
    });

    return changes;
}

/**
 * Show notification for status change
 */
function showStatusChangeNotification(change) {
    let message = `Request #${change.requestId} for ${change.componentName} has been ${change.newStatus.toLowerCase()}`;
    let type = 'info';

    if (change.newStatus === 'Approved') {
        type = 'success';
        message += '. You can now collect the component.';
    } else if (change.newStatus === 'Rejected') {
        type = 'danger';
        if (change.rejectionReason) {
            message += `. Reason: ${change.rejectionReason}`;
        }
    } else if (change.newStatus === 'Returned') {
        type = 'info';
        message += '. Thank you for returning the component.';
    }

    showAlert(message, type);
}

// Clean up polling when page is unloaded
window.addEventListener('beforeunload', () => {
    stopPolling();
});

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Search input
    document.getElementById('searchInput').addEventListener('input', filterComponents);

    // Type filter
    document.getElementById('typeFilter').addEventListener('change', filterComponents);

    // Available only filter
    document.getElementById('availableOnlyFilter').addEventListener('change', filterComponents);

    // Submit request button
    document.getElementById('submitRequestBtn').addEventListener('click', submitRequest);
}

/**
 * Load all components from API
 */
async function loadComponents() {
    try {
        const data = await ComponentAPI.getAll();
        allComponents = data.components || [];

        // Extract unique component types
        componentTypes.clear();
        allComponents.forEach(comp => componentTypes.add(comp.type));

        // Populate type filter dropdown
        populateTypeFilter();

        // Display components
        displayComponents(allComponents);
    } catch (error) {
        console.error('Error loading components:', error);
        showAlert('Failed to load components', 'danger');
    }
}

/**
 * Populate type filter dropdown
 */
function populateTypeFilter() {
    const typeFilter = document.getElementById('typeFilter');
    
    // Clear existing options except "All Types"
    typeFilter.innerHTML = '<option value="">All Types</option>';

    // Add type options
    Array.from(componentTypes).sort().forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeFilter.appendChild(option);
    });
}

/**
 * Filter components based on search and filters
 */
function filterComponents() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedType = document.getElementById('typeFilter').value;
    const availableOnly = document.getElementById('availableOnlyFilter').checked;

    let filtered = allComponents;

    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(comp => 
            comp.name.toLowerCase().includes(searchTerm) ||
            comp.description?.toLowerCase().includes(searchTerm)
        );
    }

    // Filter by type
    if (selectedType) {
        filtered = filtered.filter(comp => comp.type === selectedType);
    }

    // Filter by availability
    if (availableOnly) {
        filtered = filtered.filter(comp => comp.quantity > 0);
    }

    displayComponents(filtered);
}

/**
 * Display components in grid
 */
function displayComponents(components) {
    const grid = document.getElementById('componentsGrid');

    if (components.length === 0) {
        grid.innerHTML = '<div class="col-12"><p class="text-center text-muted">No components found</p></div>';
        return;
    }

    grid.innerHTML = components.map(comp => `
        <div class="col-md-4 col-lg-3 mb-4">
            <div class="card component-card h-100" onclick="openRequestModal(${comp.id})">
                ${comp.image_url ? 
                    `<img src="${comp.image_url}" class="component-image" alt="${comp.name}" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">` :
                    `<img src="https://via.placeholder.com/300x200?text=${encodeURIComponent(comp.name)}" class="component-image" alt="${comp.name}">`
                }
                <div class="card-body">
                    <h6 class="card-title">${comp.name}</h6>
                    <p class="card-text text-muted small">${comp.type}</p>
                    <p class="card-text small">${comp.description || 'No description'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge ${comp.quantity > 0 ? 'bg-success' : 'bg-danger'}">
                            ${comp.quantity} available
                        </span>
                        <small class="text-muted">
                            <i class="bi bi-geo-alt"></i> ${comp.location}
                        </small>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Open request modal for a component
 */
function openRequestModal(componentId) {
    const component = allComponents.find(c => c.id === componentId);
    
    if (!component) {
        showAlert('Component not found', 'danger');
        return;
    }

    if (component.quantity === 0) {
        showAlert('This component is currently out of stock', 'warning');
        return;
    }

    // Populate modal fields
    document.getElementById('requestComponentId').value = component.id;
    document.getElementById('requestComponentName').value = component.name;
    document.getElementById('requestAvailableQty').value = component.quantity;
    document.getElementById('requestQuantity').value = 1;
    document.getElementById('requestQuantity').max = component.quantity;

    // Show modal
    requestModal.show();
}

/**
 * Submit component request
 */
async function submitRequest() {
    const componentId = parseInt(document.getElementById('requestComponentId').value);
    const quantity = parseInt(document.getElementById('requestQuantity').value);
    const availableQty = parseInt(document.getElementById('requestAvailableQty').value);

    // Validate quantity
    if (!quantity || quantity <= 0) {
        showAlert('Please enter a valid quantity', 'danger');
        return;
    }

    if (quantity > availableQty) {
        showAlert(`Requested quantity exceeds available quantity (${availableQty})`, 'danger');
        return;
    }

    try {
        // Disable submit button
        const submitBtn = document.getElementById('submitRequestBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        // Submit request
        const response = await RequestAPI.create({
            component_id: componentId,
            quantity: quantity
        });

        if (response.message) {
            showAlert(response.message, 'success');
            requestModal.hide();
            
            // Reload data
            await loadComponents();
            await loadRequests();
        } else if (response.error) {
            showAlert(response.message || 'Failed to submit request', 'danger');
        }
    } catch (error) {
        console.error('Error submitting request:', error);
        showAlert('Failed to submit request', 'danger');
    } finally {
        // Re-enable submit button
        const submitBtn = document.getElementById('submitRequestBtn');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Request';
    }
}

/**
 * Load user's requests from API
 */
async function loadRequests() {
    try {
        const data = await RequestAPI.getAll();
        allRequests = data.requests || [];
        displayRequests(allRequests);
    } catch (error) {
        console.error('Error loading requests:', error);
        showAlert('Failed to load requests', 'danger');
    }
}

/**
 * Display requests in table
 */
function displayRequests(requests) {
    const tbody = document.getElementById('requestsTableBody');

    if (requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No requests found</td></tr>';
        return;
    }

    tbody.innerHTML = requests.map(req => {
        const statusClass = getStatusClass(req.status);
        const statusBadge = formatStatusBadge(req.status);
        const requestDate = formatDate(req.requested_at);
        
        let details = '';
        if (req.status === 'Rejected' && req.rejection_reason) {
            details = `<button class="btn btn-sm btn-outline-secondary" onclick="showRejectionReason('${escapeHtml(req.rejection_reason)}')">
                <i class="bi bi-info-circle"></i>
            </button>`;
        }

        return `
            <tr>
                <td>${req.id}</td>
                <td>${req.component?.name || 'N/A'}</td>
                <td>${req.quantity}</td>
                <td>${statusBadge}</td>
                <td>${requestDate}</td>
                <td>${details}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Show rejection reason in alert
 */
function showRejectionReason(reason) {
    showInfo(`Rejection Reason: ${reason}`);
}
