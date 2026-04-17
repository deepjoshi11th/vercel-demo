"""Shared dependencies for authentication and authorization."""
from fastapi import Depends, Header, HTTPException, status
from typing import Optional
from .config import supabase


def get_auth_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract and validate Bearer token from Authorization header.
    Returns only the token string (without 'Bearer' prefix).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


async def get_current_user(token: str = Depends(get_auth_header)) -> dict:
    """
    Validate JWT token with Supabase and return user data.
    Uses get_auth_header to extract and validate the Authorization header.
    """
    try:
        response = supabase.auth.get_user(token)
        return response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
