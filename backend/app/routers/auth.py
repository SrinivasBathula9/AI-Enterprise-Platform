from datetime import timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from jose import JWTError
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    generate_reset_token,
    hash_password,
    hash_token,
    refresh_token_expiry,
    reset_token_expiry,
    verify_password,
)
from app.dependencies import get_current_user, get_db
from app.models.user import PasswordResetToken, RefreshToken, User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
settings = get_settings()

_COOKIE_NAME = "refresh_token"
_COOKIE_PATH = "/api/v1/auth"


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        path=_COOKIE_PATH,
        max_age=settings.refresh_token_expire_days * 86400,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_COOKIE_NAME, path=_COOKIE_PATH)


async def _issue_tokens(
    user: User,
    db: AsyncSession,
    response: Response,
    request: Request,
) -> TokenResponse:
    """Create access token + refresh token, persist refresh token, set cookie."""
    raw_refresh = generate_refresh_token()
    token_hash = hash_token(raw_refresh)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=refresh_token_expiry(),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(db_token)
    await db.commit()

    _set_refresh_cookie(response, raw_refresh)
    access_token = create_access_token(str(user.id), user.email)
    return TokenResponse(access_token=access_token)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse(id=str(user.id), email=user.email, full_name=user.full_name)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    # Constant-time failure — same error for unknown email and wrong password
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return await _issue_tokens(user, db, response, request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=_COOKIE_NAME),
) -> TokenResponse:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    db_token = result.scalar_one_or_none()

    from datetime import datetime
    now = datetime.now(timezone.utc)

    if (
        not db_token
        or db_token.revoked
        or db_token.expires_at.replace(tzinfo=timezone.utc) < now
    ):
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    # Rotate: revoke the used token before issuing a new one
    db_token.revoked = True
    db_token.revoked_at = now
    await db.flush()

    user_result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail="User not found or disabled")

    return await _issue_tokens(user, db, response, request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=_COOKIE_NAME),
) -> None:
    if refresh_token:
        token_hash = hash_token(refresh_token)
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        db_token = result.scalar_one_or_none()
        if db_token and not db_token.revoked:
            from datetime import datetime
            db_token.revoked = True
            db_token.revoked_at = datetime.now(timezone.utc)
            await db.commit()
    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserResponse)
async def me(
    current: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    result = await db.execute(select(User).where(User.id == current["user_id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=str(user.id), email=user.email, full_name=user.full_name)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    # Always return 200 to prevent email enumeration
    if not user:
        return {"message": "If that email exists, a reset link has been sent"}

    raw_token = generate_reset_token()
    db_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        expires_at=reset_token_expiry(),
    )
    db.add(db_token)
    await db.commit()

    # In production: send email with reset link containing raw_token
    # For development: log the token so it can be used directly
    reset_link = f"{settings.frontend_url}/update-password?token={raw_token}"
    print(f"[DEV] Password reset link for {user.email}: {reset_link}")

    return {"message": "If that email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from datetime import datetime
    now = datetime.now(timezone.utc)

    token_hash = hash_token(body.token)
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    db_token = result.scalar_one_or_none()

    if (
        not db_token
        or db_token.used
        or db_token.expires_at.replace(tzinfo=timezone.utc) < now
    ):
        raise HTTPException(status_code=400, detail="Reset token invalid or expired")

    user_result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(body.new_password)
    db_token.used = True

    # Revoke all existing refresh tokens to force re-login everywhere
    existing_tokens = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id, RefreshToken.revoked == False  # noqa: E712
        )
    )
    for rt in existing_tokens.scalars().all():
        rt.revoked = True
        rt.revoked_at = now

    await db.commit()
    return {"message": "Password updated successfully"}
