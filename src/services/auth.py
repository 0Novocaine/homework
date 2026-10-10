"""Password hashing and JWT authentication utilities."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users

bearer_scheme = HTTPBearer(auto_error=False)


class Auth:
    """Provides password hashing, JWT creation, validation, and user resolution."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.jwt_secret_key
    ALGORITHM = settings.jwt_algorithm

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies a plain-text password against its hashed value.

        :param plain_password: The password supplied by the user.
        :type plain_password: str
        :param hashed_password: The stored password hash.
        :type hashed_password: str
        :return: True when the password matches the hash.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Creates a secure hash for a password.

        :param password: The plain-text password to hash.
        :type password: str
        :return: The generated password hash.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    def create_email_token(self, data: dict):
        """
        Creates a JWT token used to confirm an email address.

        :param data: The payload to include in the token.
        :type data: dict
        :return: A signed email confirmation token valid for seven days.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Extracts an email address from a valid email confirmation token.

        :param token: The email confirmation token.
        :type token: str
        :return: The email address stored in the token subject.
        :rtype: str
        :raises HTTPException: If the token is invalid or has no email subject.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid token for email verification",
                )
            return email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a signed JWT access token.

        :param data: The payload to include in the token.
        :type data: dict
        :param expires_delta: Optional token lifetime in seconds.
        :type expires_delta: float | None
        :return: A signed access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "jti": str(uuid4()),
                "scope": "access_token",
            }
        )
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a signed JWT refresh token.

        :param data: The payload to include in the token.
        :type data: dict
        :param expires_delta: Optional token lifetime in seconds.
        :type expires_delta: float | None
        :return: A signed refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "jti": str(uuid4()),
                "scope": "refresh_token",
            }
        )
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Validates a refresh token and returns the email in its subject.

        :param refresh_token: The refresh token to validate.
        :type refresh_token: str
        :return: The email address stored in the token subject.
        :rtype: str
        :raises HTTPException: If the token is invalid or has an incorrect scope.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "refresh_token":
                email = payload.get("sub")
                if email is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
        db: Session = Depends(get_db),
    ):
        """
        Resolves the current user from a valid bearer access token.

        :param credentials: The bearer token credentials.
        :type credentials: HTTPAuthorizationCredentials | None
        :param db: The database session.
        :type db: Session
        :return: The authenticated user.
        :rtype: User
        :raises HTTPException: If the credentials are missing, invalid, or reference no user.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if credentials is None:
            raise credentials_exception

        try:
            # Decode JWT
            payload = jwt.decode(credentials.credentials, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user



auth_service = Auth()
