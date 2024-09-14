from ..extensions import db
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model,UserMixin):
    """
    Represents a user in the platform.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """
        Sets the user's password by generating a password hash.

        Args:
            password (str): The password to be hashed.

        Returns:
            None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the user's password hash.
        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.email})>'