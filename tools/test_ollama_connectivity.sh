#!/bin/bash
# Test Ollama connectivity from container perspective

set -e

echo "=== Testing Ollama Connectivity from Container ==="
echo

# Check if Ollama is running on host
echo "1. Checking Ollama service on host..."
if systemctl is-active --quiet ollama; then
    echo "   ✅ Ollama service is running"
else
    echo "   ❌ Ollama service is not running"
    echo "   Run: sudo systemctl start ollama"
    exit 1
fi

# Check Ollama listening address
echo
echo "2. Checking Ollama listening address..."
LISTEN_ADDR=$(ss -tlnp 2>/dev/null | grep 11434 | awk '{print $4}')
echo "   Listening on: $LISTEN_ADDR"

if echo "$LISTEN_ADDR" | grep -q "127.0.0.1"; then
    echo "   ⚠️  Ollama is only listening on localhost (127.0.0.1)"
    echo "   Containers cannot access it!"
    echo
    echo "   To fix, set OLLAMA_HOST environment variable:"
    echo "   sudo systemctl edit ollama"
    echo "   Add these lines:"
    echo "   [Service]"
    echo "   Environment=\"OLLAMA_HOST=0.0.0.0:11434\""
    echo
    echo "   Then restart: sudo systemctl restart ollama"
    exit 1
elif echo "$LISTEN_ADDR" | grep -q "0.0.0.0"; then
    echo "   ✅ Ollama is listening on all interfaces"
else
    echo "   ⚠️  Unknown listening address"
fi

# Test from host
echo
echo "3. Testing Ollama API from host..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "   ✅ Ollama API accessible from host"
else
    echo "   ❌ Ollama API not accessible from host"
    exit 1
fi

# Get Docker bridge IP
DOCKER_IP=$(ip -4 addr show docker0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "172.17.0.1")
echo
echo "4. Testing Ollama API from container (via Docker bridge IP: $DOCKER_IP)..."
if docker run --rm curlimages/curl:latest curl -sf http://$DOCKER_IP:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama API accessible from container"
else
    echo "   ❌ Ollama API not accessible from container"
    echo "   This is expected if Ollama is listening on 127.0.0.1 only"
    exit 1
fi

# Test host.docker.internal (Linux may not support this)
echo
echo "5. Testing host.docker.internal (may not work on Linux)..."
if docker run --rm curlimages/curl:latest curl -sf http://host.docker.internal:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ host.docker.internal works"
else
    echo "   ⚠️  host.docker.internal not supported (normal on Linux)"
    echo "   Use Docker bridge IP ($DOCKER_IP) instead"
fi

echo
echo "=== Summary ==="
echo "✅ All connectivity tests passed!"
echo
echo "Configuration should use:"
echo "  base_url: http://$DOCKER_IP:11434/v1"
