"""
Simple test script to verify authentication system functionality
This is a demonstration script, not a comprehensive test suite
"""
from backend.auth import hash_password, verify_password, generate_tokens
from backend.models import User, UserRole, db
from backend.app import create_app


def test_password_hashing():
    """Test password hashing and verification"""
    print("Testing password hashing...")
    
    password = "TestPassword123"
    hashed = hash_password(password)
    
    print(f"  Original password: {password}")
    print(f"  Hashed password: {hashed[:50]}...")
    
    # Verify correct password
    assert verify_password(password, hashed), "Password verification failed!"
    print("  ✓ Correct password verified successfully")
    
    # Verify incorrect password
    assert not verify_password("WrongPassword", hashed), "Wrong password should not verify!"
    print("  ✓ Incorrect password rejected successfully")
    
    print()


def test_token_generation():
    """Test JWT token generation"""
    print("Testing JWT token generation...")
    
    # Create a test app context with SQLite for testing
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        # Create a mock user object
        class MockUser:
            id = 1
            username = "test_user"
            role = UserRole.STUDENT
        
        user = MockUser()
        tokens = generate_tokens(user)
        
        print(f"  User ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Role: {user.role.value}")
        print(f"  Access token: {tokens['access_token'][:50]}...")
        print(f"  Refresh token: {tokens['refresh_token'][:50]}...")
        print("  ✓ Tokens generated successfully")
    
    print()


def test_authentication_flow():
    """Test complete authentication flow"""
    print("Testing complete authentication flow...")
    print("  This would require a running database and Flask app")
    print("  See backend/README.md for instructions on running the application")
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("LabLink Authentication System Test")
    print("=" * 60)
    print()
    
    test_password_hashing()
    test_token_generation()
    test_authentication_flow()
    
    print("=" * 60)
    print("All basic tests passed! ✓")
    print("=" * 60)
