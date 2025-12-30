from database import SessionLocal
from datetime import timedelta, datetime, timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.engine import create
from models import Users
import bcrypt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

# openssl rand -hex 32
SECRET_KEY = "9b2468f687b8e512948ff1811854779f9a5dd772635513c9df497e359bc1176b"
ALGORITHM = "HS256"

# Bcrypt configuration
BCRYPT_ROUNDS = 12
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    """
    Database dependency that creates a new database session for each request.
    Yields the session and automatically closes it when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    """
    Creates a JWT access token with user information and expiration time.
    Token contains username, user_id, and expires in UTC timezone.
    """
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticates a user by verifying username and password.
    Returns the User object if credentials are valid, False otherwise.
    """
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    try:
        # Verify password using bcrypt
        # Both password and hash need to be bytes
        password_bytes = password.encode('utf-8')
        hash_bytes = user.hashed_password.encode('utf-8')
        if not bcrypt.checkpw(password_bytes, hash_bytes):
            return False
        # Ensure user attributes are loaded (access them to trigger lazy loading if needed)
        _ = user.id, user.username
        return user
    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return False


db_dependency = Annotated[Session, Depends(get_db)]


class Token(BaseModel):
    """
    OAuth2 token response model.
    Contains the JWT access token and token type (always 'bearer').
    """

    access_token: str
    token_type: str


class CreateUserRequest(BaseModel):
    """
    Request model for user registration.
    Validates all required fields for creating a new user account.
    """

    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """
    Register a new user account.
    Hashes the password using bcrypt before storing in database.
    """
    # Hash password using bcrypt
    hashed_password = bcrypt.hashpw(
        create_user_request.password.encode('utf-8'),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode('utf-8')
    
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(create_user_model)
    db.commit()
    return {f"{create_user_model.username}": "Created"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    """
    OAuth2 compatible login endpoint that returns a JWT access token.
    Validates user credentials and returns token valid for 20 minutes.
    """
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        # Extract user attributes while session is still active
        username = user.username
        user_id = user.id
        token = create_access_token(username, user_id, timedelta(minutes=20))
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        error_msg = f"Login error: {type(e).__name__}: {e}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Dependency that extracts and validates JWT token from Authorization header.
    Returns user information (username, id) if token is valid, raises 401 otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return {"username": username, "id": user_id}
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate the user",
        )
