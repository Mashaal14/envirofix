#!/bin/bash
# EnviroFix Local Installer

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   🚀 EnviroFix - AI-Powered Kali Environment Intelligence ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo ./install_local.sh"
    exit 1
fi

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Start Docker first: systemctl start docker"
    exit 1
fi

# Get current directory
ENVIROFIX_DIR="$(pwd)"

# Start containers
echo "🐳 Starting EnviroFix containers..."
docker compose up -d

# Wait for backend
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Test backend
if curl -s http://localhost:7070/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo "❌ Backend failed to start"
    docker logs envirofix_backend --tail 20
    exit 1
fi

# Create CLI wrapper for current directory
cat > /usr/local/bin/envirofix << 'CLIEOF'
#!/bin/bash
ENVIROFIX_DIR="/home/kali/envirofix"

case "$1" in
    start)
        cd $ENVIROFIX_DIR && docker compose up -d
        echo "✅ EnviroFix started"
        ;;
    stop)
        cd $ENVIROFIX_DIR && docker compose down
        echo "✅ EnviroFix stopped"
        ;;
    status)
        curl -s http://localhost:7070/health > /dev/null && echo "✅ Running" || echo "❌ Not running"
        ;;
    dashboard)
        xdg-open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 in browser"
        ;;
    scan)
        curl -s http://localhost:7070/scan | python3 -m json.tool
        ;;
    alerts)
        curl -s http://localhost:7070/alerts | python3 -m json.tool
        ;;
    daemon)
        python3 $ENVIROFIX_DIR/envirofix-daemon.py
        ;;
    *)
        echo "EnviroFix - AI-Powered Kali Environment Intelligence"
        echo ""
        echo "Commands:"
        echo "  envirofix start      - Start EnviroFix"
        echo "  envirofix stop       - Stop EnviroFix"
        echo "  envirofix status     - Check status"
        echo "  envirofix dashboard  - Open web dashboard"
        echo "  envirofix scan       - Run manual scan"
        echo "  envirofix alerts     - View current alerts"
        echo "  envirofix daemon     - Start background monitor with notifications"
        ;;
esac
CLIEOF

chmod +x /usr/local/bin/envirofix

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   ✅ EnviroFix Successfully Installed!                    ║"
echo "║                                                           ║"
echo "║   🌐 Dashboard: http://localhost:3000                     ║"
echo "║   📊 API:       http://localhost:7070                     ║"
echo "║                                                           ║"
echo "║   Commands:                                               ║"
echo "║   envirofix start     - Start service                     ║"
echo "║   envirofix stop      - Stop service                      ║"
echo "║   envirofix dashboard - Open web UI                       ║"
echo "║   envirofix scan      - Run system scan                   ║"
echo "║   envirofix daemon    - Start background monitor          ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Open dashboard
xdg-open http://localhost:3000 2>/dev/null &
