#!/bin/bash
# SSL Certificate Setup with Let's Encrypt

set -e

if [ -z "$1" ]; then
    echo "Usage: ./ssl_setup.sh <domain>"
    echo "Example: ./ssl_setup.sh taxsnap.example.com"
    exit 1
fi

DOMAIN=$1

echo "======================================"
echo "Setting up SSL for: $DOMAIN"
echo "======================================"

# Stop nginx if running
docker-compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true

# Obtain certificate
echo "Obtaining SSL certificate..."
sudo certbot certonly --standalone \
    -d $DOMAIN \
    --non-interactive \
    --agree-tos \
    --email admin@$DOMAIN \
    --preferred-challenges http

echo "SSL certificate obtained successfully!"
echo ""
echo "Certificate location: /etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "Next steps:"
echo "1. Update deploy/nginx.conf with your domain"
echo "2. Update .env file with DOMAIN=$DOMAIN"
echo "3. Run: docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "To renew certificates (automatic):"
echo "Add this to crontab: 0 0 1 * * certbot renew --quiet && docker-compose -f docker-compose.prod.yml restart nginx"
