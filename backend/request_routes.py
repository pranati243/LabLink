"""
Request management routes for LabLink System
Handles student request submission and faculty request processing
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.models import (
    db, Request, Component, RequestStatus, Transaction, 
    ActionType, EntityType, UserRole
)
from backend.middleware import jwt_required, role_required
from backend.auth import get_current_user, get_current_user_role


request_bp = Blueprint('requests', __name__, url_prefix='/api/requests')


def log_request_transaction(user, action_type, request_obj, details=None):
    """
    Log a request transaction to the audit log
    
    Args:
        user: User performing the action
        action_type: ActionType enum value
        request_obj: Request being acted upon
        details: Optional dictionary with additional details
    """
    transaction = Transaction(
        user_id=user.id,
        action_type=action_type,
        entity_type=EntityType.Request,
        entity_id=request_obj.id,
        details=details or {}
    )
    db.session.add(transaction)


@request_bp.route('', methods=['POST'])
@jwt_required
@role_required('student')
def create_request():
    """
    Create a new component request (Student only)
    
    Request Body:
        - component_id: ID of the component to request (required)
        - quantity: Quantity requested (required, positive integer)
        
    Returns:
        201: Request created successfully
        400: Validation error
        403: Insufficient permissions (not a student)
        404: Component not found
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Request body is required'
            }), 400
        
        # Validate required fields
        if 'component_id' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Missing required field: component_id'
            }), 400
        
        if 'quantity' not in data:
            return jsonify({
                'error': 'Validation error',
                'message': 'Missing required field: quantity'
            }), 400
        
        # Validate quantity
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Quantity must be a positive integer'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Validation error',
                'message': 'Quantity must be a valid integer'
            }), 400
        
        # Get component
        component = Component.query.get(data['component_id'])
        if not component:
            return jsonify({
                'error': 'Not found',
                'message': f'Component with ID {data["component_id"]} not found'
            }), 404
        
        # Prevent requests for zero-quantity components
        if component.quantity == 0:
            return jsonify({
                'error': 'Validation error',
                'message': 'Cannot request components with zero quantity'
            }), 400
        
        # Validate requested quantity against available quantity
        if quantity > component.quantity:
            return jsonify({
                'error': 'Validation error',
                'message': f'Requested quantity ({quantity}) exceeds available quantity ({component.quantity})'
            }), 400
        
        # Get current user
        user = get_current_user()
        
        # Create new request with Pending status
        new_request = Request(
            student_id=user.id,
            component_id=component.id,
            quantity=quantity,
            status=RequestStatus.Pending
        )
        
        db.session.add(new_request)
        db.session.flush()  # Get request ID before commit
        
        # Log transaction
        log_request_transaction(
            user,
            ActionType.REQUEST,
            new_request,
            details={
                'component_name': component.name,
                'component_id': component.id,
                'quantity': quantity,
                'student_username': user.username
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Request created successfully',
            'request': new_request.to_dict(include_relations=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create request',
            'message': str(e)
        }), 500



@request_bp.route('', methods=['GET'])
@jwt_required
def get_requests():
    """
    Get all requests with role-based filtering
    
    Students see only their own requests
    Faculty see all requests
    
    Query Parameters:
        - status: Filter by request status (optional)
        
    Returns:
        200: List of requests
    """
    try:
        user = get_current_user()
        user_role = get_current_user_role()
        
        # Build query based on user role
        if user_role == 'student':
            # Students see only their own requests
            query = Request.query.filter_by(student_id=user.id)
        else:
            # Faculty see all requests
            query = Request.query
        
        # Filter by status if provided
        status_filter = request.args.get('status')
        if status_filter:
            try:
                status_enum = RequestStatus[status_filter.upper()]
                query = query.filter_by(status=status_enum)
            except KeyError:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'Invalid status: {status_filter}. Valid values: Pending, Approved, Rejected, Returned'
                }), 400
        
        # Execute query and order by most recent first
        requests = query.order_by(Request.requested_at.desc()).all()
        
        return jsonify({
            'requests': [req.to_dict(include_relations=True) for req in requests],
            'total': len(requests)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve requests',
            'message': str(e)
        }), 500


@request_bp.route('/<int:request_id>', methods=['GET'])
@jwt_required
def get_request(request_id):
    """
    Get request details by ID
    
    Students can only view their own requests
    Faculty can view all requests
    
    Args:
        request_id: Request ID
        
    Returns:
        200: Request details
        403: Insufficient permissions (student trying to view another student's request)
        404: Request not found
    """
    try:
        request_obj = Request.query.get(request_id)
        
        if not request_obj:
            return jsonify({
                'error': 'Not found',
                'message': f'Request with ID {request_id} not found'
            }), 404
        
        # Check authorization
        user = get_current_user()
        user_role = get_current_user_role()
        
        # Students can only view their own requests
        if user_role == 'student' and request_obj.student_id != user.id:
            return jsonify({
                'error': 'Insufficient permissions',
                'message': 'You can only view your own requests'
            }), 403
        
        return jsonify({
            'request': request_obj.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve request',
            'message': str(e)
        }), 500



