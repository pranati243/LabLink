"""
Simple test script to verify request management system functionality
This is a demonstration script, not a comprehensive test suite
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.models import db, User, Component, Request, UserRole, RequestStatus
from backend.auth import hash_password, generate_tokens
from flask import json


def setup_test_data(app):
    """Create test users and components"""
    # Create tables
    db.create_all()
    
    # Create test student
    student = User(
        username='test_student',
        email='student@test.com',
        password_hash=hash_password('password123'),
        role=UserRole.STUDENT
    )
    db.session.add(student)
    
    # Create test faculty
    faculty = User(
        username='test_faculty',
        email='faculty@test.com',
        password_hash=hash_password('password123'),
        role=UserRole.FACULTY
    )
    db.session.add(faculty)
    
    # Create test component
    component = Component(
        name='Arduino Uno',
        type='Microcontroller',
        quantity=10,
        description='Test component',
        location='Lab A'
    )
    db.session.add(component)
    
    db.session.commit()
    
    return student, faculty, component


def test_request_creation():
    """Test creating a new request"""
    print("Testing request creation...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        student, faculty, component = setup_test_data(app)
        
        # Get IDs before leaving context
        component_id = component.id
        
        # Generate token for student
        tokens = generate_tokens(student)
        access_token = tokens['access_token']
    
    # Create test client outside app context
    client = app.test_client()
    
    # Test creating a request
    response = client.post(
        '/api/requests',
        json={
            'component_id': component_id,
            'quantity': 2
        },
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = json.loads(response.data)
    assert 'request' in data, "Response should contain request data"
    assert data['request']['status'] == 'Pending', "Request status should be Pending"
    print("  ✓ Request created successfully")
    
    # Test validation - quantity exceeds available
    response = client.post(
        '/api/requests',
        json={
            'component_id': component_id,
            'quantity': 100
        },
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print("  ✓ Validation works for excessive quantity")
    
    print()


def test_request_viewing():
    """Test viewing requests with role-based filtering"""
    print("Testing request viewing...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        student, faculty, component = setup_test_data(app)
        
        # Create a request
        request_obj = Request(
            student_id=student.id,
            component_id=component.id,
            quantity=2,
            status=RequestStatus.PENDING
        )
        db.session.add(request_obj)
        db.session.commit()
        
        # Generate tokens
        student_token = generate_tokens(student)['access_token']
        faculty_token = generate_tokens(faculty)['access_token']
    
    client = app.test_client()
    
    # Test student viewing their own requests
    response = client.get(
        '/api/requests',
        headers={'Authorization': f'Bearer {student_token}'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert len(data['requests']) == 1, "Student should see their own request"
    print("  ✓ Student can view their own requests")
    
    # Test faculty viewing all requests
    response = client.get(
        '/api/requests',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert len(data['requests']) == 1, "Faculty should see all requests"
    print("  ✓ Faculty can view all requests")
    
    print()


def test_request_approval():
    """Test approving a request"""
    print("Testing request approval...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        student, faculty, component = setup_test_data(app)
        
        # Create a request
        request_obj = Request(
            student_id=student.id,
            component_id=component.id,
            quantity=2,
            status=RequestStatus.PENDING
        )
        db.session.add(request_obj)
        db.session.commit()
        
        initial_quantity = component.quantity
        request_id = request_obj.id
        component_id = component.id
        
        # Generate faculty token
        faculty_token = generate_tokens(faculty)['access_token']
    
    client = app.test_client()
    
    # Test approving request
    response = client.post(
        f'/api/requests/{request_id}/approve',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert data['request']['status'] == 'Approved', "Request status should be Approved"
    print("  ✓ Request approved successfully")
    
    # Verify component quantity decreased
    with app.app_context():
        component = Component.query.get(component_id)
        assert component.quantity == initial_quantity - 2, "Component quantity should decrease"
        print("  ✓ Component quantity decreased correctly")
    
    print()


def test_request_rejection():
    """Test rejecting a request"""
    print("Testing request rejection...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        student, faculty, component = setup_test_data(app)
        
        # Create a request
        request_obj = Request(
            student_id=student.id,
            component_id=component.id,
            quantity=2,
            status=RequestStatus.PENDING
        )
        db.session.add(request_obj)
        db.session.commit()
        
        initial_quantity = component.quantity
        request_id = request_obj.id
        component_id = component.id
        
        # Generate faculty token
        faculty_token = generate_tokens(faculty)['access_token']
    
    client = app.test_client()
    
    # Test rejecting request
    response = client.post(
        f'/api/requests/{request_id}/reject',
        json={'rejection_reason': 'Not available'},
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert data['request']['status'] == 'Rejected', "Request status should be Rejected"
    assert data['request']['rejection_reason'] == 'Not available', "Rejection reason should be stored"
    print("  ✓ Request rejected successfully")
    
    # Verify component quantity unchanged
    with app.app_context():
        component = Component.query.get(component_id)
        assert component.quantity == initial_quantity, "Component quantity should not change"
        print("  ✓ Component quantity unchanged")
    
    print()


def test_request_return():
    """Test marking a request as returned"""
    print("Testing request return...")
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        student, faculty, component = setup_test_data(app)
        
        # Create an approved request
        request_obj = Request(
            student_id=student.id,
            component_id=component.id,
            quantity=2,
            status=RequestStatus.APPROVED
        )
        db.session.add(request_obj)
        
        # Decrease component quantity to simulate approval
        component.quantity -= 2
        db.session.commit()
        
        current_quantity = component.quantity
        request_id = request_obj.id
        component_id = component.id
        
        # Generate faculty token
        faculty_token = generate_tokens(faculty)['access_token']
    
    client = app.test_client()
    
    # Test returning request
    response = client.post(
        f'/api/requests/{request_id}/return',
        headers={'Authorization': f'Bearer {faculty_token}'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = json.loads(response.data)
    assert data['request']['status'] == 'Returned', "Request status should be Returned"
    print("  ✓ Request marked as returned successfully")
    
    # Verify component quantity increased
    with app.app_context():
        component = Component.query.get(component_id)
        assert component.quantity == current_quantity + 2, "Component quantity should increase"
        print("  ✓ Component quantity increased correctly")
    
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("LabLink Request Management System Test")
    print("=" * 60)
    print()
    
    try:
        test_request_creation()
        test_request_viewing()
        test_request_approval()
        test_request_rejection()
        test_request_return()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
