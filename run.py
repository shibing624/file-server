#!/usr/bin/env python3
"""
File Server Entry Point

A simple script to run the file server with proper configuration.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import HOST, PORT
from src.main import app

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
╔════════════════════════════════════════════╗
║        File Server - v1.0.0                ║
╚════════════════════════════════════════════╝

Starting server at http://{HOST}:{PORT}

Press Ctrl+C to stop
""")
    
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
