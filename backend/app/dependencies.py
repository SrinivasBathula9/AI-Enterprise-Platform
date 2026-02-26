from typing import AsyncGenerator

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal

settings = get_settings()
bearer_scheme = HTTPBearer()

# Simple global cache for JWKS to avoid redundant lookups
_JWKS_CACHE: dict | None = None


async def get_jwks() -> dict:
    global _JWKS_CACHE
    if _JWKS_CACHE is None:
        if not settings.supabase_url:
            print("Warning: SUPABASE_URL not set, cannot fetch JWKS")
            return {"keys": []}
        
        jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        print(f"Fetching JWKS from {jwks_url}")
        headers = {"apikey": settings.supabase_anon_key}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(jwks_url, headers=headers, timeout=10)
                resp.raise_for_status()
                _JWKS_CACHE = resp.json()
                print(f"Successfully cached {len(_JWKS_CACHE.get('keys', []))} keys from JWKS")
            except Exception as e:
                print(f"Failed to fetch JWKS: {e}")
                return {"keys": []}
    return _JWKS_CACHE


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")
        
        if alg.startswith("HS"):
            # Symmetric verification using the secret
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[alg],
                options={"verify_aud": False},
            )
        else:
            # Asymmetric verification using JWKS
            jwks = await get_jwks()
            kid = header.get("kid")
            key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
            
            if not key:
                print(f"Auth failed: Key ID '{kid}' not found in JWKS")
                raise credentials_exception
            
            payload = jwt.decode(
                token,
                key,
                algorithms=[alg],
                options={"verify_aud": False},
            )

        user_id: str = payload.get("sub")
        if user_id is None:
            print(f"Auth failed: No 'sub' in payload: {payload}")
            raise credentials_exception
            
        return {"user_id": user_id, "email": payload.get("email", ""), "payload": payload}
        
    except JWTError as e:
        print(f"Auth failed: JWT decoding error: {e}")
        try:
            header = jwt.get_unverified_header(token)
            print(f"Token Header: {header}")
        except Exception:
            pass
        raise credentials_exception
    except Exception as e:
        print(f"Auth failed: Unexpected error: {e}")
        raise credentials_exception