@request_bp.route('/<int:request_id>/approve', methods=['POST'])
@jwt_required
@role_required('faculty')
def approve_request(request_id):
    """
    Approve a pending request (Faculty only)
    
    Updates request status to Approved and decreases component quantity
    
    Args:
        request_id: Request ID
        
    Returns:
        200: Request approved successfully
        400: Validation error (insufficient quantity, invalid status)
        403: Insufficient permissions
        404: Request not found
    """
    try:
        request_obj = Request.query.get(request_id)
        
        if not request_obj:
            return jsonify({
                'error': 'Not found',
                'message': f'Request with ID {request_id} not found'
            }), 404
        
        # Validate request is in Pending status
        if request_obj.status != RequestStatus.Pending:
            return jsonify({
                'error': 'Validation error',
                'message': f'Cannot approve request with status: {request_obj.status.value}. Only Pending requests can be approved.'
            }), 400
        
        # Get component
        component = request_obj.component
        
        # Validate available quantity before approval
        if component.quantity < request_obj.quantity:
            return jsonify({
                'error': 'Validation error',
                'message': f'Insufficient quantity. Available: {component.quantity}, Requested: {request_obj.quantity}'
            }), 400
        
        # Get current faculty user
        user = get_current_user()
        
        # Update request status to Approved
        request_obj.status = RequestStatus.Approved
        request_obj.processed_at = datetime.utcnow()
        request_obj.processed_by = user.id
        
        # Decrease component quantity by requested amount
        component.quantity -= request_obj.quantity
        
        # Log transaction
        log_request_transaction(
            user,
            ActionType.APPROVE,
            request_obj,
            details={
                'component_name': component.name,
                'component_id': component.id,
                'quantity': request_obj.quantity,
                'student_username': request_obj.student.username,
                'faculty_username': user.username,
                'previous_component_quantity': component.quantity + request_obj.quantity,
                'new_component_quantity': component.quantity
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Request approved successfully',
            'request': request_obj.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to approve request',
            'message': str(e)
        }), 500



@request_bp.route('/<int:request_id>/reject', methods=['POST'])
@jwt_required
@role_required('faculty')
def reject_request(request_id):
    """
    Reject a pending request (Faculty only)
    
    Updates request status to Rejected without modifying component quantity
    
    Args:
        request_id: Request ID
        
    Request Body:
        - rejection_reason: Reason for rejection (optional)
        
    Returns:
        200: Request rejected successfully
        400: Validation error (invalid status)
        403: Insufficient permissions
        404: Request not found
    """
    try:
        request_obj = Request.query.get(request_id)
        
        if not request_obj:
            return jsonify({
                'error': 'Not found',
                'message': f'Request with ID {request_id} not found'
            }), 404
        
        # Validate request is in Pending status
        if request_obj.status != RequestStatus.Pending:
            return jsonify({
                'error': 'Validation error',
                'message': f'Cannot reject request with status: {request_obj.status.value}. Only Pending requests can be rejected.'
            }), 400
        
        # Get optional rejection reason from request body
        data = request.get_json() or {}
        rejection_reason = data.get('rejection_reason')
        
        # Get current faculty user
        user = get_current_user()
        
        # Update request status to Rejected
        request_obj.status = RequestStatus.Rejected
        request_obj.processed_at = datetime.utcnow()
        request_obj.processed_by = user.id
        request_obj.rejection_reason = rejection_reason
        
        # Do not modify component quantity
        
        # Log transaction
        log_request_transaction(
            user,
            ActionType.REJECT,
            request_obj,
            details={
                'component_name': request_obj.component.name,
                'component_id': request_obj.component_id,
                'quantity': request_obj.quantity,
                'student_username': request_obj.student.username,
                'faculty_username': user.username,
                'rejection_reason': rejection_reason
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Request rejected successfully',
            'request': request_obj.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to reject request',
            'message': str(e)
        }), 500



@request_bp.route('/<int:request_id>/return', methods=['POST'])
@jwt_required
@role_required('faculty')
def return_request(request_id):
    """
    Mark a request as returned (Faculty only)
    
    Updates request status to Returned and increases component quantity
    
    Args:
        request_id: Request ID
        
    Returns:
        200: Request marked as returned successfully
        400: Validation error (invalid status, already returned)
        403: Insufficient permissions
        404: Request not found
    """
    try:
        request_obj = Request.query.get(request_id)
        
        if not request_obj:
            return jsonify({
                'error': 'Not found',
                'message': f'Request with ID {request_id} not found'
            }), 404
        
        # Validate request is in Approved status
        if request_obj.status != RequestStatus.Approved:
            return jsonify({
                'error': 'Validation error',
                'message': f'Cannot mark request as returned with status: {request_obj.status.value}. Only Approved requests can be returned.'
            }), 400
        
        # Prevent duplicate return operations
        if request_obj.returned_at is not None:
            return jsonify({
                'error': 'Validation error',
                'message': 'This request has already been marked as returned'
            }), 400
        
        # Get component
        component = request_obj.component
        
        # Get current faculty user
        user = get_current_user()
        
        # Update request status to Returned
        request_obj.status = RequestStatus.Returned
        request_obj.returned_at = datetime.utcnow()
        
        # Increase component quantity by returned amount
        previous_quantity = component.quantity
        component.quantity += request_obj.quantity
        
        # Log transaction
        log_request_transaction(
            user,
            ActionType.RETURN,
            request_obj,
            details={
                'component_name': component.name,
                'component_id': component.id,
                'quantity': request_obj.quantity,
                'student_username': request_obj.student.username,
                'faculty_username': user.username,
                'previous_component_quantity': previous_quantity,
                'new_component_quantity': component.quantity
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Request marked as returned successfully',
            'request': request_obj.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to mark request as returned',
            'message': str(e)
        }), 500

