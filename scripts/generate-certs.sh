#!/bin/bash
# Generate self-signed TLS certificates for development/testing
# For production, use Let's Encrypt or your organization's CA

set -e

CERT_DIR="traefik/certs"
DOMAIN=${1:-"deepfix.local"}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Generating self-signed certificate for: ${DOMAIN}${NC}"

# Create directory
mkdir -p "$CERT_DIR"

# Generate certificate
openssl req -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -subj "/CN=${DOMAIN}/O=DeepFix/C=US" \
    -addext "subjectAltName=DNS:${DOMAIN},DNS:localhost,IP:127.0.0.1"

# Set permissions
chmod 600 "$CERT_DIR/server.key"
chmod 644 "$CERT_DIR/server.crt"

echo -e "${GREEN}Certificate generated successfully!${NC}"
echo ""
echo "Files created:"
echo "  - $CERT_DIR/server.crt (certificate)"
echo "  - $CERT_DIR/server.key (private key)"
echo ""
echo -e "${YELLOW}WARNING: Self-signed certificates are for testing only.${NC}"
echo "For production, use Let's Encrypt or a trusted CA."
