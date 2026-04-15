"""FastAPI application entry point."""
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .app import create_app


app = create_app()


@app.get("/")
def read_root():
    """Serve index.html for root path."""
    return FileResponse("frontend/index.html")


# Mount static files (CSS, JS) - must be after all routes
app.mount("/", StaticFiles(directory="../frontend", html=False), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
