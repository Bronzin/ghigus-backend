# app/api/routers/auth.py
import smtplib
import threading
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    Token,
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.db.deps import get_db, get_current_user
from app.db.models.user import User

NOTIFY_EMAIL = "alfonso.bronzin@gmail.com"


def _send_login_notification(username: str, ip: str, user_agent: str):
    """Send login notification email in a background thread."""
    if not settings.smtp_user or not settings.smtp_password:
        print("SMTP not configured, skipping login notification")
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    body = (
        f"Nuovo accesso a Ghigus\n"
        f"{'─' * 40}\n"
        f"Utente:     {username}\n"
        f"Data/ora:   {now}\n"
        f"IP:         {ip}\n"
        f"Browser:    {user_agent}\n"
    )
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = f"🔑 Ghigus – Login di {username}"
    msg["From"] = settings.smtp_user
    msg["To"] = NOTIFY_EMAIL

    def _send():
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as srv:
                srv.starttls()
                srv.login(settings.smtp_user, settings.smtp_password)
                srv.sendmail(settings.smtp_user, [NOTIFY_EMAIL], msg.as_string())
            print(f"Login notification sent for {username}")
        except Exception as exc:
            print(f"Failed to send login notification: {exc}")

    threading.Thread(target=_send, daemon=True).start()


router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible login endpoint.
    Returns a JWT access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password non corretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente disattivato",
        )

    # Send login notification email (background, non-blocking)
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    user_agent = request.headers.get("user-agent", "unknown")
    _send_login_notification(user.username, client_ip, user_agent)

    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@router.post("/setup", response_model=UserResponse)
async def setup_first_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Setup endpoint to create the first admin user.
    Only works if no users exist in the database.
    """
    existing_users = db.query(User).count()
    if existing_users > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup già completato. Utenti già presenti.",
        )

    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La password deve essere di almeno 8 caratteri",
        )

    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user
