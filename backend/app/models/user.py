from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
import re

class UserSchema(Schema):
    """
    Validation schema for user data.
    
    Provides comprehensive validation for user registration and updates,
    ensuring data integrity and security requirements are met.
    """
    # Primary key (read-only)
    id = fields.Integer(dump_only=True)
    
    # Username validation
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=100, error="Username must be between 3 and 100 characters long."),
            validate.Regexp(
                r'^[a-zA-Z0-9_.-]+$',
                error="Username can only contain letters, numbers, periods, underscores, and hyphens."
            )
        ]
    )
    
    # Email validation
    email = fields.Email(
        required=True,
        validate=validate.Length(max=120, error="Email must be 120 characters or less.")
    )
    
    # Password validation (not stored directly, used for validation only)
    password = fields.String(
        required=True,
        load_only=True,
        validate=[
            validate.Length(min=8, error="Password must be at least 8 characters long.")
        ]
    )
    
    # Password confirmation field for registration
    password_confirm = fields.String(
        required=False,
        load_only=True # Never include in serialized output
    )
    
    # Password hash is never exposed or loaded directly
    password_hash = fields.String(dump_only=True)
    
    @validates("password")
    def validate_password_strength(self, value):
        """Validate password has required complexity."""
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in value):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        # Check for at least one digit
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one number.")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character.")
        
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validate that password and password_confirm match if both provided."""
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.", field_name="password_confirm")
        
    # Define custom schema context for different validation scenarios
    class Meta:
        """Meta options for the UserSchema."""
        # Fields to include by default in serialized output
        fields = ("id", "username", "email")

class User(db.Model):
    """User model for authentication & preferences."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Checks the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"
    