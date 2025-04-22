# Import models for easier access
from models.data_host import DataHost

# Import User class directly to avoid circular imports
from flask_login import UserMixin
import json
import config

class User(UserMixin):
    """User model with remember me functionality"""

    def __init__(self, id):
        """
        Initialize a user

        Args:
            id (str): User ID
        """
        self.id = id
        self.remember = False

    def get_id(self):
        """
        Get user ID

        Returns:
            str: User ID
        """
        return self.id

    @staticmethod
    def load_users():
        """
        Load users from JSON file

        Returns:
            dict: Dictionary of users with username as key and password as value
        """
        with open(config.USERS_FILE_PATH, 'r') as f:
            return json.load(f)

    @classmethod
    def get_user(cls, user_id):
        """
        Get user by ID

        Args:
            user_id (str): User ID

        Returns:
            User: User object if found, None otherwise
        """
        users = cls.load_users()
        if user_id in users:
            return cls(user_id)
        return None

    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticate user

        Args:
            username (str): Username
            password (str): Password

        Returns:
            User: User object if authentication successful, None otherwise
        """
        users = cls.load_users()
        if username in users and users[username] == password:
            return cls(username)
        return None
