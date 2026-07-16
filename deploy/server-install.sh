#!/usr/bin/env bash
# EnviroFix — one-time server bootstrap (Ubuntu 24.04, e.g. AWS EC2).
#
# Run this ONCE after SSH-ing into a fresh instance, as a normal sudo-capable
# user. It installs Docker so the app can run via docker-compose.prod.yml,
# deployed on every push to master by .github/workflows/deploy.yml (via the
# self-hosted GitHub Actions runner, set up separately). This script does not
# touch nginx/TLS or DNS.
#
# Usage:
#   chmod +x deploy/server-install.sh
#   ./deploy/server-install.sh
#
# Optional: pass --with-ollama to also install Ollama + pull deepseek-r1:8b
# for full AI mode. Without this flag, the app is left in mock-AI mode
# (USE_OLLAMA=false), which is what you set up for this Ubuntu 24.04 box.

set -euo pipefail

WITH_OLLAMA=false
for arg in "$@"; do
  case "$arg" in
    --with-ollama) WITH_OLLAMA=true ;;
  esac
done

if [ "$EUID" -eq 0 ]; then
  echo "Do not run this as root / with sudo. Run it as your normal user;" >&2
  echo "it will call sudo itself for the specific steps that need it." >&2
  exit 1
fi

echo "==> Updating package index"
sudo apt-get update -y

echo "==> Installing Docker Engine + Compose v2 plugin"
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com | sudo bash
else
  echo "Docker already installed, skipping."
fi

echo "==> Adding $USER to the docker group"
if ! id -nG "$USER" | grep -qw docker; then
  sudo usermod -aG docker "$USER"
  NEEDS_RELOGIN=true
else
  NEEDS_RELOGIN=false
fi

if [ "$WITH_OLLAMA" = true ]; then
  echo "==> Installing Ollama (full AI mode requested via --with-ollama)"
  if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sudo bash
  fi
  sudo systemctl enable --now ollama
  echo "==> Pulling deepseek-r1:8b (this can take several minutes)"
  ollama pull deepseek-r1:8b
  echo "Remember to set USE_OLLAMA=true in the deployed .env for this to be used."
else
  echo "==> Skipping Ollama install (mock AI mode — pass --with-ollama to enable full AI mode)"
fi

echo ""
echo "============================================================"
echo " Host setup complete."
echo "============================================================"
if [ "${NEEDS_RELOGIN:-false}" = true ]; then
  echo "! You were just added to the docker group — log out and back in"
  echo "  (or run 'newgrp docker') before running any docker commands"
  echo "  by hand. The runner service itself does not need this, since"
  echo "  systemd re-reads group membership when the service starts."
fi
echo ""
echo "Next steps:"
echo "1. Make sure .env exists in the runner's checkout directory"
echo "   (usually ~/actions-runner/_work/envirofix/envirofix/.env),"
echo "   matching the keys in this repo's .env.example."
echo "   Set USE_OLLAMA=$([ "$WITH_OLLAMA" = true ] && echo true || echo false)."
echo "2. Push to master (or re-run the deploy workflow manually) to deploy."
echo "3. Confirm your AWS security group allows only 80 and 443 inbound"
echo "   (3000 and 7070 are bound to 127.0.0.1 and don't need to be open)."
echo "============================================================"
