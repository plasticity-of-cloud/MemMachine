#!/bin/bash
# Setup Ollama Docker Bridge Forwarding
# This keeps Ollama on localhost while allowing Docker containers to access it

set -e

echo "=== Setting up Ollama Docker Bridge Forwarding ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Install socat
echo "1. Installing socat..."
apt-get update -qq
apt-get install -y socat
echo "   ✅ socat installed"

# Create systemd service
echo
echo "2. Creating ollama-docker-bridge.service..."
tee /etc/systemd/system/ollama-docker-bridge.service > /dev/null <<'EOF'
[Unit]
Description=Forward Ollama to Docker Bridge
After=network.target ollama.service docker.service
Requires=ollama.service

[Service]
Type=simple
ExecStart=/usr/bin/socat TCP-LISTEN:11434,bind=172.17.0.1,fork TCP:127.0.0.1:11434
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
echo "   ✅ Service file created"

# Enable and start service
echo
echo "3. Enabling and starting service..."
systemctl daemon-reload
systemctl enable ollama-docker-bridge
systemctl start ollama-docker-bridge
echo "   ✅ Service started"

# Verify
echo
echo "4. Verifying setup..."
sleep 2
if systemctl is-active --quiet ollama-docker-bridge; then
    echo "   ✅ ollama-docker-bridge is running"
else
    echo "   ❌ ollama-docker-bridge failed to start"
    systemctl status ollama-docker-bridge --no-pager
    exit 1
fi

# Test connectivity
echo
echo "5. Testing connectivity from Docker..."
if docker run --rm curlimages/curl:latest curl -sf http://172.17.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama accessible from Docker containers"
else
    echo "   ❌ Cannot access Ollama from Docker"
    exit 1
fi

echo
echo "=== Setup Complete! ==="
echo
echo "Ollama is now accessible from Docker containers at:"
echo "  http://172.17.0.1:11434"
echo
echo "Security status:"
echo "  ✅ Ollama still on localhost (127.0.0.1)"
echo "  ✅ Only Docker containers can access it"
echo "  ✅ Not exposed to network"
echo
echo "To check status: sudo systemctl status ollama-docker-bridge"
echo "To stop: sudo systemctl stop ollama-docker-bridge"
echo "To disable: sudo systemctl disable ollama-docker-bridge"
