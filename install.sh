#!/bin/bash
# EnviroFix One-Command Installer

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   🚀 EnviroFix - AI-Powered Kali Environment Intelligence ║"
echo "║                                                           ║"
echo "║   Installing...                                           ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root: sudo ./install.sh${NC}"
    exit 1
fi

# Check Kali Linux
if ! grep -q "Kali" /etc/os-release; then
    echo -e "${RED}❌ EnviroFix requires Kali Linux${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Kali Linux detected${NC}"

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | bash
fi

# Start Ollama service
systemctl enable ollama
systemctl start ollama

# Pull DeepSeek model (if not already)
echo "🤖 Pulling DeepSeek-R1 model (first time takes ~5 minutes)..."
ollama pull deepseek-r1:8b

# Clone or update EnviroFix
if [ ! -d "/opt/envirofix" ]; then
    echo "📥 Downloading EnviroFix..."
    git clone https://github.com/mashaal/envirofix.git /opt/envirofix
else
    cd /opt/envirofix && git pull
fi

cd /opt/envirofix

# Start EnviroFix
echo "🐳 Starting EnviroFix containers..."
docker-compose up -d

# Wait for backend to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Start background daemon
echo "🔍 Starting EnviroFix background monitor..."
nohup python3 /opt/envirofix/envirofix-daemon.py > /var/log/envirofix.log 2>&1 &

# Create systemd service for persistence
cat > /etc/systemd/system/envirofix.service << 'SERVICE'
[Unit]
Description=EnviroFix Background Monitor
After=docker.service ollama.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/envirofix/envirofix-daemon.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable envirofix
systemctl start envirofix

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   ✅ EnviroFix Successfully Installed!                    ║"
echo "║                                                           ║"
echo "║   🌐 Dashboard: http://localhost:3000                     ║"
echo "║   📊 API:       http://localhost:7070                     ║"
echo "║                                                           ║"
echo "║   EnviroFix is now running in the background.            ║"
echo "║   You will receive desktop notifications for any issues. ║"
echo "║                                                           ║"
echo "║   📖 Open dashboard to view AI-powered fixes              ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Open dashboard in browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 2>/dev/null &
fi
