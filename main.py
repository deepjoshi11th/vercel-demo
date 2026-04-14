from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import jwt
from supabase import create_client, Client
from datetime import datetime
from typing import Optional


app = FastAPI(
    title="Vercel + FastAPI",
    description="Vercel + FastAPI",
    version="1.0.0",
)

# Add CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url: str = str(os.environ.get("SUPABASE_URL"))
key: str = str(os.environ.get("SUPABASE_SECRET_KEY"))
anon_key: str = str(os.environ.get("SUPABASE_ANON_KEY", ""))
supabase: Client = create_client(url, key)


# Request/Response Models
class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str


class ProfileDetailsRequest(BaseModel):
    sensitive_part: str


class ProfileDetailsResponse(BaseModel):
    id: str
    sensitive_part: str

# Protected Data Endpoints
def get_auth_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract authorization header from request."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization


# JWT validation function
async def get_current_user(authorization: Optional[str] = None) -> dict:
    """
    Extracts and validates JWT token from Authorization header.
    Returns user data if valid, raises 401 if invalid.
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

    try:
        # Verify token with Supabase
        response = supabase.auth.get_user(token)
        return response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authentication Endpoints
@app.post("/auth/signup", response_model=dict)
async def signup(request: SignupRequest):
    """
    Sign up with email and password.
    """
    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })
        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
            "session": {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            } if response.session else None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}",
        )


@app.post("/auth/login", response_model=dict)
async def login(request: LoginRequest):
    """
    Log in with email and password.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })
        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
            "session": {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}",
        )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(authorization: str = Depends(get_auth_header)):
    """
    Get current authenticated user profile.
    """
    user = await get_current_user(authorization)
    return UserResponse(
        id=user.id,
        email=user.email,
    )


@app.post("/auth/logout")
async def logout():
    """
    Logout endpoint (token invalidation happens on client side).
    """
    return {"message": "Logged out successfully"}


@app.get("/api/data")
async def get_sample_data(authorization: str = Depends(get_auth_header)):
    """
    Get all sample data (requires authentication).
    RLS policies on sample_table will restrict data based on user context.
    """
    try:
        user = await get_current_user(authorization)
        print("DEBUG - Fetching data for user:", type(user))  # Debugging statement
        # Create client with user's token for RLS to apply
        user_client = create_client(url, key)
        response = user_client.table("sample_table").select("*").execute()
        data = response.data
        return {
            "data": data,
            "total": len(data),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch data: {str(e)}",
        )


@app.get("/api/items/{item_id}")
async def get_item(item_id: int, authorization: str = Depends(get_auth_header)):
    """
    Get specific item by ID (requires authentication).
    RLS policies will enforce user access control.
    """
    try:
        user = await get_current_user(authorization)
        user_client = create_client(url, key)
        response = user_client.table("sample_table").select("*").eq("id", item_id).execute()
        data = response.data
        if data:
            item = data[0]
            return {
                "item": item,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {"error": "Item not found"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch item: {str(e)}",
        )


@app.post("/api/profile-details")
async def update_profile_details(
    request: ProfileDetailsRequest,
    authorization: str = Depends(get_auth_header)
):
    """
    Create or update profile details for authenticated user.
    Uses RLS to ensure users can only modify their own data.
    """
    try:
        user = await get_current_user(authorization)
        user_client = create_client(url, key)

        # Upsert profile details - insert if doesn't exist, update if it does
        response = user_client.table("profile_details").upsert({
            "id": user.id,
            "sensetive_part": request.sensitive_part
        }).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "id": response.data[0]["id"],
                    "sensitive_part": response.data[0]["sensetive_part"]
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            raise Exception("Failed to save profile details")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile details: {str(e)}",
        )


@app.get("/api/profile-details")
async def get_profile_details(authorization: str = Depends(get_auth_header)):
    """
    Get profile details for authenticated user.
    RLS ensures users can only see their own data.
    """
    try:
        user = await get_current_user(authorization)
        user_client = create_client(url, key)

        response = user_client.table("profile_details").select("*").eq("id", user.id).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "id": response.data[0]["id"],
                    "sensitive_part": response.data[0]["sensetive_part"]
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {
                "success": True,
                "data": None,
                "message": "No profile details found",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch profile details: {str(e)}",
        )


@app.get("/")
def read_root():
    return FileResponse("index.html")


# Mount static files (CSS, JS) - must be after all routes
app.mount("/", StaticFiles(directory=".", html=False), name="static")
