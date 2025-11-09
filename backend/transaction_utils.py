"""
Transaction logging utilities for LabLink System
Provides centralized transaction logging functionality
"""
from backend.models import db, Transaction, ActionType, EntityType


def log_transaction(user_id, action_type, entity_type, entity_id, details=None):
    """
    Log a transaction to the audit log
    
    This is a centralized utility function for recording all system actions
    in the transaction log for audit purposes.
    
    Args:
        user_id: ID of the user performing the action (integer)
        action_type: Type of action being performed (ActionType enum or string)
        entity_type: Type of entity being acted upon (EntityType enum or string)
        entity_id: ID of the entity being acted upon (integer)
        details: Optional dictionary with additional details about the transaction
        
    Returns:
        Transaction: The created transaction object
        
    Raises:
        ValueError: If action_type or entity_type are invalid
        
    Example:
        log_transaction(
            user_id=1,
            action_type=ActionType.CREATE,
            entity_type=EntityType.Component,
            entity_id=5,
            details={'name': 'Arduino Uno', 'quantity': 10}
        )
    """
    # Convert string to enum if necessary
    if isinstance(action_type, str):
        try:
            action_type = ActionType[action_type.upper()]
        except KeyError:
            raise ValueError(f"Invalid action_type: {action_type}")
    
    if isinstance(entity_type, str):
        try:
            entity_type = EntityType[entity_type.upper()]
        except KeyError:
            raise ValueError(f"Invalid entity_type: {entity_type}")
    
    # Create transaction record
    transaction = Transaction(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {}
    )
    
    db.session.add(transaction)
    
    return transaction
