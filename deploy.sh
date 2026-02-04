#!/bin/bash
# File Server Deployment Script
# Usage: ./deploy.sh

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/opt/file-server"
DATA_DIR="/var/data/file-server"
SERVICE_NAME="file-server"
PORT=8008

# Check dependencies
check_dependencies() {
    echo "Checking dependencies..."
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 is not installed"
        exit 1
    fi
    if ! command -v pip3 &> /dev/null; then
        echo "Error: pip3 is not installed"
        exit 1
    fi
}

# Load environment
load_env() {
    if [[ -f ".env" ]]; then
        echo "Loading environment from .env"
        set -a
        source ".env"
        set +a
    fi
}

# Set configuration
set_config() {
    APP_DIR="${APP_DIR:-/opt/file-server}"
    DATA_DIR="${STORAGE_DIR:-/var/data/file-server}"
    SERVICE_NAME="${SERVICE_NAME:-file-server}"
    PORT="${PORT:-8008}"
}

# Create directories
create_directories() {
    echo "Creating directories..."
    sudo mkdir -p "$APP_DIR" "$DATA_DIR"
}

# Install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    cd "$SCRIPT_DIR"
    pip3 install -r requirements.txt --user
    sudo cp -r src "$APP_DIR/"
    sudo cp requirements.txt "$APP_DIR/"
    sudo cp .env "$APP_DIR/" 2>/dev/null || true
}

# Create systemd service
create_service() {
    echo "Creating systemd service..."
    sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=File Server
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
Environment=PYTHONPATH=$APP_DIR
EnvironmentFile=-$APP_DIR/.env
ExecStart=uvicorn src.main:app --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
}

# Start service
start_service() {
    echo "Starting service..."
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl restart "$SERVICE_NAME"
    echo "Service started on port $PORT"
}

# Main
main() {
    check_dependencies
    load_env
    set_config
    create_directories
    install_dependencies
    create_service
    start_service
    echo "Deployment completed!"
}

main "$@"
