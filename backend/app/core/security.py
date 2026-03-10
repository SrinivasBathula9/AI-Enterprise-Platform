import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Argon2id — winner of the Password Hashing Competition (PHC).
# Industry standard for new systems. Resistant to GPU/ASIC brute-force
# and side-channel attacks. Replaces bcrypt.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Access token (JWT, short-lived, in-memory on client) ─────────────────────

def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and verify an access token. Raises JWTError on failure."""
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    if payload.get("type") != "access":
        raise JWTError("Not an access token")
    return payload


# ── Refresh token (opaque random bytes, stored as SHA-256 hash in DB) ────────

def generate_refresh_token() -> str:
    """Cryptographically secure 32-byte URL-safe token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """SHA-256 hash a token for secure DB storage (raw token never persisted)."""
    return hashlib.sha256(token.encode()).hexdigest()


def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )


# ── Password-reset token ──────────────────────────────────────────────────────

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def reset_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)
