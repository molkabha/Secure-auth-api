from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreate, UserResponse, Token, LoginRequest, RefreshTokenRequest
from ..crud import create_user, get_user_by_email, get_user_by_username, get_user_by_credentials
from ..auth import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    validate_refresh_token,
    revoke_refresh_token
)
from ..config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    return create_user(db=db, user=user)


@router.post("/login", response_model=Token)
def login(user_credentials: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_credentials(db, username=user_credentials.username)
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(db, user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    user = validate_refresh_token(db, token_request.refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    revoke_refresh_token(db, token_request.refresh_token)
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(db, user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )

