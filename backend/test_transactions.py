"""
Tests for transaction log endpoints
"""
import pytest
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models import (
    db, User, Component, Transaction, 
    UserRole, ActionType, EntityType
)
from backend.auth import hash_password


@pytest.fixture
def app():
    """Create test application"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        
        # Create test users
        faculty = User(
            username='faculty_test',
            email='faculty@test.com',
            password_hash=hash_password('password123'),
            role=UserRole.FACULTY
        )
        student = User(
            username='student_test',
            email='student@test.com',
            password_hash=hash_password('password123'),
            role=UserRole.STUDENT
        )
        db.session.add(faculty)
        db.session.add(student)
        db.session.commit()
        
        # Create test component
        component = Component(
            name='Test Arduino',
            type='Microcontroller',
            quantity=10,
            location='Lab A'
        )
        db.session.add(component)
        db.session.commit()
        
        # Create test transactions
        txn1 = Transaction(
            user_id=faculty.id,
            action_type=ActionType.CREATE,
            entity_type=EntityType.Component,
            entity_id=component.id,
            details={'component_name': 'Test Arduino', 'quantity': 10}
        )
        txn2 = Transaction(
            user_id=faculty.id,
            action_type=ActionType.UPDATE,
            entity_type=EntityType.Component,
            entity_id=component.id,
            details={'component_name': 'Test Arduino', 'old_quantity': 10, 'new_quantity': 15}
        )
        db.session.add(txn1)
        db.session.add(txn2)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def faculty_token(client):
    """Get faculty JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'faculty_test',
        'password': 'password123'
    })
    return response.json['access_token']


@pytest.fixture
def student_token(client):
    """Get student JWT token"""
    response = client.post('/api/auth/login', json={
        'username': 'student_test',
        'password': 'password123'
    })
    return response.json['access_token']


def test_get_transactions_faculty(client, faculty_token):
    """Test faculty can view all transactions"""
    response = client.get(
        '/api/transactions',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert 'transactions' in data
    assert 'total' in data
    assert data['total'] >= 2  # At least the 2 test transactions


def test_get_transactions_student_forbidden(client, student_token):
    """Test students cannot view transactions"""
    response = client.get(
        '/api/transactions',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 403


def test_get_transactions_filter_by_action_type(client, faculty_token):
    """Test filtering transactions by action type"""
    response = client.get(
        '/api/transactions?action_type=CREATE',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert all(txn['action_type'] == 'CREATE' for txn in data['transactions'])


def test_get_transactions_filter_by_component_name(client, faculty_token):
    """Test searching transactions by component name"""
    response = client.get(
        '/api/transactions?component_name=Arduino',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert data['total'] >= 1


def test_get_transactions_pagination(client, faculty_token):
    """Test transaction pagination"""
    response = client.get(
        '/api/transactions?limit=1&offset=0',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200
    data = response.json
    assert len(data['transactions']) <= 1
    assert data['limit'] == 1
    assert data['offset'] == 0


def test_get_transactions_invalid_action_type(client, faculty_token):
    """Test invalid action type returns error"""
    response = client.get(
        '/api/transactions?action_type=INVALID',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_get_transactions_no_auth(client):
    """Test accessing transactions without authentication"""
    response = client.get('/api/transactions')
    
    assert response.status_code == 401
