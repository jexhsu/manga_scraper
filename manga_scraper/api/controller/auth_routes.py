from typing import Set
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    Response,
    status,
    Form,
    Query,
)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import random
import string

from ..models import User
from ..database import SessionLocal
from manga_scraper.settings import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SETUP_ADMIN_TOKEN,
    DEBUG_SETUP,
    VERSION,
)

auth_router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{VERSION}/auth/login")

# Add token blacklist (in-memory storage for revoked tokens)
token_blacklist: Set[str] = set()


# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreateUserRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True


# Utility Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: If token is invalid, expired or revoked
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication failed: Invalid or missing credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check if token is revoked
    if token in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked (logged out)",
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


# Routes
@auth_router.post(
    "/setup-admin",
    status_code=201,
    include_in_schema=DEBUG_SETUP,
)
def setup_admin(
    username: str = Form(..., description="Admin username"),
    password: str = Form(..., description="Admin password"),
    token: str = Header(..., alias="X-Setup-Token"),
    db: Session = Depends(get_db),
):
    """Endpoint for initial admin setup during development"""
    if token != SETUP_ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid setup token.")

    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    # Create new admin user
    user = User(username=username, password=hash_password(password), is_admin=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Admin created successfully."}


@auth_router.post(
    "/create-user",
    status_code=201,
    summary="Create new user (admin only)",
    description="Only admins can create new regular users with username and password.",
)
def create_user(
    username: str = Form(..., description="Username for new user"),
    password: str = Form(..., description="Password for new user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Requires admin privileges
):
    """
    Endpoint for admin to create a new non-admin user.
    """
    # Only admins allowed
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required.")

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    # Create new user with hashed password and is_admin=False
    user = User(
        username=username,
        password=hash_password(password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": f"User '{username}' created successfully."}


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Login with username and password to get JWT token.",
)
def login(
    username: str = Form(..., description="Username"),
    password: str = Form(..., description="Password"),
    db: Session = Depends(get_db),
):
    """Authentication endpoint that returns JWT token"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post(
    "/reset-password",
    summary="Reset Password",
    description="Allow a user to reset their password by providing the old and new passwords.",
)
def reset_password(
    old_password: str = Form(..., description="Old password"),
    new_password: str = Form(..., description="New password"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Requires authentication
):
    """
    Allow users to reset their password.
    """
    if not verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect.")

    # Update password in the database
    current_user.password = hash_password(new_password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password reset successfully."}


@auth_router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="Refresh JWT Token",
    description="Allow a user to refresh their expired JWT token.",
)
def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Requires authentication
):
    """
    Endpoint to refresh the JWT token if it's expired.
    """
    new_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": new_token, "token_type": "bearer"}


@auth_router.get(
    "/check-user-exists",
    summary="Check if a username exists",
    description="Check if a given username already exists in the system.",
)
def check_user_exists(
    username: str = Query(..., description="Username to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Now requires authentication
):
    """
    Check if a username already exists in the database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        return {"exists": True}
    return {"exists": False}


@auth_router.post(
    "/logout",
    summary="Logout the user",
    description="Invalidate the current JWT token and log out the user.",
    response_model=dict,
)
def logout(
    response: Response,
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Logout the current user by revoking their JWT token.

    Args:
        response: FastAPI response object
        token: JWT token to revoke
        current_user: Currently authenticated user

    Returns:
        dict: Success message

    Note:
        - Adds token to blacklist to prevent further use
        - Clears any client-side token storage via response cookies
    """
    # Add token to blacklist
    token_blacklist.add(token)

    # Clear client-side token storage
    response.delete_cookie("access_token")

    return {"message": "Successfully logged out. Token has been revoked."}


@auth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
    description="Get details of the currently authenticated user.",
)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Endpoint to get information about the currently logged in user"""
    return current_user
