# MemMachine Configuration Schema (Ollama-Focused)

## Overview

This document describes the complete schema for `configuration.yml` with focus on Ollama provider setup.

## Complete Schema

```yaml
# Logging configuration
logging:
  path: string              # Log file path (e.g., /tmp/memory_log)
  level: string             # Log level: debug | info | error

# Default embedder reference
default_embedder: string    # Must reference an embedder ID defined below

# Long-term memory configuration
long_term_memory:
  embedder: string          # Reference to embedder ID
  reranker: string          # Reference to reranker ID
  vector_graph_store: string # Reference to vector_graph_store ID
  database: string          # Reference to storage ID

# Session database configuration
SessionDB:
  uri: string               # SQLite: "sqlite:///path.db" or PostgreSQL: "postgresql://..."

# Language models (Ollama)
Model:
  <model_id>:               # Unique identifier for this model
    model_vendor: "openai-compatible"  # MUST be "openai-compatible" for Ollama
    model: string           # Model name (e.g., "phi4-mini", "llama3")
    api_key: "EMPTY"        # Use "EMPTY" for Ollama
    base_url: string        # Ollama API URL (e.g., "http://localhost:11434/v1")

# Storage backends (PostgreSQL)
storage:
  <storage_id>:             # Unique identifier for this storage
    vendor_name: "postgres" # MUST be "postgres"
    host: string            # PostgreSQL host
    port: integer           # PostgreSQL port (default: 5432)
    user: string            # Database user
    db_name: string         # Database name
    password: string        # Database password

# Profile memory configuration
profile_memory:
  llm_model: string         # Reference to Model ID
  embedding_model: string   # Reference to embedder ID
  database: string          # Reference to storage ID
  prompt: string            # Prompt module name (e.g., "profile_prompt")

# Session memory configuration
sessionMemory:
  model_name: string        # Reference to Model ID
  message_capacity: integer # Maximum number of messages (default: 500)
  max_message_length: integer # Max length per message (default: 16000)
  max_token_num: integer    # Token limit for eviction (default: 8000)

# Embedders (Ollama)
embedder:
  <embedder_id>:            # Unique identifier for this embedder
    provider: "openai"      # MUST be "openai" for Ollama
    config:
      model: string         # Embedding model (e.g., "nomic-embed-text")
      api_key: "EMPTY"      # Use "EMPTY" for Ollama
      base_url: string      # Ollama API URL (e.g., "http://localhost:11434/v1")
      dimensions: integer   # Embedding dimensions (e.g., 768)

# Rerankers
reranker:
  <reranker_id>:            # Unique identifier for this reranker
    provider: string        # identity | embedder | cross-encoder | bm25 | rrf-hybrid
    config:                 # Provider-specific configuration
      # For "embedder" provider:
      embedder_id: string   # Reference to embedder ID
      # For "rrf-hybrid" provider:
      reranker_ids:         # List of reranker IDs to combine
        - string

# Vector graph stores (Neo4j)
vector_graph_store:
  <store_id>:               # Unique identifier for this store
    provider: "neo4j"       # MUST be "neo4j"
    config:
      uri: string           # Neo4j URI (e.g., "bolt://localhost:7687")
      username: string      # Neo4j username
      password: string      # Neo4j password
```

## Ollama-Specific Configuration

### Language Model (Ollama)

```yaml
Model:
  ollama_model:
    model_vendor: "openai-compatible"  # Required for Ollama
    model: "phi4-mini"                 # Any Ollama model
    api_key: "EMPTY"                   # Ollama doesn't need API key
    base_url: "http://localhost:11434/v1"  # Ollama API endpoint
```

**Common Ollama Models:**
- `phi4-mini` - Small, fast model
- `llama3` - Meta's Llama 3
- `mistral` - Mistral AI model
- `qwen2.5` - Alibaba's Qwen model

### Embedder (Ollama)

```yaml
embedder:
  ollama_embedder:
    provider: "openai"                 # Required for Ollama
    config:
      model: "nomic-embed-text"        # Ollama embedding model
      api_key: "EMPTY"                 # Ollama doesn't need API key
      base_url: "http://localhost:11434/v1"  # Ollama API endpoint
      dimensions: 768                  # Model-specific dimensions
```

**Common Ollama Embedding Models:**
- `nomic-embed-text` - 768 dimensions
- `mxbai-embed-large` - 1024 dimensions
- `all-minilm` - 384 dimensions

## Reranker Providers

### Identity Reranker (No Reranking)
```yaml
reranker:
  no_rerank:
    provider: "identity"
```

### Embedder Reranker
```yaml
reranker:
  embed_rerank:
    provider: "embedder"
    config:
      embedder_id: "ollama_embedder"
```

