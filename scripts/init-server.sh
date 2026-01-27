#!/bin/bash
# =====================================================
# Hub Chantier - Initialisation serveur Scaleway
# =====================================================
# Executer en root sur une instance Ubuntu 22.04+
# Usage: ssh root@IP 'bash -s' < scripts/init-server.sh

set -euo pipefail

echo "======================================"
echo "Hub Chantier - Init Serveur"
echo "======================================"

# 1. Mise a jour systeme
echo "[1/6] Mise a jour systeme..."
apt-get update && apt-get upgrade -y

# 2. Installer Docker
echo "[2/6] Installation Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installe."
else
    echo "Docker deja installe."
fi

# 3. Installer Docker Compose (plugin)
echo "[3/6] Verification Docker Compose..."
if docker compose version &> /dev/null; then
    echo "Docker Compose disponible."
else
    apt-get install -y docker-compose-plugin
    echo "Docker Compose installe."
fi

# 4. Configurer le firewall
echo "[4/6] Configuration firewall (UFW)..."
apt-get install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirection vers HTTPS)
ufw allow 443/tcp   # HTTPS
ufw --force enable
echo "Firewall configure : SSH (22), HTTP (80), HTTPS (443)."

# 5. Configurer swap (utile sur petites instances)
echo "[5/6] Configuration swap (2 Go)..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "Swap 2 Go active."
else
    echo "Swap deja configure."
fi

# 6. Creer utilisateur deploiement
echo "[6/6] Creation utilisateur deploy..."
if ! id "deploy" &>/dev/null; then
    adduser --disabled-password --gecos "" deploy
    usermod -aG docker deploy
    # Copier les cles SSH root vers deploy
    mkdir -p /home/deploy/.ssh
    cp /root/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
    chown -R deploy:deploy /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    echo "Utilisateur 'deploy' cree (groupe docker)."
else
    echo "Utilisateur 'deploy' existe deja."
fi

echo ""
echo "======================================"
echo "Serveur pret !"
echo "======================================"
echo ""
echo "Prochaines etapes :"
echo "  1. Se connecter : ssh deploy@$(hostname -I | awk '{print $1}')"
echo "  2. Cloner le projet : git clone <repo> ~/hub-chantier"
echo "  3. Configurer : cp .env.production.example .env.production && nano .env.production"
echo "  4. Deployer : bash scripts/deploy.sh"
echo ""
