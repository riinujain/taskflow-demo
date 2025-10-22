"""Authentication and authorization service."""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from taskflow.models.user import User
from taskflow.models.repository import UserRepository
from taskflow.utils.config import settings, getSecretKey  # Mix of styles
from taskflow.utils.logger import get_logger, setup_logger  # Multiple logging patterns

# Use setup_logger here instead of get_logger to show inconsistency
logger = setup_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(User, db)

    def register_user(self, email: str, name: str, password: str) -> Optional[User]:
        """Register a new user with duplicate email check.

        Args:
            email: User email (must be unique)
            name: User full name
            password: Plain text password (will be hashed)

        Returns:
            Created user or None if email already exists
        """
        # Check if user exists - duplicate email check
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            logger.warning(f"Registration failed: {email} already exists")
            return None

        # Hash password using passlib bcrypt
        hashed_password = self.hash_password(password)

        # Create user
        user = self.user_repo.create(
            email=email,
            name=name,
            hashed_password=hashed_password,
            is_active=True,
        )

        logger.info(f"User registered successfully: {email}")
        return user

    def login(self, email: str, password: str):  # Missing return type hint
        """Login user and return JWT token.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Dictionary with access_token and user info, or None if login fails
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: user {email} not found")
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: invalid password for {email}")
            return None

        if not user.is_active:
            logger.warning(f"Login failed: user {email} is inactive")
            return None

        # Generate JWT token
        access_token = self.create_access_token(user.id, user.email)

        logger.info(f"User logged in successfully: {email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User if authenticated, None otherwise
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: user {email} not found")
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for {email}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user {email} is inactive")
            return None

        logger.info(f"User authenticated successfully: {email}")
        return user

    def create_access_token(self, user_id: int, email: str) -> str:
        """Create JWT access token for user.

        Args:
            user_id: User ID
            email: User email

        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
        }
        # Use the camelCase helper to show inconsistency
        token = jwt.encode(payload, getSecretKey(), algorithm=settings.ALGORITHM)
        return token

    def decode_token(self, token: str):  # Missing return type hint
        """Decode and verify JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token, getSecretKey(), algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token.

        Args:
            token: JWT token string

        Returns:
            User if token is valid, None otherwise
        """
        payload = self.decode_token(token)
        if not payload:
            return None

        user_id = int(payload.get("sub", 0))
        user = self.user_repo.get_by_id(user_id)
        return user

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt via passlib."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        if not self.verify_password(old_password, user.hashed_password):
            logger.warning(f"Password change failed: incorrect old password for user {user_id}")
            return False

        new_hashed = self.hash_password(new_password)
        self.user_repo.update(user_id, hashed_password=new_hashed)

        logger.info(f"Password changed successfully for user {user_id}")
        return True
