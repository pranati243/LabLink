/**
 * Faculty Dashboard JavaScript
 * Handles component management, request approval/rejection, and transaction log viewing
 */

// Global state
let allComponents = [];
let allRequests = [];
let allTransactions = [];
let componentTypes = new Set();
let componentModal;
let rejectModal;
let deleteModal;
let currentEditingComponentId = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!isAuthenticated()) {
        logout();
        return;
    }

    // Check if user is faculty
    const user = getCurrentUser();
    if (user.role !== 'faculty') {
        alert('Access denied. This page is for faculty only.');
        logout();
        return;
    }

    // Display username
    document.getElementById('username').textContent = user.username;

    // Initialize Bootstrap modals
    componentModal = new bootstrap.Modal(document.getElementById('componentModal'));
    rejectModal = new bootstrap.Modal(document.getElementById('rejectModal'));
    deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

    // Set up event listeners
    setupEventListeners();

    // Load initial data
    await loadComponents();
    await loadRequests();
    await loadTransactions();
});

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Component management
    document.getElementById('addComponentBtn').addEventListener('click', openAddComponentModal);
    document.getElementById('saveComponentBtn').addEventListener('click', saveComponent);
    document.getElementById('componentSearchInput').addEventListener('input', filterComponents);
    document.getElementById('componentTypeFilter').addEventListener('change', filterComponents);

    // Delete confirmation
    document.getElementById('confirmDeleteBtn').addEventListener('click', confirmDeleteComponent);

    // Reject request
    document.getElementById('confirmRejectBtn').addEventListener('click', confirmRejectRequest);

    // Transaction filters
    document.getElementById('startDateFilter').addEventListener('change', filterTransactions);
    document.getElementById('endDateFilter').addEventListener('change', filterTransactions);
    document.getElementById('actionTypeFilter').addEventListener('change', filterTransactions);
    document.getElementById('transactionSearchInput').addEventListener('input', filterTransactions);
}

// ==================== Component Management ====================

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
        populateComponentTypeFilter();

        // Display components
        displayComponents(allComponents);
    } catch (error) {
        console.error('Error loading components:', error);
        showAlert('Failed to load components', 'danger');
    }
}

/**
 * Populate component type filter dropdown
 */
function populateComponentTypeFilter() {
    const typeFilter = document.getElementById('componentTypeFilter');
    
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
    const searchTerm = document.getElementById('componentSearchInput').value.toLowerCase();
    const selectedType = document.getElementById('componentTypeFilter').value;

    let filtered = allComponents;

    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(comp => 
            comp.name.toLowerCase().includes(searchTerm) ||
            comp.description?.toLowerCase().includes(searchTerm) ||
            comp.location?.toLowerCase().includes(searchTerm)
        );
    }

    // Filter by type
    if (selectedType) {
        filtered = filtered.filter(comp => comp.type === selectedType);
    }

    displayComponents(filtered);
}

/**
 * Display components in table
 */
