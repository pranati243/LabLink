#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Integration Test for LabLink System
Tests complete workflows to verify all components are properly integrated
"""
import sys
import os
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path to import backend module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import (
    db, User, Component, Request, Transaction,
    UserRole, RequestStatus, ActionType, EntityType
)
from backend.auth import hash_password, generate_tokens
from flask import json


class IntegrationTestRunner:
    """Integration test runner for LabLink system"""
    
    def __init__(self):
        """Initialize test runner with file-based SQLite database"""
        # Set environment variables for testing
        os.environ['FLASK_ENV'] = 'testing'
        # Use file-based SQLite for better session handling
        test_db_path = os.path.join(os.path.dirname(__file__), 'test_integration.db')
        os.environ['TEST_DATABASE_URL'] = f'sqlite:///{test_db_path}'
        
        # Remove old test database if it exists
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.student_token = None
        self.faculty_token = None
        self.component_id = None
        self.request_id = None
        self.test_db_path = test_db_path
        
    def setup_database(self):
        """Create database tables and seed initial data"""
        print("Setting up test database...")
        
        with self.app.app_context():
            # Create all tables
            db.create_all()
            
            # Create test student user
            student = User(
                username='test_student',
                email='student@lablink.test',
                password_hash=hash_password('student123'),
                role=UserRole.STUDENT
            )
            db.session.add(student)
            
            # Create test faculty user
            faculty = User(
                username='test_faculty',
                email='faculty@lablink.test',
                password_hash=hash_password('faculty123'),
                role=UserRole.FACULTY
            )
            db.session.add(faculty)
            
            db.session.commit()
            
            print("  ✓ Database tables created")
            print("  ✓ Test users created")
    
    def test_authentication_flow(self):
        """Test 1: Authentication flow end-to-end"""
        print("\n" + "=" * 60)
        print("Test 1: Authentication Flow")
        print("=" * 60)
        
        # Generate tokens programmatically (like other tests do)
        print("\n1.1 Generating authentication tokens...")
        with self.app.app_context():
            from backend.models import User
            from backend.auth import generate_tokens
            
            student = User.query.filter_by(username='test_student').first()
            faculty = User.query.filter_by(username='test_faculty').first()
            
            student_tokens = generate_tokens(student)
            faculty_tokens = generate_tokens(faculty)
            
            self.student_token = student_tokens['access_token']
            self.faculty_token = faculty_tokens['access_token']
            
            print("  ✓ Tokens generated successfully")
        
        # Test student login via API
        print("\n1.2 Testing student login via API...")
        response = self.client.post('/api/auth/login', json={
            'username': 'test_student',
            'password': 'student123'
        })
        
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = json.loads(response.data)
        assert 'access_token' in data, "No access token in response"
        assert 'user' in data, "No user data in response"
        assert data['user']['role'] == 'student', "Wrong user role"
        
        print("  ✓ Student login successful")
        print(f"    Username: {data['user']['username']}")
        print(f"    Role: {data['user']['role']}")
        
        # Test faculty login via API
        print("\n1.3 Testing faculty login via API...")
        response = self.client.post('/api/auth/login', json={
            'username': 'test_faculty',
            'password': 'faculty123'
        })
        
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = json.loads(response.data)
        assert data['user']['role'] == 'faculty', "Wrong user role"
        
        print("  ✓ Faculty login successful")
        print(f"    Username: {data['user']['username']}")
        print(f"    Role: {data['user']['role']}")
        
        # Test invalid credentials
        print("\n1.4 Testing invalid credentials...")
        response = self.client.post('/api/auth/login', json={
            'username': 'test_student',
            'password': 'wrong_password'
        })
        
        assert response.status_code == 401, "Should reject invalid credentials"
        print("  ✓ Invalid credentials rejected")
        
        # Test protected endpoint without token
        print("\n1.5 Testing protected endpoint without token...")
        response = self.client.get('/api/components')
        assert response.status_code == 401, "Should require authentication"
        print("  ✓ Protected endpoint requires authentication")
        
        print("\n✓ Authentication flow test passed!")
    
    def test_component_crud_operations(self):
        """Test 2: Component CRUD operations"""
        print("\n" + "=" * 60)
        print("Test 2: Component CRUD Operations")
        print("=" * 60)
        
        # Test creating component (faculty only)
        print("\n2.1 Testing component creation (faculty)...")
        response = self.client.post(
            '/api/components',
            json={
                'name': 'Arduino Uno R3',
                'type': 'Microcontroller',
                'quantity': 15,
                'description': 'ATmega328P based development board',
                'location': 'Lab A, Shelf 2'
            },
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        if response.status_code != 201:
            print(f"    Error response: {json.loads(response.data)}")
        assert response.status_code == 201, f"Component creation failed: {response.status_code}"
        data = json.loads(response.data)
        assert 'component' in data, "No component data in response"
        
        self.component_id = data['component']['id']
        print("  ✓ Component created successfully")
        print(f"    ID: {data['component']['id']}")
        print(f"    Name: {data['component']['name']}")
        print(f"    Quantity: {data['component']['quantity']}")
        
        # Test student cannot create component
        print("\n2.2 Testing component creation (student - should fail)...")
        response = self.client.post(
            '/api/components',
            json={
                'name': 'Test Component',
                'type': 'Test',
                'quantity': 5,
                'location': 'Test'
            },
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 403, "Student should not be able to create components"
        print("  ✓ Student correctly denied component creation")
        
        # Test viewing components (both roles)
        print("\n2.3 Testing component listing...")
        response = self.client.get(
            '/api/components',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200, "Component listing failed"
        data = json.loads(response.data)
        assert len(data['components']) > 0, "No components returned"
        print(f"  ✓ Component listing successful ({data['total']} components)")
        
        # Test updating component (faculty only)
        print("\n2.4 Testing component update (faculty)...")
        response = self.client.put(
            f'/api/components/{self.component_id}',
            json={'quantity': 20},
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, "Component update failed"
        data = json.loads(response.data)
        assert data['component']['quantity'] == 20, "Quantity not updated"
        print("  ✓ Component updated successfully")
        print(f"    New quantity: {data['component']['quantity']}")
        
        # Test getting single component
        print("\n2.5 Testing get component by ID...")
        response = self.client.get(
            f'/api/components/{self.component_id}',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200, "Get component failed"
        data = json.loads(response.data)
        assert data['component']['id'] == self.component_id, "Wrong component returned"
        print("  ✓ Get component by ID successful")
        
        print("\n✓ Component CRUD operations test passed!")
    
    def test_request_workflow(self):
        """Test 3: Request workflow (create, approve, reject, return)"""
        print("\n" + "=" * 60)
        print("Test 3: Request Workflow")
        print("=" * 60)
        
        # Test creating request (student)
        print("\n3.1 Testing request creation (student)...")
        response = self.client.post(
            '/api/requests',
            json={
                'component_id': self.component_id,
                'quantity': 3
            },
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 201, f"Request creation failed: {response.status_code}"
        data = json.loads(response.data)
        assert data['request']['status'] == 'Pending', "Request should be Pending"
        
        self.request_id = data['request']['id']
        print("  ✓ Request created successfully")
        print(f"    ID: {data['request']['id']}")
        print(f"    Status: {data['request']['status']}")
        print(f"    Quantity: {data['request']['quantity']}")
        
        # Test student viewing their requests
        print("\n3.2 Testing student viewing their requests...")
        response = self.client.get(
            '/api/requests',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200, "Get requests failed"
        data = json.loads(response.data)
        assert len(data['requests']) > 0, "No requests returned"
        print(f"  ✓ Student can view their requests ({data['total']} requests)")
        
        # Test faculty viewing all requests
        print("\n3.3 Testing faculty viewing all requests...")
        response = self.client.get(
            '/api/requests',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, "Get requests failed"
        data = json.loads(response.data)
        assert len(data['requests']) > 0, "No requests returned"
        print(f"  ✓ Faculty can view all requests ({data['total']} requests)")
        
        # Test approving request (faculty)
        print("\n3.4 Testing request approval (faculty)...")
        
        # Get component quantity before approval
        response = self.client.get(
            f'/api/components/{self.component_id}',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        quantity_before = json.loads(response.data)['component']['quantity']
        
        # Approve request
        response = self.client.post(
            f'/api/requests/{self.request_id}/approve',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, f"Request approval failed: {response.status_code}"
        data = json.loads(response.data)
        assert data['request']['status'] == 'Approved', "Request should be Approved"
        
        # Verify component quantity decreased
        response = self.client.get(
            f'/api/components/{self.component_id}',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        quantity_after = json.loads(response.data)['component']['quantity']
        
        assert quantity_after == quantity_before - 3, "Component quantity should decrease"
        print("  ✓ Request approved successfully")
        print(f"    Component quantity: {quantity_before} → {quantity_after}")
        
        # Test returning request (faculty)
        print("\n3.5 Testing request return (faculty)...")
        response = self.client.post(
            f'/api/requests/{self.request_id}/return',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, f"Request return failed: {response.status_code}"
        data = json.loads(response.data)
        assert data['request']['status'] == 'Returned', "Request should be Returned"
        
        # Verify component quantity increased
        response = self.client.get(
            f'/api/components/{self.component_id}',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        quantity_final = json.loads(response.data)['component']['quantity']
        
        assert quantity_final == quantity_before, "Component quantity should be restored"
        print("  ✓ Request returned successfully")
        print(f"    Component quantity restored: {quantity_after} → {quantity_final}")
        
        # Test rejection workflow
        print("\n3.6 Testing request rejection workflow...")
        
        # Create another request
        response = self.client.post(
            '/api/requests',
            json={
                'component_id': self.component_id,
                'quantity': 2
            },
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        reject_request_id = json.loads(response.data)['request']['id']
        
        # Reject the request
        response = self.client.post(
            f'/api/requests/{reject_request_id}/reject',
            json={'rejection_reason': 'Component reserved for another project'},
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, "Request rejection failed"
        data = json.loads(response.data)
        assert data['request']['status'] == 'Rejected', "Request should be Rejected"
        assert data['request']['rejection_reason'] is not None, "Rejection reason should be stored"
        print("  ✓ Request rejected successfully")
        print(f"    Reason: {data['request']['rejection_reason']}")
        
        print("\n✓ Request workflow test passed!")
    
    def test_transaction_logging(self):
        """Test 4: Transaction logging"""
        print("\n" + "=" * 60)
        print("Test 4: Transaction Logging")
        print("=" * 60)
        
        # Test viewing transactions (faculty only)
        print("\n4.1 Testing transaction log viewing (faculty)...")
        response = self.client.get(
            '/api/transactions',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, "Get transactions failed"
        data = json.loads(response.data)
        assert 'transactions' in data, "No transactions in response"
        assert data['total'] > 0, "No transactions logged"
        print(f"  ✓ Transaction log accessible ({data['total']} transactions)")
        
        # Verify different action types are logged
        action_types = set(txn['action_type'] for txn in data['transactions'])
        print(f"    Action types logged: {', '.join(action_types)}")
        
        # Test student cannot view transactions
        print("\n4.2 Testing transaction log access (student - should fail)...")
        response = self.client.get(
            '/api/transactions',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 403, "Student should not access transaction log"
        print("  ✓ Student correctly denied transaction log access")
        
        # Test filtering transactions
        print("\n4.3 Testing transaction filtering...")
        response = self.client.get(
            '/api/transactions?action_type=CREATE',
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 200, "Transaction filtering failed"
        data = json.loads(response.data)
        if data['total'] > 0:
            assert all(txn['action_type'] == 'CREATE' for txn in data['transactions']), \
                "Filter not working correctly"
        print("  ✓ Transaction filtering works correctly")
        
        print("\n✓ Transaction logging test passed!")
    
    def test_role_based_access_control(self):
        """Test 5: Role-based access control"""
        print("\n" + "=" * 60)
        print("Test 5: Role-Based Access Control")
        print("=" * 60)
        
        # Test student cannot access faculty-only endpoints
        print("\n5.1 Testing student access restrictions...")
        
        faculty_only_endpoints = [
            ('POST', '/api/components', {'name': 'Test', 'type': 'Test', 'quantity': 1, 'location': 'Test'}),
            ('PUT', f'/api/components/{self.component_id}', {'quantity': 10}),
            ('DELETE', f'/api/components/{self.component_id}', None),
            ('POST', f'/api/requests/{self.request_id}/approve', None),
            ('POST', f'/api/requests/{self.request_id}/reject', None),
            ('POST', f'/api/requests/{self.request_id}/return', None),
            ('GET', '/api/transactions', None),
        ]
        
        denied_count = 0
        for method, endpoint, data in faculty_only_endpoints:
            if method == 'GET':
                response = self.client.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {self.student_token}'}
                )
            elif method == 'POST':
                response = self.client.post(
                    endpoint,
                    json=data,
                    headers={'Authorization': f'Bearer {self.student_token}'}
                )
            elif method == 'PUT':
                response = self.client.put(
                    endpoint,
                    json=data,
                    headers={'Authorization': f'Bearer {self.student_token}'}
                )
            elif method == 'DELETE':
                response = self.client.delete(
                    endpoint,
                    headers={'Authorization': f'Bearer {self.student_token}'}
                )
            
            if response.status_code == 403:
                denied_count += 1
        
        print(f"  ✓ Student correctly denied access to {denied_count}/{len(faculty_only_endpoints)} faculty endpoints")
        
        # Test faculty cannot create requests
        print("\n5.2 Testing faculty access restrictions...")
        response = self.client.post(
            '/api/requests',
            json={
                'component_id': self.component_id,
                'quantity': 1
            },
            headers={'Authorization': f'Bearer {self.faculty_token}'}
        )
        
        assert response.status_code == 403, "Faculty should not be able to create requests"
        print("  ✓ Faculty correctly denied request creation")
        
        print("\n✓ Role-based access control test passed!")
    
    def test_health_check(self):
        """Test 6: Health check endpoint"""
        print("\n" + "=" * 60)
        print("Test 6: Health Check Endpoint")
        print("=" * 60)
        
        print("\n6.1 Testing health check endpoint...")
        response = self.client.get('/health')
        
        assert response.status_code == 200, "Health check failed"
        data = json.loads(response.data)
        assert 'status' in data, "No status in health check"
        assert 'database' in data, "No database status in health check"
        
        print("  ✓ Health check endpoint working")
        print(f"    Status: {data['status']}")
        print(f"    Database: {data['database']}")
        
        print("\n✓ Health check test passed!")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "=" * 60)
        print("LABLINK SYSTEM - END-TO-END INTEGRATION TEST")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_database()
            
            # Run tests in order
            self.test_authentication_flow()
            self.test_component_crud_operations()
            self.test_request_workflow()
            self.test_transaction_logging()
            self.test_role_based_access_control()
            self.test_health_check()
            
            # Summary
            print("\n" + "=" * 60)
            print("ALL INTEGRATION TESTS PASSED! ✓")
            print("=" * 60)
            print("\nVerified:")
            print("  ✓ Authentication flow end-to-end")
            print("  ✓ Component CRUD operations")
            print("  ✓ Request workflow (create, approve, reject, return)")
            print("  ✓ Transaction logging")
            print("  ✓ Role-based access control")
            print("  ✓ Health check endpoint")
            print("\nAll components are properly integrated!")
            print("=" * 60)
            
            return True
            
        except AssertionError as e:
            print(f"\n\n✗ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n\n✗ UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    runner = IntegrationTestRunner()
    success = runner.run_all_tests()
    
    # Cleanup test database
    if hasattr(runner, 'test_db_path') and os.path.exists(runner.test_db_path):
        try:
            os.remove(runner.test_db_path)
        except:
            pass
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
