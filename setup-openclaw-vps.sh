#!/usr/bin/env bash
# ============================================================================
# OpenClaw VPS Setup Script
# ============================================================================
# This script sets up OpenClaw on a fresh Linux VPS (Ubuntu/Debian).
#
# What it does:
#   1. Creates a dedicated 'openclaw' user (security best practice)
#   2. Installs Node.js 22 LTS
#   3. Installs OpenClaw via npm
#   4. Runs the OpenClaw onboarding wizard
#   5. Sets up a systemd service for the OpenClaw gateway daemon
#
# Usage:
#   SSH into your VPS as root, then run:
#     bash setup-openclaw-vps.sh
#
# WARNING: OpenClaw is experimental software. Do not run on machines with
#          sensitive personal data. This script creates a dedicated user
#          to limit the blast radius.
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ---- Pre-flight checks ----
if [[ "$(id -u)" -ne 0 ]]; then
    log_error "This script must be run as root. Use: sudo bash setup-openclaw-vps.sh"
    exit 1
fi

log_info "Starting OpenClaw VPS setup..."

# ---- Step 1: System updates and base dependencies ----
log_info "Step 1/6 - Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git build-essential ca-certificates gnupg ufw
log_ok "System packages updated."

# ---- Step 2: Create dedicated openclaw user ----
OPENCLAW_USER="openclaw"
OPENCLAW_HOME="/home/${OPENCLAW_USER}"

if id "${OPENCLAW_USER}" &>/dev/null; then
    log_warn "User '${OPENCLAW_USER}' already exists. Skipping creation."
else
    log_info "Step 2/6 - Creating dedicated '${OPENCLAW_USER}' user..."
    useradd -m -s /bin/bash "${OPENCLAW_USER}"
    # Add to sudo group for limited admin tasks
    usermod -aG sudo "${OPENCLAW_USER}"
    log_ok "User '${OPENCLAW_USER}' created."
fi

# ---- Step 3: Install Node.js 22 LTS ----
log_info "Step 3/6 - Installing Node.js 22 LTS..."
if command -v node &>/dev/null && [[ "$(node -v | cut -d. -f1 | tr -d 'v')" -ge 22 ]]; then
    log_ok "Node.js $(node -v) already installed and meets requirements."
else
    # Use NodeSource setup for Node.js 22
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y -qq nodejs
    log_ok "Node.js $(node -v) installed."
fi

# Verify npm is available
log_info "npm version: $(npm -v)"

# ---- Step 4: Install pnpm (optional but recommended) ----
log_info "Step 4/6 - Installing pnpm..."
if command -v pnpm &>/dev/null; then
    log_ok "pnpm already installed: $(pnpm -v)"
else
    npm install -g pnpm@latest
    log_ok "pnpm installed: $(pnpm -v)"
fi

# ---- Step 5: Install OpenClaw ----
log_info "Step 5/6 - Installing OpenClaw..."

# Install as the openclaw user
su - "${OPENCLAW_USER}" <<'INSTALL_EOF'
set -euo pipefail

echo "[INFO] Installing OpenClaw globally for user..."

# Ensure npm global dir is in user space
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.npm-global/bin:$PATH"

# Install OpenClaw
npm install -g openclaw@latest

echo "[OK] OpenClaw installed: $(openclaw --version 2>/dev/null || echo 'version check pending')"
INSTALL_EOF

log_ok "OpenClaw package installed."

# ---- Step 6: Configure firewall ----
log_info "Step 6/6 - Configuring firewall..."
ufw allow OpenSSH
# OpenClaw gateway default port
ufw allow 18789/tcp comment "OpenClaw Gateway"
# Allow web dashboard if applicable
ufw allow 3000/tcp comment "OpenClaw Dashboard"
ufw --force enable
log_ok "Firewall configured (SSH + OpenClaw ports 18789, 3000)."

# ---- Create systemd service for OpenClaw gateway ----
log_info "Setting up OpenClaw systemd service..."

cat > /etc/systemd/system/openclaw.service <<EOF
[Unit]
Description=OpenClaw Gateway Daemon
After=network.target

[Service]
Type=simple
User=${OPENCLAW_USER}
Group=${OPENCLAW_USER}
WorkingDirectory=${OPENCLAW_HOME}
Environment=PATH=${OPENCLAW_HOME}/.npm-global/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${OPENCLAW_HOME}/.npm-global/bin/openclaw gateway start --foreground
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable openclaw.service
log_ok "Systemd service created and enabled."

# ---- Summary ----
echo ""
echo "============================================================================"
echo -e "${GREEN}OpenClaw VPS Setup Complete!${NC}"
echo "============================================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Switch to the openclaw user:"
echo "     su - openclaw"
echo ""
echo "  2. Run the onboarding wizard to configure OpenClaw:"
echo "     openclaw onboard --install-daemon"
echo ""
echo "     The wizard will guide you through:"
echo "     - Setting up your AI provider (Anthropic API key recommended)"
echo "     - Connecting messaging channels (WhatsApp, Telegram, Discord, etc.)"
echo "     - Configuring the workspace and skills"
echo ""
echo "  3. After onboarding, start the gateway:"
echo "     systemctl start openclaw"
echo ""
echo "  4. Check status:"
echo "     systemctl status openclaw"
echo "     openclaw doctor"
echo ""
echo "  5. View logs:"
echo "     journalctl -u openclaw -f"
echo "     openclaw logs --follow"
echo ""
echo "  Security reminders:"
echo "  - Change your root password: passwd"
echo "  - Set up SSH key auth and disable password auth"
echo "  - Enable explicit consent mode: exec.ask: \"on\" in config"
echo "  - Vet any community plugins before installing"
echo ""
echo "  VPS IP: $(hostname -I | awk '{print $1}')"
echo "  OpenClaw Dashboard: http://$(hostname -I | awk '{print $1}'):3000"
echo "============================================================================"