function displayComponents(components) {
    const tbody = document.getElementById('componentsTableBody');

    if (components.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No components found</td></tr>';
        return;
    }

    tbody.innerHTML = components.map(comp => {
        const imageHtml = comp.image_url ? 
            `<img src="${comp.image_url}" class="component-image-preview" alt="${comp.name}" onerror="this.src='https://via.placeholder.com/100?text=No+Image'">` :
            `<img src="https://via.placeholder.com/100?text=No+Image" class="component-image-preview" alt="No image">`;

        return `
            <tr>
                <td>${comp.id}</td>
                <td>${imageHtml}</td>
                <td>${comp.name}</td>
                <td>${comp.type}</td>
                <td><span class="badge ${comp.quantity > 0 ? 'bg-success' : 'bg-danger'}">${comp.quantity}</span></td>
                <td>${comp.location}</td>
                <td class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="openEditComponentModal(${comp.id})">
                        <i class="bi bi-pencil"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="openDeleteModal(${comp.id})">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Open modal to add new component
 */
function openAddComponentModal() {
    currentEditingComponentId = null;
    document.getElementById('componentModalTitle').textContent = 'Add Component';
    document.getElementById('componentForm').reset();
    document.getElementById('componentId').value = '';
    componentModal.show();
}

/**
 * Open modal to edit existing component
 */
function openEditComponentModal(componentId) {
    const component = allComponents.find(c => c.id === componentId);
    
    if (!component) {
        showAlert('Component not found', 'danger');
        return;
    }

    currentEditingComponentId = componentId;
    document.getElementById('componentModalTitle').textContent = 'Edit Component';
    document.getElementById('componentId').value = component.id;
    document.getElementById('componentName').value = component.name;
    document.getElementById('componentType').value = component.type;
    document.getElementById('componentQuantity').value = component.quantity;
    document.getElementById('componentDescription').value = component.description || '';
    document.getElementById('componentImageUrl').value = component.image_url || '';
    document.getElementById('componentLocation').value = component.location;
    
    componentModal.show();
}

/**
 * Save component (create or update)
 */
async function saveComponent() {
    // Get form values
    const name = document.getElementById('componentName').value.trim();
    const type = document.getElementById('componentType').value.trim();
    const quantity = parseInt(document.getElementById('componentQuantity').value);
    const description = document.getElementById('componentDescription').value.trim();
    const imageUrl = document.getElementById('componentImageUrl').value.trim();
    const location = document.getElementById('componentLocation').value.trim();

    // Validate required fields
    if (!name || !type || !location) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }

    if (isNaN(quantity) || quantity < 0) {
        showAlert('Quantity must be a positive number', 'danger');
        return;
    }

    const componentData = {
        name,
        type,
        quantity,
        description: description || null,
        image_url: imageUrl || null,
        location
    };

    try {
        // Disable save button
        const saveBtn = document.getElementById('saveComponentBtn');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        let response;
        if (currentEditingComponentId) {
            // Update existing component
            response = await ComponentAPI.update(currentEditingComponentId, componentData);
        } else {
            // Create new component
            response = await ComponentAPI.create(componentData);
        }

        if (response.message) {
            showAlert(response.message, 'success');
            componentModal.hide();
            await loadComponents();
        } else if (response.error) {
            showAlert(response.message || 'Failed to save component', 'danger');
        }
    } catch (error) {
        console.error('Error saving component:', error);
        showAlert('Failed to save component', 'danger');
    } finally {
        // Re-enable save button
        const saveBtn = document.getElementById('saveComponentBtn');
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save';
    }
}

/**
 * Open delete confirmation modal
 */
function openDeleteModal(componentId) {
    document.getElementById('deleteComponentId').value = componentId;
    deleteModal.show();
}

/**
 * Confirm and execute component deletion
 */
async function confirmDeleteComponent() {
    const componentId = parseInt(document.getElementById('deleteComponentId').value);

    try {
        // Disable delete button
        const deleteBtn = document.getElementById('confirmDeleteBtn');
        deleteBtn.disabled = true;
        deleteBtn.textContent = 'Deleting...';

        const response = await ComponentAPI.delete(componentId);

        if (response.message) {
            showAlert(response.message, 'success');
            deleteModal.hide();
            await loadComponents();
        } else if (response.error) {
            showAlert(response.message || 'Failed to delete component', 'danger');
        }
    } catch (error) {
        console.error('Error deleting component:', error);
        showAlert('Failed to delete component', 'danger');
    } finally {
        // Re-enable delete button
        const deleteBtn = document.getElementById('confirmDeleteBtn');
        deleteBtn.disabled = false;
        deleteBtn.textContent = 'Delete';
    }
}


// ==================== Request Management ====================

/**
 * Load all requests from API
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

    // Filter to show all requests (faculty can see all)
    const displayRequests = requests;

    if (displayRequests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No requests found</td></tr>';
        return;
    }

    tbody.innerHTML = displayRequests.map(req => {
        const statusBadge = formatStatusBadge(req.status);
        const requestDate = formatDate(req.requested_at);
        const studentName = req.student?.username || 'Unknown';
        const componentName = req.component?.name || 'N/A';

        let actionButtons = '';
        if (req.status === 'Pending') {
            actionButtons = `
                <button class="btn btn-sm btn-success" onclick="approveRequest(${req.id})">
                    <i class="bi bi-check-circle"></i> Approve
                </button>
                <button class="btn btn-sm btn-danger" onclick="openRejectModal(${req.id})">
                    <i class="bi bi-x-circle"></i> Reject
                </button>
            `;
        } else if (req.status === 'Approved') {
            actionButtons = `
                <button class="btn btn-sm btn-info" onclick="markAsReturned(${req.id})">
                    <i class="bi bi-arrow-return-left"></i> Mark Returned
                </button>
            `;
        } else {
            actionButtons = '<span class="text-muted">No actions</span>';
        }

        return `
            <tr>
                <td>${req.id}</td>
                <td>${studentName}</td>
                <td>${componentName}</td>
                <td>${req.quantity}</td>
                <td>${requestDate}</td>
                <td>${statusBadge}</td>
                <td class="action-buttons">${actionButtons}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Approve a request
 */
async function approveRequest(requestId) {
    if (!confirm('Are you sure you want to approve this request?')) {
        return;
    }

    try {
        const response = await RequestAPI.approve(requestId);

        if (response.message) {
            showAlert(response.message, 'success');
            await loadRequests();
            await loadComponents(); // Refresh components to update quantities
        } else if (response.error) {
            showAlert(response.message || 'Failed to approve request', 'danger');
        }
    } catch (error) {
        console.error('Error approving request:', error);
        showAlert('Failed to approve request', 'danger');
    }
}

/**
 * Open reject modal
 */
function openRejectModal(requestId) {
    document.getElementById('rejectRequestId').value = requestId;
    document.getElementById('rejectionReason').value = '';
    rejectModal.show();
}

/**
 * Confirm and execute request rejection
 */
async function confirmRejectRequest() {
    const requestId = parseInt(document.getElementById('rejectRequestId').value);
    const rejectionReason = document.getElementById('rejectionReason').value.trim();

    try {
        // Disable reject button
        const rejectBtn = document.getElementById('confirmRejectBtn');
        rejectBtn.disabled = true;
        rejectBtn.textContent = 'Rejecting...';

        const response = await RequestAPI.reject(requestId, rejectionReason || null);

        if (response.message) {
            showAlert(response.message, 'success');
            rejectModal.hide();
            await loadRequests();
        } else if (response.error) {
            showAlert(response.message || 'Failed to reject request', 'danger');
        }
    } catch (error) {
        console.error('Error rejecting request:', error);
        showAlert('Failed to reject request', 'danger');
    } finally {
        // Re-enable reject button
        const rejectBtn = document.getElementById('confirmRejectBtn');
        rejectBtn.disabled = false;
        rejectBtn.textContent = 'Reject Request';
    }
}

/**
 * Mark request as returned
 */
async function markAsReturned(requestId) {
    if (!confirm('Are you sure you want to mark this request as returned?')) {
        return;
    }

    try {
        const response = await RequestAPI.markReturned(requestId);

        if (response.message) {
            showAlert(response.message, 'success');
            await loadRequests();
            await loadComponents(); // Refresh components to update quantities
        } else if (response.error) {
            showAlert(response.message || 'Failed to mark as returned', 'danger');
        }
    } catch (error) {
        console.error('Error marking as returned:', error);
        showAlert('Failed to mark as returned', 'danger');
    }
}


// ==================== Transaction Log ====================

/**
 * Load all transactions from API
 */
async function loadTransactions() {
    try {
        const filters = getTransactionFilters();
        const data = await TransactionAPI.getAll(filters);
        allTransactions = data.transactions || [];
        displayTransactions(allTransactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
        showAlert('Failed to load transactions', 'danger');
    }
}

/**
 * Get transaction filters from form inputs
 */
function getTransactionFilters() {
    const filters = {};

    const startDate = document.getElementById('startDateFilter').value;
    const endDate = document.getElementById('endDateFilter').value;
    const actionType = document.getElementById('actionTypeFilter').value;
    const search = document.getElementById('transactionSearchInput').value.trim();

    if (startDate) filters.start_date = startDate;
    if (endDate) filters.end_date = endDate;
    if (actionType) filters.action_type = actionType;
    if (search) filters.search = search;

    return filters;
}

/**
 * Filter transactions based on current filter values
 */
async function filterTransactions() {
    await loadTransactions();
}

/**
 * Display transactions in table
 */
function displayTransactions(transactions) {
    const tbody = document.getElementById('transactionsTableBody');

    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No transactions found</td></tr>';
        return;
    }

    tbody.innerHTML = transactions.map(txn => {
        const timestamp = formatDateTime(txn.timestamp);
        const username = txn.user?.username || 'Unknown';
        const details = formatTransactionDetails(txn);

        return `
            <tr>
                <td>${txn.id}</td>
                <td>${timestamp}</td>
                <td>${username}</td>
                <td><span class="badge bg-primary">${txn.action_type}</span></td>
                <td>${txn.entity_type}</td>
                <td>${txn.entity_id}</td>
                <td><small>${details}</small></td>
            </tr>
        `;
    }).join('');
}

/**
 * Format transaction details for display
 */
function formatTransactionDetails(txn) {
    if (!txn.details) {
        return 'N/A';
    }

    try {
        const details = typeof txn.details === 'string' ? JSON.parse(txn.details) : txn.details;
        
        // Format based on action type
        switch (txn.action_type) {
            case 'CREATE':
                return `Created: ${details.name || 'N/A'}`;
            
            case 'UPDATE':
                if (details.changes) {
                    const changes = Object.entries(details.changes)
                        .map(([key, value]) => `${key}: ${value.old} → ${value.new}`)
                        .join(', ');
                    return changes || 'Updated';
                }
                return 'Updated';
            
            case 'DELETE':
                return `Deleted: ${details.name || 'N/A'}`;
            
            case 'REQUEST':
                return `Requested ${details.quantity || 'N/A'} of ${details.component_name || 'N/A'}`;
            
            case 'APPROVE':
                return `Approved request #${details.request_id || 'N/A'}`;
            
            case 'REJECT':
                const reason = details.rejection_reason ? ` (${details.rejection_reason})` : '';
                return `Rejected request #${details.request_id || 'N/A'}${reason}`;
            
            case 'RETURN':
                return `Returned ${details.quantity || 'N/A'} of ${details.component_name || 'N/A'}`;
            
            default:
                return JSON.stringify(details).substring(0, 100);
        }
    } catch (error) {
        console.error('Error formatting transaction details:', error);
        return 'Error formatting details';
    }
}

// ==================== Utility Functions ====================
// Note: Common utility functions are now in utils.js
