# File Server 文件服务器

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

[English](README.md)

**File Server**：一个支持密码保护的简单自托管文件存储服务。

file-server 是一个轻量级文件存储解决方案，提供以下功能：
- 密码保护的文件上传
- Web 界面和 RESTful API
- 文件列表和删除管理
- 支持多种文件格式

为什么选择 file-server？
- **简单易用**：配置简单，一键部署
- **安全可靠**：上传需要密码验证
- **高性能**：基于 FastAPI 构建，性能优异
- **灵活访问**：支持 Web 界面和 API 调用

## 功能特性

| 功能 | 说明 |
|------|------|
| 文件上传 | 通过 Web 或 API 进行密码保护的上传 |
| 文件存储 | 本地文件系统存储，路径可配置 |
| 文件管理 | 列出、查看和删除文件 |
| API 接口 | RESTful API 支持程序化访问 |
| 安全防护 | 文件类型验证和路径遍历保护 |

## 安装

```bash
git clone https://github.com/shibing624/file-server.git
cd file-server
pip install -r requirements.txt
```

## 快速开始

1. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env 文件，设置 UPLOAD_PASSWORD
```

2. 运行服务：

```bash
python run.py
```

或者直接使用 uvicorn：

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8008
```

3. 在浏览器中访问 `http://localhost:8008`

## API 使用

### 上传文件

```bash
curl -F "password=你的密码" -F "file=@图片.png" http://localhost:8008/upload
```

返回：
```json
{
  "url": "http://localhost:8008/files/0204_a1b2c3d4_图片.png",
  "filename": "0204_a1b2c3d4_图片.png",
  "size": 123456,
  "message": "Upload successful"
}
```

### 列出文件

```bash
curl "http://localhost:8008/list?password=你的密码"
```

### 删除文件

```bash
curl -X DELETE "http://localhost:8008/delete/文件名.png?password=你的密码"
```

## 配置说明

通过环境变量或 `.env` 文件进行配置：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `UPLOAD_PASSWORD` | - | 上传密码（必填） |
| `STORAGE_DIR` | `~/.file-server/data` | 文件存储路径 |
| `BASE_URL` | `http://localhost:8008` | 公网访问地址 |
| `MAX_FILE_SIZE` | `524288000` | 最大文件大小（字节，默认 500MB） |
| `HOST` | `0.0.0.0` | 服务器绑定地址 |
| `PORT` | `8008` | 服务器端口 |

## 部署方式

### 使用 deploy.sh 脚本（推荐）

```bash
# 编辑配置
nano .env

# 运行部署脚本
chmod +x deploy.sh
sudo ./deploy.sh
```

### 使用 Docker

```bash
docker-compose up -d
```

### Nginx 反向代理配置

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

## 开源协议

本项目基于 [Apache License 2.0](LICENSE) 开源协议。

## 社区与支持

- **GitHub Issues**: [提交问题](https://github.com/shibing624/file-server/issues)
- **邮箱**: [shibing624@126.com](mailto:shibing624@126.com)
- **微信**: 添加 `xuming624`，备注 "llm" 加入 LLM 技术交流群

<img src="https://github.com/shibing624/graphrag-lite/raw/main/docs/wechat.jpeg" width="200"/>

## 引用

如果您在研究中使用了本项目，请引用：

```bibtex
@software{file-server,
  author = {Xu Ming},
  title = {File Server: Self-hosted file storage service},
  year = {2026},
  url = {https://github.com/shibing624/file-server}
}
```
