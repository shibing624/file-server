"""
Utility functions for the file server.
文件服务器的工具函数

Licensed under the Apache License, Version 2.0
"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Tuple


def verify_password(password: str, expected_password: str) -> bool:
    """
    Verify password using constant-time comparison to prevent timing attacks.
    使用常量时间比较验证密码，防止时序攻击
    """
    import hmac
    return hmac.compare_digest(password, expected_password)


def get_file_hash(content: bytes, algorithm: str = "md5") -> str:
    """
    Calculate file hash for deduplication.
    计算文件哈希用于去重
    
    Args:
        content: File content in bytes
        algorithm: Hash algorithm (md5, sha256)
    
    Returns:
        Hex digest of the hash
    """
    if algorithm == "sha256":
        return hashlib.sha256(content).hexdigest()[:16]
    return hashlib.md5(content).hexdigest()[:12]


def generate_filename(original_name: str, content: bytes) -> str:
    """
    Generate unique filename: MMDD_hash_shortname
    生成唯一文件名格式：月日_哈希_短名
    
    Args:
        original_name: Original filename
        content: File content for hash generation
    
    Returns:
        Sanitized unique filename
    """
    ext = Path(original_name).suffix.lower()
    date_prefix = datetime.now().strftime("%m%d")
    file_hash = get_file_hash(content)[:8]
    
    # Clean filename: keep ASCII alphanumeric, hyphen, underscore
    clean_name = "".join(
        c for c in Path(original_name).stem 
        if c.isascii() and (c.isalnum() or c in "-_.")
    )[:8]
    
    if not clean_name:
        clean_name = "file"
    
    return f"{date_prefix}_{file_hash}_{clean_name}{ext}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    格式化文件大小为人类可读格式
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.1f} GB"


def get_file_icon(filename: str) -> str:
    """
    Get emoji icon based on file extension.
    根据文件扩展名获取表情图标
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    
    icons = {
        # Images
        "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️", "gif": "🖼️", 
        "webp": "🖼️", "svg": "🖼️", "bmp": "🖼️", "ico": "🖼️",
        # Videos
        "mp4": "🎬", "webm": "🎬", "avi": "🎬", "mov": "🎬", 
        "mkv": "🎬", "flv": "🎬", "wmv": "🎬",
        # Audio
        "mp3": "🎵", "wav": "🎵", "ogg": "🎵", "flac": "🎵", 
        "aac": "🎵", "m4a": "🎵",
        # Documents
        "pdf": "📄", "doc": "📄", "docx": "📄", "txt": "📄", 
        "md": "📄", "rtf": "📄",
        # Spreadsheets
        "xls": "📊", "xlsx": "📊", "csv": "📊", "ods": "📊",
        # Presentations
        "ppt": "📽️", "pptx": "📽️", "odp": "📽️",
        # Archives
        "zip": "📦", "tar": "📦", "gz": "📦", "bz2": "📦", 
        "rar": "📦", "7z": "📦",
        # Code
        "html": "🌐", "css": "🎨", "js": "⚡", "ts": "⚡", 
        "py": "🐍", "java": "☕", "go": "🐹",
        "rs": "🦀", "cpp": "🔧", "c": "🔧", "h": "🔧",
        "json": "📋", "xml": "📋", "yaml": "📋", "yml": "📋",
    }
    
    return icons.get(ext, "📎")


def is_safe_path(filepath: Path, base_dir: Path) -> bool:
    """
    Check if a file path is within the allowed directory.
    检查文件路径是否在允许的目录内（防止目录遍历攻击）
    """
    try:
        return filepath.resolve().is_relative_to(base_dir.resolve())
    except Exception:
        return False


def validate_filename(filename: str) -> Tuple[bool, str]:
    """
    Validate filename for security.
    验证文件名安全性
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"
    
    # Check for path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False, "Invalid filename"
    
    # Check for hidden files
    if filename.startswith("."):
        return False, "Hidden files are not allowed"
    
    return True, ""
