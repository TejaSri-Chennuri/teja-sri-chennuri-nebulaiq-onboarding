"""
Zentra AI - Authentication API
"""
from datetime import timedelta
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User
from app.models.notification import NotificationPreference
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    phone_number: Optional[str] = None
    currency: str = "INR"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone_number: Optional[str]
    currency: str
    is_verified: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    currency: Optional[str] = None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=get_password_hash(request.password),
        phone_number=request.phone_number,
        currency=request.currency,
    )
    db.add(user)
    db.flush()

    # Create default notification preferences
    prefs = NotificationPreference(user_id=user.id)
    db.add(prefs)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            currency=user.currency,
            is_verified=user.is_verified,
        ),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login with email and password."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            currency=user.currency,
            is_verified=user.is_verified,
        ),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        currency=current_user.currency,
        is_verified=current_user.is_verified,
    )


@router.put("/me", response_model=UserResponse)
def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile."""
    if request.full_name:
        current_user.full_name = request.full_name
    if request.phone_number is not None:
        current_user.phone_number = request.phone_number
    if request.currency:
        current_user.currency = request.currency

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        currency=current_user.currency,
        is_verified=current_user.is_verified,
    )


@router.get("/gmail/authorize")
def gmail_authorize(current_user: User = Depends(get_current_user)):
    """Get Gmail OAuth authorization URL."""
    from google_auth_oauthlib.flow import Flow

    if not settings.GMAIL_CLIENT_ID:
        return {
            "auth_url": None,
            "message": "Gmail integration not configured. Using mock data.",
        }

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "redirect_uris": [settings.GMAIL_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    flow.redirect_uri = settings.GMAIL_REDIRECT_URI
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=str(current_user.id),
    )
    return {"auth_url": auth_url}


@router.get("/gmail/callback")
def gmail_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Gmail OAuth callback."""
    if not settings.GMAIL_CLIENT_ID:
        return {"message": "Gmail OAuth not configured"}

    try:
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )
        flow.redirect_uri = settings.GMAIL_REDIRECT_URI
        flow.fetch_token(code=code)

        credentials = flow.credentials
        user = db.query(User).filter(User.id == state).first()
        if user:
            user.gmail_access_token = credentials.token
            user.gmail_refresh_token = credentials.refresh_token
            db.commit()

        return {"message": "Gmail connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")
