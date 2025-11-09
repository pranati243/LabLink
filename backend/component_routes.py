"""
Component management routes for LabLink System
Handles CRUD operations for laboratory components
"""
from flask import Blueprint, request, jsonify
from backend.models import db, Component, Request, RequestStatus, Transaction, ActionType, EntityType
from backend.middleware import jwt_required, role_required
from backend.auth import get_current_user
from sqlalchemy import or_


component_bp = Blueprint('components', __name__, url_prefix='/api/components')


def validate_component_data(data, is_update=False):
    """
    Validate component data for creation or update
    
    Args:
        data: Dictionary containing component data
        is_update: Boolean indicating if this is an update operation
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Required fields for creation
    if not is_update:
        required_fields = ['name', 'type', 'quantity', 'location']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
    
    # Validate quantity if provided
    if 'quantity' in data:
        try:
            quantity = int(data['quantity'])
            if quantity < 0:
                return False, "Quantity must be a positive integer"
        except (ValueError, TypeError):
            return False, "Quantity must be a valid integer"
    
    return True, None


def log_component_transaction(user, action_type, component, details=None):
    """
    Log a component transaction to the audit log
    
    Args:
        user: User performing the action
        action_type: ActionType enum value
        component: Component being acted upon
        details: Optional dictionary with additional details
    """
    transaction = Transaction(
        user_id=user.id,
        action_type=action_type,
        entity_type=EntityType.Component,
        entity_id=component.id,
        details=details or {}
    )
    db.session.add(transaction)


@component_bp.route('', methods=['GET'])
@jwt_required
def get_components():
    """
    Get all components with optional filtering and search
    
    Query Parameters:
        - type: Filter by component type
        - search: Search by component name (case-insensitive)
        - available_only: Show only components with quantity > 0 (boolean)
        
    Returns:
        200: List of components
    """
    try:
        query = Component.query
        
        # Filter by type
        component_type = request.args.get('type')
        if component_type:
            query = query.filter(Component.type == component_type)
        
        # Search by name
        search_term = request.args.get('search')
        if search_term:
            query = query.filter(Component.name.ilike(f'%{search_term}%'))
        
        # Filter available only
        available_only = request.args.get('available_only', '').lower() == 'true'
        if available_only:
            query = query.filter(Component.quantity > 0)
        
        # Execute query
        components = query.order_by(Component.name).all()
        
        return jsonify({
            'components': [comp.to_dict() for comp in components],
            'total': len(components)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve components',
            'message': str(e)
        }), 500


@component_bp.route('', methods=['POST'])
@jwt_required
@role_required('faculty')
def create_component():
    """
    Create a new component (Faculty only)
    
    Request Body:
        - name: Component name (required)
        - type: Component type (required)
        - quantity: Available quantity (required, positive integer)
        - description: Component description (optional)
        - image_url: URL to component image (optional)
        - location: Storage location (required)
        
    Returns:
        201: Component created successfully
        400: Validation error
        403: Insufficient permissions
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Request body is required'
            }), 400
        
        # Validate component data
        is_valid, error_message = validate_component_data(data)
        if not is_valid:
            return jsonify({
                'error': 'Validation error',
                'message': error_message
            }), 400
        
        # Create new component
        component = Component(
            name=data['name'],
            type=data['type'],
            quantity=int(data['quantity']),
            description=data.get('description'),
            image_url=data.get('image_url'),
            location=data['location']
        )
        
        db.session.add(component)
        db.session.flush()  # Get component ID before commit
        
        # Log transaction
        user = get_current_user()
        log_component_transaction(
            user,
            ActionType.CREATE,
            component,
            details={
                'name': component.name,
                'type': component.type,
                'quantity': component.quantity,
                'location': component.location
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Component created successfully',
            'component': component.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create component',
            'message': str(e)
        }), 500


@component_bp.route('/<int:component_id>', methods=['GET'])
@jwt_required
def get_component(component_id):
    """
    Get component details by ID
    
    Args:
        component_id: Component ID
        
    Returns:
        200: Component details
        404: Component not found
    """
    try:
        component = Component.query.get(component_id)
        
        if not component:
            return jsonify({
                'error': 'Not found',
                'message': f'Component with ID {component_id} not found'
            }), 404
        
        return jsonify({
            'component': component.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve component',
            'message': str(e)
        }), 500


@component_bp.route('/<int:component_id>', methods=['PUT'])
@jwt_required
@role_required('faculty')
def update_component(component_id):
    """
    Update an existing component (Faculty only)
    
    Args:
        component_id: Component ID
        
    Request Body:
        - name: Component name (optional)
        - type: Component type (optional)
        - quantity: Available quantity (optional, positive integer)
        - description: Component description (optional)
        - image_url: URL to component image (optional)
        - location: Storage location (optional)
        
    Returns:
        200: Component updated successfully
        400: Validation error
        403: Insufficient permissions
        404: Component not found
    """
    try:
        component = Component.query.get(component_id)
        
        if not component:
            return jsonify({
                'error': 'Not found',
                'message': f'Component with ID {component_id} not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Request body is required'
            }), 400
        
        # Validate component data
        is_valid, error_message = validate_component_data(data, is_update=True)
        if not is_valid:
            return jsonify({
                'error': 'Validation error',
                'message': error_message
            }), 400
        
        # Store old values for transaction log
        old_values = {
            'name': component.name,
            'type': component.type,
            'quantity': component.quantity,
            'description': component.description,
            'image_url': component.image_url,
            'location': component.location
        }
        
        # Update component fields
        if 'name' in data:
            component.name = data['name']
        if 'type' in data:
            component.type = data['type']
        if 'quantity' in data:
            component.quantity = int(data['quantity'])
        if 'description' in data:
            component.description = data['description']
        if 'image_url' in data:
            component.image_url = data['image_url']
        if 'location' in data:
            component.location = data['location']
        
        # Store new values for transaction log
        new_values = {
            'name': component.name,
            'type': component.type,
            'quantity': component.quantity,
            'description': component.description,
            'image_url': component.image_url,
            'location': component.location
        }
        
        # Log transaction with old and new values
        user = get_current_user()
        log_component_transaction(
            user,
            ActionType.UPDATE,
            component,
            details={
                'old_values': old_values,
                'new_values': new_values
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Component updated successfully',
            'component': component.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update component',
            'message': str(e)
        }), 500


@component_bp.route('/<int:component_id>', methods=['DELETE'])
@jwt_required
@role_required('faculty')
def delete_component(component_id):
    """
    Delete a component (Faculty only)
    
    Prevents deletion if component has pending requests
    
    Args:
        component_id: Component ID
        
    Returns:
        200: Component deleted successfully
        400: Component has pending requests
        403: Insufficient permissions
        404: Component not found
    """
    try:
        component = Component.query.get(component_id)
        
        if not component:
            return jsonify({
                'error': 'Not found',
                'message': f'Component with ID {component_id} not found'
            }), 404
        
        # Check for pending requests
        pending_requests = Request.query.filter_by(
            component_id=component_id,
            status=RequestStatus.PENDING
        ).count()
        
        if pending_requests > 0:
            return jsonify({
                'error': 'Validation error',
                'message': f'Cannot delete component with {pending_requests} pending request(s). Please process all pending requests first.'
            }), 400
        
        # Store component details for transaction log
        component_details = {
            'name': component.name,
            'type': component.type,
            'quantity': component.quantity,
            'location': component.location
        }
        
        # Log transaction before deletion
        user = get_current_user()
        log_component_transaction(
            user,
            ActionType.DELETE,
            component,
            details=component_details
        )
        
        # Delete component
        db.session.delete(component)
        db.session.commit()
        
        return jsonify({
            'message': 'Component deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete component',
            'message': str(e)
        }), 500
