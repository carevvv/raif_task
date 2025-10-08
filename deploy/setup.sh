#!/bin/bash
# TaxSnap VPS Setup Script for Ubuntu 22.04+

set -e

echo "======================================"
echo "Checko VPS Setup Script"
echo "======================================"

# Update system
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed successfully"
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose already installed"
fi

# Install Git
echo "Installing Git..."
sudo apt-get install -y git

# Install Certbot
echo "Installing Certbot..."
sudo apt-get install -y certbot

echo "======================================"
echo "Setup completed!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone <your-repo-url>"
echo "2. Copy .env.example to .env and configure it"
echo "3. Run: ./deploy/ssl_setup.sh <your-domain>"
echo "4. Run: docker-compose -f docker-compose.prod.yml up -d"
echo ""
