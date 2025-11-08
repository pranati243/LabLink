"""
Seed data script for LabLink System
Creates initial users, components, and sample requests
"""
import os
from datetime import datetime, timedelta
from flask import Flask
import bcrypt
from models import db, User, Component, Request, UserRole, RequestStatus

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL', 'postgresql://lablink:lablink@localhost:5432/lablink')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_users():
    """Create initial faculty and student users"""
    print("Creating users...")
    
    users_data = [
        {
            'username': 'faculty',
            'email': 'faculty@lablink.edu',
            'password': 'faculty123',
            'role': UserRole.FACULTY
        },
        {
            'username': 'student',
            'email': 'student@lablink.edu',
            'password': 'student123',
            'role': UserRole.STUDENT
        },
        {
            'username': 'john_doe',
            'email': 'john.doe@lablink.edu',
            'password': 'student123',
            'role': UserRole.STUDENT
        },
        {
            'username': 'jane_smith',
            'email': 'jane.smith@lablink.edu',
            'password': 'student123',
            'role': UserRole.STUDENT
        },
        {
            'username': 'prof_wilson',
            'email': 'wilson@lablink.edu',
            'password': 'faculty123',
            'role': UserRole.FACULTY
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"  ⚠ User '{user_data['username']}' already exists, skipping...")
            created_users.append(existing_user)
            continue
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=hash_password(user_data['password']),
            role=user_data['role']
        )
        db.session.add(user)
        created_users.append(user)
        print(f"  ✓ Created {user_data['role'].value}: {user_data['username']}")
    
    db.session.commit()
    print(f"✓ Created {len(created_users)} users\n")
    return created_users

def seed_components():
    """Add sample components (Arduino boards, sensors, cables, modules)"""
    print("Creating components...")
    
    components_data = [
        # Arduino Boards
        {
            'name': 'Arduino Uno R3',
            'type': 'Microcontroller',
            'quantity': 15,
            'description': 'ATmega328P based microcontroller board with 14 digital I/O pins',
            'location': 'Rack A, Shelf 1'
        },
        {
            'name': 'Arduino Mega 2560',
            'type': 'Microcontroller',
            'quantity': 8,
            'description': 'ATmega2560 based board with 54 digital I/O pins and 16 analog inputs',
            'location': 'Rack A, Shelf 1'
        },
        {
            'name': 'Arduino Nano',
            'type': 'Microcontroller',
            'quantity': 20,
            'description': 'Compact ATmega328P board, breadboard-friendly',
            'location': 'Rack A, Shelf 2'
        },
        
        # Sensors
        {
            'name': 'DHT22 Temperature & Humidity Sensor',
            'type': 'Sensor',
            'quantity': 25,
            'description': 'Digital temperature and humidity sensor with high accuracy',
            'location': 'Rack B, Shelf 1'
        },
        {
            'name': 'HC-SR04 Ultrasonic Sensor',
            'type': 'Sensor',
            'quantity': 30,
            'description': 'Ultrasonic distance sensor, range 2cm to 400cm',
            'location': 'Rack B, Shelf 1'
        },
        {
            'name': 'PIR Motion Sensor',
            'type': 'Sensor',
            'quantity': 18,
            'description': 'Passive infrared motion detection sensor',
            'location': 'Rack B, Shelf 2'
        },
        {
            'name': 'MQ-2 Gas Sensor',
            'type': 'Sensor',
            'quantity': 12,
            'description': 'Detects LPG, propane, methane, hydrogen, alcohol, smoke',
            'location': 'Rack B, Shelf 2'
        },
        {
            'name': 'BMP280 Pressure Sensor',
            'type': 'Sensor',
            'quantity': 10,
            'description': 'Barometric pressure and temperature sensor',
            'location': 'Rack B, Shelf 3'
        },
        
        # Modules
        {
            'name': 'ESP8266 WiFi Module',
            'type': 'Module',
            'quantity': 22,
            'description': 'WiFi module for IoT projects with TCP/IP stack',
            'location': 'Rack C, Shelf 1'
        },
        {
            'name': 'HC-05 Bluetooth Module',
            'type': 'Module',
            'quantity': 16,
            'description': 'Bluetooth serial communication module',
            'location': 'Rack C, Shelf 1'
        },
        {
            'name': 'L298N Motor Driver',
            'type': 'Module',
            'quantity': 14,
            'description': 'Dual H-bridge motor driver for DC motors',
            'location': 'Rack C, Shelf 2'
        },
        {
            'name': '16x2 LCD Display',
            'type': 'Display',
            'quantity': 12,
            'description': '16 character x 2 line LCD display with I2C interface',
            'location': 'Rack C, Shelf 3'
        },
        
        # Cables and Accessories
        {
            'name': 'Jumper Wires (Male-Male)',
            'type': 'Cable',
            'quantity': 50,
            'description': 'Pack of 40 jumper wires, 20cm length',
            'location': 'Rack D, Shelf 1'
        },
        {
            'name': 'Jumper Wires (Male-Female)',
            'type': 'Cable',
            'quantity': 45,
            'description': 'Pack of 40 jumper wires, 20cm length',
            'location': 'Rack D, Shelf 1'
        },
        {
            'name': 'Breadboard 830 Points',
            'type': 'Accessory',
            'quantity': 28,
            'description': 'Solderless breadboard with 830 tie points',
            'location': 'Rack D, Shelf 2'
        },
        {
            'name': 'USB Cable Type A to B',
            'type': 'Cable',
            'quantity': 20,
            'description': 'USB cable for Arduino Uno/Mega programming',
            'location': 'Rack D, Shelf 3'
        }
    ]
    
    created_components = []
    for comp_data in components_data:
        # Check if component already exists
        existing_comp = Component.query.filter_by(name=comp_data['name']).first()
        if existing_comp:
            print(f"  ⚠ Component '{comp_data['name']}' already exists, skipping...")
            created_components.append(existing_comp)
            continue
        
        component = Component(**comp_data)
        db.session.add(component)
        created_components.append(component)
        print(f"  ✓ Created: {comp_data['name']} (Qty: {comp_data['quantity']})")
    
    db.session.commit()
    print(f"✓ Created {len(created_components)} components\n")
    return created_components

