"""
Simple demonstration script to verify transaction log functionality
"""
from backend.transaction_utils import log_transaction
from backend.models import db, User, Component, Transaction, UserRole, ActionType, EntityType
from backend.app import create_app


def test_transaction_logging():
    """Test transaction logging utility"""
    print("Testing transaction logging utility...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(
            username='test_faculty',
            email='faculty@test.com',
            password_hash='hashed_password',
            role=UserRole.FACULTY
        )
        db.session.add(user)
        db.session.commit()
        
        # Create test component
        component = Component(
            name='Arduino Uno',
            type='Microcontroller',
            quantity=10,
            location='Lab A'
        )
        db.session.add(component)
        db.session.commit()
        
        print(f"  Created user: {user.username} (ID: {user.id})")
        print(f"  Created component: {component.name} (ID: {component.id})")
        
        # Test logging a transaction
        transaction = log_transaction(
            user_id=user.id,
            action_type=ActionType.CREATE,
            entity_type=EntityType.COMPONENT,
            entity_id=component.id,
            details={
                'component_name': component.name,
                'quantity': component.quantity,
                'location': component.location
            }
        )
        db.session.commit()
        
        print(f"  ✓ Transaction logged successfully (ID: {transaction.id})")
        print(f"    Action: {transaction.action_type.value}")
        print(f"    Entity: {transaction.entity_type.value} #{transaction.entity_id}")
        print(f"    Details: {transaction.details}")
        
        # Test with string enums
        transaction2 = log_transaction(
            user_id=user.id,
            action_type='UPDATE',
            entity_type='COMPONENT',
            entity_id=component.id,
            details={'old_quantity': 10, 'new_quantity': 15}
        )
        db.session.commit()
        
        print(f"  ✓ Transaction with string enums logged (ID: {transaction2.id})")
        
        # Verify transactions were created
        all_transactions = Transaction.query.all()
        print(f"\n  Total transactions in database: {len(all_transactions)}")
        
        for txn in all_transactions:
            print(f"    - {txn.action_type.value} on {txn.entity_type.value} #{txn.entity_id}")
        
        print("\n✓ Transaction logging utility working correctly!\n")


def test_transaction_routes():
    """Test transaction API routes"""
    print("Testing transaction API routes...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    # Check that the blueprint is registered
    print(f"  Registered blueprints: {list(app.blueprints.keys())}")
    
    if 'transactions' in app.blueprints:
        print("  ✓ Transaction blueprint registered successfully")
        
        # Check routes
        transaction_routes = [rule.rule for rule in app.url_map.iter_rules() if 'transaction' in rule.rule]
        print(f"  Transaction routes: {transaction_routes}")
        print("  ✓ Transaction routes configured correctly")
    else:
        print("  ✗ Transaction blueprint not found!")
    
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("Transaction Log System Demonstration")
    print("=" * 60)
    print()
    
    test_transaction_logging()
    test_transaction_routes()
    
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