### BM25 Reranker
```yaml
reranker:
  bm25_rerank:
    provider: "bm25"
```

### Hybrid Reranker (RRF)
```yaml
reranker:
  hybrid_rerank:
    provider: "rrf-hybrid"
    config:
      reranker_ids:
        - "embed_rerank"
        - "bm25_rerank"
```

## Environment Variable Substitution

Use `${VAR_NAME}` syntax to reference environment variables:

```yaml
Model:
  ollama_model:
    base_url: "${OLLAMA_BASE_URL}"

storage:
  profile_storage:
    password: "${POSTGRES_PASSWORD}"
```

## Minimal Working Configuration (Ollama)

```yaml
logging:
  path: /tmp/memory_log
  level: info

default_embedder: ollama_embedder

long_term_memory:
  embedder: ollama_embedder
  reranker: my_reranker
  vector_graph_store: neo4j_store
  database: profile_storage

SessionDB:
  uri: sqlite:///sessions.db

Model:
  ollama_model:
    model_vendor: openai-compatible
    model: phi4-mini
    api_key: EMPTY
    base_url: http://localhost:11434/v1

storage:
  profile_storage:
    vendor_name: postgres
    host: localhost
    port: 5432
    user: memmachine
    db_name: memmachine
    password: memmachine_password

profile_memory:
  llm_model: ollama_model
  embedding_model: ollama_embedder
  database: profile_storage
  prompt: profile_prompt

sessionMemory:
  model_name: ollama_model
  message_capacity: 500
  max_message_length: 16000
  max_token_num: 8000

embedder:
  ollama_embedder:
    provider: openai
    config:
      model: nomic-embed-text
      api_key: EMPTY
      base_url: http://localhost:11434/v1
      dimensions: 768

reranker:
  my_reranker:
    provider: embedder
    config:
      embedder_id: ollama_embedder

vector_graph_store:
  neo4j_store:
    provider: neo4j
    config:
      uri: bolt://localhost:7687
      username: neo4j
      password: neo4j_password
```

## Validation

Use the provided validator tool:

```bash
# Validate configuration.yml
python3 tools/validate_config_simple.py

# Validate specific file
python3 tools/validate_config_simple.py path/to/config.yml
```

## Common Validation Errors

### Missing Required Sections
```
❌ Missing required section: Model
```
**Fix:** Add all required top-level sections

### Invalid Model Vendor
```
❌ Model.ollama_model.model_vendor must be 'openai-compatible' for Ollama
```
**Fix:** Set `model_vendor: "openai-compatible"`

### Invalid Embedder Provider
```
❌ embedder.ollama_embedder.provider must be 'openai' for Ollama
```
**Fix:** Set `provider: "openai"`

### Broken Reference
```
❌ profile_memory.llm_model 'ollama_model' not found in Model section
```
**Fix:** Ensure referenced ID exists in the corresponding section

### Missing Required Field
```
❌ embedder.ollama_embedder.config missing 'base_url' field
```
**Fix:** Add the required field to the configuration

## Docker Compose Considerations

When using Docker Compose, containers communicate using **service names** as hostnames, NOT `localhost`.

### Container-to-Container Communication

Containers on the same Docker network use service names:

```yaml
# PostgreSQL storage - use service name "postgres"
storage:
  profile_storage:
    host: postgres  # Service name from docker-compose.yml
    port: 5432

# Neo4j - use service name "neo4j"
vector_graph_store:
  neo4j_store:
    config:
      uri: bolt://neo4j:7687  # Service name from docker-compose.yml
```

### Container-to-Host Communication

To access services running on the **host machine** (like Ollama), use `host.docker.internal`:

```yaml
# Ollama running on host machine
Model:
  ollama_model:
    base_url: "http://host.docker.internal:11434/v1"  # Access host from container

embedder:
  ollama_embedder:
    config:
      base_url: "http://host.docker.internal:11434/v1"  # Access host from container
```

### When to Use localhost

`localhost` only works for services within the **same container**. In Docker Compose:
- ❌ `localhost` does NOT work between containers
- ✅ Use service names for container-to-container
- ✅ Use `host.docker.internal` for container-to-host

### Network Configuration

From `docker-compose.yml`:
```yaml
networks:
  memmachine-network:
    driver: bridge
    name: memmachine-network
```

All services are on the `memmachine-network` bridge network and can communicate using service names.

## Best Practices

1. **Use environment variables** for sensitive data (passwords, API keys)
2. **Reference IDs consistently** - ensure all references point to defined components
3. **Choose appropriate reranker** - hybrid rerankers provide best results but are slower
4. **Set token limits** - adjust `max_token_num` based on your model's context window
5. **Use descriptive IDs** - name components clearly (e.g., `ollama_embedder`, not `emb1`)
