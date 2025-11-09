"""
Database models for LabLink System
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SQLEnum
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    FACULTY = "faculty"


class RequestStatus(enum.Enum):
    """Request status enumeration"""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    RETURNED = "Returned"


class ActionType(enum.Enum):
    """Transaction action type enumeration"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    REQUEST = "REQUEST"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    RETURN = "RETURN"


class EntityType(enum.Enum):
    """Transaction entity type enumeration"""
    COMPONENT = "Component"
    REQUEST = "Request"
    USER = "User"


class User(db.Model):
    """User model for students and faculty"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(SQLEnum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    requests = db.relationship('Request', foreign_keys='Request.student_id', backref='student', lazy='dynamic')
    processed_requests = db.relationship('Request', foreign_keys='Request.processed_by', backref='processor', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat()
        }


class Component(db.Model):
    """Component model for laboratory inventory items"""
    __tablename__ = 'components'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    requests = db.relationship('Request', backref='component', lazy='dynamic')
    
    def __repr__(self):
        return f'<Component {self.name} ({self.quantity} available)>'
    
    def to_dict(self):
        """Convert component to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'quantity': self.quantity,
            'description': self.description,
            'image_url': self.image_url,
            'location': self.location,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Request(db.Model):
    """Request model for component borrowing requests"""
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(SQLEnum(RequestStatus), nullable=False, default=RequestStatus.Pending, index=True)
    rejection_reason = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    returned_at = db.Column(db.DateTime)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='request', lazy='dynamic',
                                   primaryjoin="and_(Transaction.entity_type=='Request', "
                                              "foreign(Transaction.entity_id)==Request.id)")
    
    def __repr__(self):
        return f'<Request {self.id} - {self.status.value}>'
    
    def to_dict(self, include_relations=False):
        """Convert request to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'component_id': self.component_id,
            'quantity': self.quantity,
            'status': self.status.value,
            'rejection_reason': self.rejection_reason,
            'requested_at': self.requested_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processed_by': self.processed_by,
            'returned_at': self.returned_at.isoformat() if self.returned_at else None
        }
        
        if include_relations:
            data['student'] = self.student.to_dict() if self.student else None
            data['component'] = self.component.to_dict() if self.component else None
            data['processor'] = self.processor.to_dict() if self.processor else None
        
        return data


class Transaction(db.Model):
    """Transaction model for audit logging"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action_type = db.Column(SQLEnum(ActionType), nullable=False, index=True)
    entity_type = db.Column(SQLEnum(EntityType), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<Transaction {self.action_type.value} on {self.entity_type.value} {self.entity_id}>'
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type.value,
            'entity_type': self.entity_type.value,
            'entity_id': self.entity_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
