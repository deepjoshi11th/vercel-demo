"""FastAPI application entry point."""
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from .app import create_app


app = create_app()

# Determine the base directory for serving static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@app.get("/")
def read_root():
    """Serve index.html for root path."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)


# Mount static files (CSS, JS) - must be after all routes
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
