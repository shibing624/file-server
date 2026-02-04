"""
File Server - A simple self-hosted file storage service.
文件服务器 - 简单的自托管文件存储服务

Features:
- Password-protected uploads
- Web interface and RESTful API
- File listing and management
- Multiple file format support

Author: Xu Ming
License: Apache 2.0
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import (
    HOST, PORT, UPLOAD_PASSWORD, STORAGE_DIR, BASE_URL,
    MAX_FILE_SIZE, BLOCKED_EXTENSIONS, LOG_LEVEL
)
from .utils import (
    verify_password, generate_filename, format_file_size,
    get_file_icon, is_safe_path, validate_filename
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting File Server v{__version__}")
    logger.info(f"Storage directory: {STORAGE_DIR}")
    yield
    logger.info("Shutting down File Server")


app = FastAPI(
    title="File Server",
    description="A simple self-hosted file storage service",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/files", StaticFiles(directory=str(STORAGE_DIR)), name="files")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/", response_class=HTMLResponse)
async def index():
    """Web upload interface."""
    html_content = (Path(__file__).parent / "static" / "index.html").read_text()
    return HTMLResponse(content=html_content)


@app.post("/upload")
async def upload_file(
    password: str = Form(..., description="Upload password"),
    file: UploadFile = File(..., description="File to upload")
):
    """
    Upload a file to the server.
    
    - **password**: Required upload password
    - **file**: File to upload (max 500MB)
    
    Returns:
        - **url**: Direct access URL
        - **filename**: Generated filename
        - **size**: File size in bytes
    """
    # Verify password
    if not verify_password(password, UPLOAD_PASSWORD):
        logger.warning(f"Upload attempt with wrong password from file: {file.filename}")
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Check file type
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext in BLOCKED_EXTENSIONS:
        logger.warning(f"Blocked file type upload: {ext}")
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed: {ext}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {format_file_size(MAX_FILE_SIZE)}"
        )
    
    # Generate safe filename
    filename = generate_filename(file.filename, content)
    filepath = STORAGE_DIR / filename
    
    # Save file
    try:
        with open(filepath, "wb") as f:
            f.write(content)
        logger.info(f"File uploaded: {filename} ({format_file_size(len(content))})")
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Return URL
    url = f"{BASE_URL}/files/{filename}"
    return {
        "url": url,
        "filename": filename,
        "size": len(content),
        "message": "Upload successful"
    }


@app.get("/list")
async def list_files(password: str = Query(..., description="Access password")):
    """
    List all uploaded files.
    
    - **password**: Required access password
    
    Returns:
        - **files**: List of file information
        - **total**: Total number of files
    """
    if not verify_password(password, UPLOAD_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    if not STORAGE_DIR.exists():
        return {"files": [], "total": 0}
    
    files = []
    try:
        for f in STORAGE_DIR.iterdir():
            if f.is_file():
                try:
                    stat = f.stat()
                    files.append({
                        "name": f.name,
                        "url": f"{BASE_URL}/files/{f.name}",
                        "size": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "icon": get_file_icon(f.name),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Failed to read directory: {e}")
        raise HTTPException(status_code=500, detail="Failed to read file list")
    
    # Sort by creation time (newest first)
    files.sort(key=lambda x: x["created"], reverse=True)
    
    return {"files": files, "total": len(files)}


@app.delete("/delete/{filename}")
async def delete_file(
    filename: str,
    password: str = Query(..., description="Access password")
):
    """
    Delete a file.
    
    - **filename**: Name of the file to delete
    - **password**: Required access password
    """
    if not verify_password(password, UPLOAD_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Validate filename
    is_valid, error = validate_filename(filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    filepath = STORAGE_DIR / filename
    
    # Security check
    if not is_safe_path(filepath, STORAGE_DIR):
        logger.warning(f"Path traversal attempt: {filename}")
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        filepath.unlink()
        logger.info(f"File deleted: {filename}")
        return {"message": f"Deleted: {filename}"}
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "File Server API",
        "version": __version__,
        "endpoints": {
            "upload": {"method": "POST", "path": "/upload", "auth": "password"},
            "list": {"method": "GET", "path": "/list", "auth": "password"},
            "delete": {"method": "DELETE", "path": "/delete/{filename}", "auth": "password"},
            "health": {"method": "GET", "path": "/health", "auth": "none"}
        },
        "limits": {
            "max_file_size": MAX_FILE_SIZE,
            "max_file_size_formatted": format_file_size(MAX_FILE_SIZE)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
