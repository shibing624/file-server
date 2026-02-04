"""
Configuration management for the file server.
文件服务器的配置管理

Licensed under the Apache License, Version 2.0
"""
import os
from pathlib import Path
from typing import Set


def get_env_str(key: str, default: str) -> str:
    """Get string from environment variable."""
    return os.getenv(key, default)


def get_env_int(key: str, default: int) -> int:
    """Get integer from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean from environment variable."""
    value = os.getenv(key, str(default).lower()).lower()
    return value in ("true", "1", "yes", "on")


def get_env_set(key: str, default: Set[str]) -> Set[str]:
    """Get set of strings from comma-separated environment variable."""
    value = os.getenv(key)
    if value:
        return set(ext.strip().lower() for ext in value.split(","))
    return default


# Server configuration
HOST: str = get_env_str("HOST", "0.0.0.0")
PORT: int = get_env_int("PORT", 8008)

# Security
UPLOAD_PASSWORD: str = get_env_str("UPLOAD_PASSWORD", "123456")
if not UPLOAD_PASSWORD:
    import secrets
    UPLOAD_PASSWORD = secrets.token_urlsafe(16)
    print(f"Warning: Using auto-generated password: {UPLOAD_PASSWORD}")

# Storage - default to home directory for easy local development
DEFAULT_STORAGE_DIR = Path.home() / "data" / "file-server" 
STORAGE_DIR: Path = Path(get_env_str("STORAGE_DIR", str(DEFAULT_STORAGE_DIR)))
BASE_URL: str = get_env_str("BASE_URL", "http://localhost:8008").rstrip("/")

# File limits
MAX_FILE_SIZE: int = get_env_int("MAX_FILE_SIZE", 500 * 1024 * 1024)  # 500MB

# Blocked extensions (security)
BLOCKED_EXTENSIONS: Set[str] = get_env_set(
    "BLOCKED_EXTENSIONS",
    {
        ".exe", ".dll", ".bat", ".cmd", ".sh", ".ps1",
        ".msi", ".scr", ".com", ".vbs", ".vbe", ".wsf",
        ".jar", ".war", ".ear",
    }
)

# Logging
LOG_LEVEL: str = get_env_str("LOG_LEVEL", "INFO").upper()

# Ensure storage directory exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
