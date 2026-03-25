# MemMachine Configuration Schema (CORRECT)

## Overview

This document describes the **actual** configuration schema used by MemMachine, extracted from the Pydantic models in `packages/server/src/memmachine_server/common/configuration/`.

## Top-Level Required Sections

```yaml
logging:              # LogConf - required
episodic_memory:      # EpisodicMemoryConfPartial - required  
semantic_memory:      # SemanticMemoryConf - required
session_manager:      # SessionManagerConf - required
resources:            # ResourcesConf - required
episode_store:        # EpisodeStoreConf - required
```

## Complete Schema

### logging (LogConf)

```yaml
logging:
  level: info          # LogLevel: debug | info | error
  format: "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
  path: /tmp/memory_log  # Log file path
```

### episodic_memory (EpisodicMemoryConfPartial)

```yaml
episodic_memory:
  enabled: true        # bool (default: true)
  long_term_memory:    # LongTermMemoryConfPartial
    embedder: <embedder_id>
    reranker: <reranker_id>
    vector_graph_store: <database_id>
  short_term_memory:   # ShortTermMemoryConfPartial
    llm_model: <language_model_id>
    message_capacity: 500
    max_message_length: 16000
    max_token_num: 8000
```

### semantic_memory (SemanticMemoryConf)

```yaml
semantic_memory:
  enabled: true                    # bool (default: true)
  database: <database_id>          # str | None
  config_database: <database_id>   # str - REQUIRED
  llm_model: <language_model_id>   # str | None
  embedding_model: <embedder_id>   # str | None
  ingestion_trigger_messages: 5    # int
  ingestion_trigger_age: 300       # seconds (default: 5 minutes)
  max_features_per_update: 50      # int
```

### session_manager (SessionManagerConf)

```yaml
session_manager:
  database: <database_id>  # str (default: "")
```

### episode_store (EpisodeStoreConf)

```yaml
episode_store:
  database: <database_id>      # str (default: "")
  with_count_cache: true       # bool (default: true)
```

### resources (ResourcesConf)

The `resources` section contains all reusable components referenced by other sections.

```yaml
resources:
  language_models:    # LanguageModelsConf
    <model_id>:
      provider: <provider_name>
      config: <provider_specific_config>
  
  embedders:          # EmbeddersConf
    <embedder_id>:
      provider: <provider_name>
      config: <provider_specific_config>
  
  rerankers:          # RerankersConf
    <reranker_id>:
      provider: <provider_name>
      config: <provider_specific_config>
  
  databases:          # DatabasesConf
    <database_id>:
      provider: <provider_name>
      config: <provider_specific_config>
```

## Resource Providers

### Language Models

**Supported providers:**
- `openai-responses` - OpenAI Responses API
- `openai-chat-completions` - OpenAI Chat Completions API (use this for Ollama)
- `amazon-bedrock` - Amazon Bedrock

**Example (Ollama):**
```yaml
resources:
  language_models:
    ollama_model:
      provider: openai-chat-completions
      config:
        model: phi4-mini
        api_key: EMPTY
        base_url: http://host.docker.internal:11434/v1
```

### Embedders

**Supported providers:**
- `openai` - OpenAI Embeddings API (use this for Ollama)
- `amazon-bedrock` - Amazon Bedrock
- `sentence-transformer` - Local Sentence Transformers

**Example (Ollama):**
```yaml
resources:
  embedders:
    ollama_embedder:
      provider: openai
      config:
        model: nomic-embed-text
        api_key: EMPTY
        base_url: http://host.docker.internal:11434/v1
        dimensions: 768
```

### Rerankers

**Supported providers:**
- `rrf-hybrid` - Reciprocal Rank Fusion (combines multiple rerankers)
- `embedder` - Uses an embedder for reranking
- `bm25` - BM25 keyword-based reranking
- `identity` - No reranking (pass-through)
- `cohere` - Cohere Rerank API
- `amazon-bedrock` - Amazon Bedrock Rerank
- `cross-encoder` - Cross-encoder model

**Example (Hybrid):**
```yaml
resources:
  rerankers:
    hybrid_reranker:
      provider: rrf-hybrid
      config:
        reranker_ids:
          - embedder_reranker
          - bm25_reranker
    embedder_reranker:
      provider: embedder
      config:
        embedder_id: ollama_embedder
    bm25_reranker:
      provider: bm25
```

### Databases

**Supported providers:**
- `postgres` / `postgresql` - PostgreSQL
- `sqlite` - SQLite
- `neo4j` - Neo4j graph database
- `nebula_graph` - Nebula Graph

**Example (PostgreSQL):**
```yaml
resources:
  databases:
    profile_storage:
      provider: postgres
      config:
        host: postgres
        port: 5432
        user: memmachine
        db_name: memmachine
        password: ${POSTGRES_PASSWORD}
```

**Example (Neo4j):**
```yaml
resources:
  databases:
    neo4j_store:
      provider: neo4j
      config:
        uri: bolt://neo4j:7687
        username: neo4j
        password: ${NEO4J_PASSWORD}
```

## Docker Compose Networking

When running in Docker Compose:

- **PostgreSQL**: Use service name `postgres` as host
- **Neo4j**: Use service name `neo4j` in URI (`bolt://neo4j:7687`)
- **Ollama on host**: Use `http://host.docker.internal:11434/v1`

## Environment Variables

Use `${VAR_NAME}` syntax for environment variable substitution:

```yaml
password: ${POSTGRES_PASSWORD}
```

## Complete Working Example (Ollama + Docker Compose)

See `configuration.yml` in the repository root for a complete working example.

## Validation

Validate your configuration:

```bash
python3 tools/validate_config_complete.py configuration.yml
```

## Common Errors

### Missing required sections
```
Error: Missing required section: semantic_memory
```
**Fix**: Add all required top-level sections.

### Invalid reference
```
Error: semantic_memory.llm_model: references unknown language_model 'my_model'
```
**Fix**: Ensure the referenced ID exists in `resources.language_models`.

### Missing config_database
```
Error: semantic_memory.config_database: field required
```
**Fix**: Add `config_database` field to `semantic_memory` section.

### Wrong provider
```
Error: Unknown embedder provider 'ollama'
```
**Fix**: Use `openai` provider for Ollama embeddings, not `ollama`.
