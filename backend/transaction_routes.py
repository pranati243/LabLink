"""
Transaction log routes for LabLink System
Handles viewing and filtering of transaction audit logs
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_
from backend.models import (
    db, Transaction, User, Component, Request as RequestModel,
    ActionType, EntityType
)
from backend.middleware import jwt_required, role_required


transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')


@transaction_bp.route('', methods=['GET'])
@jwt_required
@role_required('faculty')
def get_transactions():
    """
    Get all transactions with filtering options (Faculty only)
    
    Displays transactions in reverse chronological order (most recent first)
    
    Query Parameters:
        - start_date: Filter transactions from this date (ISO format: YYYY-MM-DD)
        - end_date: Filter transactions until this date (ISO format: YYYY-MM-DD)
        - user_id: Filter by user ID
        - action_type: Filter by action type (CREATE, UPDATE, DELETE, REQUEST, APPROVE, REJECT, RETURN)
        - component_name: Search by component name (case-insensitive partial match)
        - limit: Maximum number of results (default: 100)
        - offset: Number of results to skip for pagination (default: 0)
        
    Returns:
        200: List of transactions with details
        400: Validation error (invalid date format or action type)
        403: Insufficient permissions (not faculty)
    """
    try:
        query = Transaction.query
        
        # Filter by date range
        start_date = request.args.get('start_date')
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
                query = query.filter(Transaction.timestamp >= start_datetime)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid start_date format. Use ISO format: YYYY-MM-DD'
                }), 400
        
        end_date = request.args.get('end_date')
        if end_date:
            try:
                # Add one day to include the entire end date
                end_datetime = datetime.fromisoformat(end_date)
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                query = query.filter(Transaction.timestamp <= end_datetime)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid end_date format. Use ISO format: YYYY-MM-DD'
                }), 400
        
        # Filter by user
        user_id = request.args.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
                query = query.filter(Transaction.user_id == user_id)
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Invalid user_id. Must be an integer'
                }), 400
        
        # Filter by action type
        action_type = request.args.get('action_type')
        if action_type:
            try:
                action_enum = ActionType[action_type.upper()]
                query = query.filter(Transaction.action_type == action_enum)
            except KeyError:
                valid_actions = ', '.join([a.name for a in ActionType])
                return jsonify({
                    'error': 'Validation error',
                    'message': f'Invalid action_type: {action_type}. Valid values: {valid_actions}'
                }), 400
        
        # Search by component name
        component_name = request.args.get('component_name')
        if component_name:
            # Search in transaction details for component_name field
            query = query.filter(
                Transaction.details['component_name'].astext.ilike(f'%{component_name}%')
            )
        
        # Get pagination parameters
        try:
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            
            if limit < 1 or limit > 1000:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Limit must be between 1 and 1000'
                }), 400
            
            if offset < 0:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'Offset must be non-negative'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Validation error',
                'message': 'Invalid limit or offset. Must be integers'
            }), 400
        
        # Get total count before pagination
        total_count = query.count()
        
        # Order by most recent first and apply pagination
        transactions = query.order_by(Transaction.timestamp.desc()).limit(limit).offset(offset).all()
        
        # Enrich transaction data with user and entity information
        enriched_transactions = []
        for txn in transactions:
            txn_dict = txn.to_dict()
            
            # Add user information
            user = User.query.get(txn.user_id)
            if user:
                txn_dict['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role.value
                }
            
            # Add entity information based on entity type
            if txn.entity_type == EntityType.Component:
                component = Component.query.get(txn.entity_id)
                if component:
                    txn_dict['entity'] = {
                        'type': 'Component',
                        'id': component.id,
                        'name': component.name
                    }
            elif txn.entity_type == EntityType.Request:
                req = RequestModel.query.get(txn.entity_id)
                if req:
                    txn_dict['entity'] = {
                        'type': 'Request',
                        'id': req.id,
                        'status': req.status.value
                    }
            
            enriched_transactions.append(txn_dict)
        
        return jsonify({
            'transactions': enriched_transactions,
            'total': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve transactions',
            'message': str(e)
        }), 500
