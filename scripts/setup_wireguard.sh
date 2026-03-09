#!/bin/bash
# Run this on every Oracle/Fly/GCP VPS to set up WireGuard

set -e

echo "=== WireGuard VPN Server Setup ==="

# Install WireGuard
echo "Installing WireGuard..."
sudo apt update && sudo apt install -y wireguard

# Generate keys
echo "Generating WireGuard keys..."
wg genkey | sudo tee /etc/wireguard/privatekey | wg pubkey | sudo tee /etc/wireguard/publickey
PRIVATE_KEY=$(sudo cat /etc/wireguard/privatekey)
PUBLIC_KEY=$(sudo cat /etc/wireguard/publickey)

# Create WireGuard config
echo "Creating WireGuard configuration..."
sudo bash -c "cat > /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $PRIVATE_KEY
Address = 10.8.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOF"

# Enable IP forwarding
echo "Enabling IP forwarding..."
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Start WireGuard
echo "Starting WireGuard..."
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 51820/udp
sudo ufw allow 22/tcp
sudo ufw --force enable

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo "=== SERVER READY ==="
echo "Public Key: $PUBLIC_KEY"
echo "Endpoint: $PUBLIC_IP:51820"
echo ""
echo "Add this to your database:"
echo "INSERT INTO vpn_servers (country, country_code, city, endpoint, public_key)"
echo "VALUES ('Country', 'CC', 'City', '$PUBLIC_IP:51820', '$PUBLIC_KEY');"
