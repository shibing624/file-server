# File Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

[中文](README_CN.md)

**File Server**: A simple, self-hosted file storage service with password protection.

file-server is a lightweight file storage solution that provides:
- Password-protected file uploads
- Web interface and RESTful API
- File listing and management
- Multiple file format support

Why file-server?
- **Simple**: Minimal setup, easy to deploy
- **Secure**: Password authentication for uploads
- **Fast**: Built with FastAPI for high performance
- **Flexible**: Web UI and API access

## Features

| Feature | Description |
|---------|-------------|
| Upload | Password-protected file uploads via web or API |
| Storage | Local file system storage with configurable path |
| Management | List, view, and delete files |
| API | RESTful API for programmatic access |
| Security | File type validation and path traversal protection |

## Installation

```bash
git clone https://github.com/shibing624/file-server.git
cd file-server
pip install -r requirements.txt
```

## Quick Start

1. Configure environment variables:

```bash
cp .env.example .env
# Edit .env and set UPLOAD_PASSWORD
```

2. Run the server:

```bash
python run.py
```

Or using uvicorn directly:

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8008
```

3. Access the web interface at `http://localhost:8008`

## API Usage

### Upload File

```bash
curl -F "password=your_password" -F "file=@image.png" http://localhost:8008/upload
```

Response:
```json
{
  "url": "http://localhost:8008/files/0204_a1b2c3d4_image.png",
  "filename": "0204_a1b2c3d4_image.png",
  "size": 123456,
  "message": "Upload successful"
}
```

### List Files

```bash
curl "http://localhost:8008/list?password=your_password"
```

### Delete File

```bash
curl -X DELETE "http://localhost:8008/delete/filename.png?password=your_password"
```

## Configuration

Configuration via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `UPLOAD_PASSWORD` | - | Required upload password |
| `STORAGE_DIR` | `~/.file-server/data` | File storage path |
| `BASE_URL` | `http://localhost:8008` | Public access URL |
| `MAX_FILE_SIZE` | `524288000` | Max file size in bytes (500MB) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8008` | Server port |

## Deployment

### Using deploy.sh

```bash
# Edit .env configuration
nano .env

# Run deployment
chmod +x deploy.sh
sudo ./deploy.sh
```

### Using Docker

```bash
docker-compose up -d
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name files.example.com;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Community & Support

- **GitHub Issues**: [Submit an issue](https://github.com/shibing624/file-server/issues)
- **Email**: [shibing624@126.com](mailto:shibing624@126.com)
- **WeChat**: Add `xuming624` with note "llm" to join the LLM tech wechat group

<img src="https://github.com/shibing624/graphrag-lite/raw/main/docs/wechat.jpeg" width="200"/>

## Citation

```bibtex
@software{file-server,
  author = {Xu Ming},
  title = {File Server: Self-hosted file storage service},
  year = {2026},
  url = {https://github.com/shibing624/file-server}
}
```
