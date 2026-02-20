# OpenClaw VPS Setup Guide

## Quick Start

SSH into your VPS and run the setup script:

```bash
# 1. Connect to your VPS
ssh root@217.154.42.151

# 2. Download and run the setup script (from this repo)
curl -fsSL https://raw.githubusercontent.com/ReeperReepx/AI-PR-agency/claude/setup-openclaw-vps-flN4q/setup-openclaw-vps.sh | bash

# OR if you prefer to clone the repo first:
git clone https://github.com/ReeperReepx/AI-PR-agency.git
cd AI-PR-agency
git checkout claude/setup-openclaw-vps-flN4q
bash setup-openclaw-vps.sh
```

## Manual Step-by-Step (if you prefer not to use the script)

### 1. SSH into your VPS

```bash
ssh root@217.154.42.151
# Enter password when prompted
```

### 2. Update system & install dependencies

```bash
apt-get update && apt-get upgrade -y
apt-get install -y curl wget git build-essential
```

### 3. Create a dedicated user (do NOT run OpenClaw as root)

```bash
useradd -m -s /bin/bash openclaw
usermod -aG sudo openclaw
su - openclaw
```

### 4. Install Node.js 22

```bash
# As root:
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
```

### 5. Install OpenClaw

```bash
# As the openclaw user:
su - openclaw
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
npm install -g openclaw@latest
```

### 6. Run the onboarding wizard

```bash
openclaw onboard --install-daemon
```

The wizard will walk you through:
- Choosing your AI provider (get an [Anthropic API key](https://console.anthropic.com/) for best results)
- Connecting messaging channels (WhatsApp, Telegram, Discord, Slack, etc.)
- Configuring workspace and agent skills

### 7. Start the gateway

```bash
# If the systemd service was set up by the script:
sudo systemctl start openclaw
sudo systemctl status openclaw

# Or start manually:
openclaw gateway start
```

### 8. Verify everything works

```bash
openclaw doctor
openclaw logs --follow
```

## Firewall Ports

The setup script configures UFW with these rules:
- **22/tcp** - SSH access
- **18789/tcp** - OpenClaw Gateway RPC
- **3000/tcp** - OpenClaw Dashboard

## Post-Setup Security

1. **Change the root password immediately**: `passwd`
2. **Set up SSH key authentication** and disable password login
3. **Enable explicit consent mode** in OpenClaw config: `exec.ask: "on"`
4. **Vet community plugins** before installing - some contain malware

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Gateway not responding | `openclaw gateway restart` and verify API keys |
| "RPC probe: failed" | Check port 18789: `sudo lsof -i :18789` |
| "0 tokens used" | Daemon stopped or API auth failed, restart gateway |
| General health check | `openclaw doctor` |

## Resources

- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [OpenClaw Docs](https://docs.openclaw.ai/install)
- [DigitalOcean Guide](https://www.digitalocean.com/community/tutorials/how-to-run-openclaw)
