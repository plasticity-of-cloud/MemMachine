# Ollama Docker Connectivity Guide

## Problem

Ollama defaults to `127.0.0.1:11434` (localhost only) for security. Docker containers cannot access localhost services on the host, even with `host.docker.internal:host-gateway`.

## Why Ollama Uses Localhost Only

**Security by design:** Ollama binds to localhost to prevent exposing an unauthenticated LLM API to your network. This is the correct default.

## Solutions

### Option 1: Bind Ollama to 0.0.0.0 (Simplest)

**Trade-off:** Ollama becomes accessible from your network. Acceptable for development/private networks.

#### Step 1: Configure Ollama

```bash
sudo systemctl edit ollama
```

Add:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

#### Step 2: Restart

```bash
sudo systemctl restart ollama
```

#### Step 3: Verify

```bash
ss -tlnp | grep 11434
# Should show: 0.0.0.0:11434
```

#### Step 4: Test from container

```bash
docker run --rm --add-host=host.docker.internal:host-gateway curlimages/curl:latest \
  curl -s http://host.docker.internal:11434/api/tags
```

**Security considerations:**
- Ollama is now accessible from your entire network
- No authentication by default
- Consider firewall rules: `sudo ufw allow from 172.17.0.0/16 to any port 11434`

### Option 2: Run Ollama in Docker (Most Secure)

Use the official Ollama Docker image and add it to docker-compose.yml:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: memmachine-ollama
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - memmachine-network
    # Optional: expose for host access
    # ports:
    #   - "11434:11434"

volumes:
  ollama_data:
```

Update configuration to use service name:
```yaml
base_url: http://ollama:11434/v1
```

### Option 3: Network Mode Host (Linux Only)

Run MemMachine container with `network_mode: host` - container shares host network namespace and can access localhost services.

**Not recommended:** Breaks container isolation.

## Recommended Approach

**For development:** Option 1 (bind to 0.0.0.0)
**For production:** Option 2 (Ollama in Docker)

## Verify Container Can Access Ollama

```bash
# Test from a container
docker run --rm curlimages/curl:latest curl -s http://172.17.0.1:11434/api/tags
```

Should return JSON with available models.

## Start MemMachine

```bash
docker compose up -d
docker logs -f memmachine-app
```

If configured correctly, you should see:
```
INFO: Application startup complete.
```

Instead of:
```
InvalidEmbedderError: embedder 'ollama_embedder' is invalid
```
