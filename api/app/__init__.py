"""FastAPI application package."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .auth import router as auth_router
from .api import router as api_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
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

    # Include routers
    app.include_router(auth_router)
    app.include_router(api_router)

    # Custom OpenAPI schema to define Bearer token security
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Vercel + FastAPI",
            version="1.0.0",
            description="Vercel + FastAPI",
            routes=app.routes,
        )

        # Define Bearer token security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT access token from /auth/login endpoint"
            }
        }

        # Apply security to protected endpoints
        for path, path_item in openapi_schema.get("paths", {}).items():
            # Apply security to /api/* endpoints (all protected data endpoints)
            if path.startswith("/api/"):
                for method, operation in path_item.items():
                    if method in ["get", "post", "put", "delete", "patch"]:
                        if "security" not in operation:
                            operation["security"] = [{"bearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app