def seed_requests(users, components):
    """Generate sample requests with various statuses"""
    print("Creating sample requests...")
    
    # Get student and faculty users
    students = [u for u in users if u.role == UserRole.STUDENT]
    faculty = [u for u in users if u.role == UserRole.FACULTY]
    
    if not students or not faculty or not components:
        print("  ⚠ Not enough users or components to create requests")
        return []
    
    # Create sample requests with different statuses
    requests_data = [
        # Pending requests
        {
            'student': students[0],
            'component': components[0],  # Arduino Uno
            'quantity': 2,
            'status': RequestStatus.PENDING,
            'days_ago': 1
        },
        {
            'student': students[1] if len(students) > 1 else students[0],
            'component': components[4],  # HC-SR04 Sensor
            'quantity': 3,
            'status': RequestStatus.PENDING,
            'days_ago': 2
        },
        
        # Approved requests
        {
            'student': students[0],
            'component': components[8],  # ESP8266
            'quantity': 1,
            'status': RequestStatus.APPROVED,
            'days_ago': 5,
            'processed_by': faculty[0]
        },
        {
            'student': students[1] if len(students) > 1 else students[0],
            'component': components[12],  # Jumper Wires
            'quantity': 2,
            'status': RequestStatus.APPROVED,
            'days_ago': 4,
            'processed_by': faculty[0]
        },
        
        # Rejected request
        {
            'student': students[0],
            'component': components[1],  # Arduino Mega
            'quantity': 5,
            'status': RequestStatus.REJECTED,
            'rejection_reason': 'Requested quantity exceeds project requirements',
            'days_ago': 7,
            'processed_by': faculty[0]
        },
        
        # Returned request
        {
            'student': students[1] if len(students) > 1 else students[0],
            'component': components[2],  # Arduino Nano
            'quantity': 1,
            'status': RequestStatus.RETURNED,
            'days_ago': 10,
            'processed_by': faculty[0]
        }
    ]
    
    created_requests = []
    for req_data in requests_data:
        request = Request(
            student_id=req_data['student'].id,
            component_id=req_data['component'].id,
            quantity=req_data['quantity'],
            status=req_data['status'],
            rejection_reason=req_data.get('rejection_reason'),
            requested_at=datetime.utcnow() - timedelta(days=req_data['days_ago'])
        )
        
        if 'processed_by' in req_data:
            request.processed_by = req_data['processed_by'].id
            request.processed_at = request.requested_at + timedelta(hours=2)
            
            if req_data['status'] == RequestStatus.RETURNED:
                request.returned_at = request.processed_at + timedelta(days=3)
        
        db.session.add(request)
        created_requests.append(request)
        print(f"  ✓ Created {req_data['status'].value} request: {req_data['component'].name}")
    
    db.session.commit()
    print(f"✓ Created {len(created_requests)} sample requests\n")
    return created_requests

def seed_all():
    """Seed all data"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("LabLink Database Seeding")
        print("=" * 60)
        print()
        
        # Seed users
        users = seed_users()
        
        # Seed components
        components = seed_components()
        
        # Seed requests
        requests = seed_requests(users, components)
        
        print("=" * 60)
        print("Seeding Complete!")
        print("=" * 60)
        print()
        print("Default Credentials:")
        print("  Faculty: username='faculty', password='faculty123'")
        print("  Student: username='student', password='student123'")
        print()
        print(f"Summary:")
        print(f"  - {len(users)} users created")
        print(f"  - {len(components)} components created")
        print(f"  - {len(requests)} sample requests created")
        print()

def clear_all_data():
    """Clear all data from database (use with caution!)"""
    app = create_app()
    
    with app.app_context():
        print("WARNING: This will delete all data from the database!")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() == 'yes':
            # Delete in correct order due to foreign keys
            Request.query.delete()
            Component.query.delete()
            User.query.delete()
            db.session.commit()
            print("✓ All data cleared")
        else:
            print("Operation cancelled")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_all_data()
    else:
        seed_all()
