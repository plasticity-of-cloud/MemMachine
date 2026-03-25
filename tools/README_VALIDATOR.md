# Configuration Validator

Validates MemMachine `configuration.yml` files to ensure 100% correctness, with focus on Ollama provider setup.

## Installation

No additional dependencies required beyond PyYAML (already in MemMachine dependencies):

```bash
pip install pyyaml
```

## Usage

### Basic Validation

```bash
# Validate configuration.yml in current directory
python3 tools/validate_config_simple.py

# Validate specific file
python3 tools/validate_config_simple.py path/to/config.yml
```

### Exit Codes

- `0` - Configuration is valid
- `1` - Configuration has errors

### Example Output

**Valid configuration:**
```
✅ Configuration is valid: configuration.yml
```

**Invalid configuration:**
```
❌ Configuration validation failed: configuration.yml

  • Model.ollama_model.model_vendor must be 'openai-compatible' for Ollama
  • embedder.ollama_embedder.config missing 'base_url' field
  • profile_memory.llm_model 'missing_model' not found in Model section
```

## What It Validates

### Structure Validation
- ✅ All required top-level sections present
- ✅ Required fields in each section
- ✅ Correct data types

### Ollama-Specific Validation
- ✅ Model vendor is `openai-compatible`
- ✅ Embedder provider is `openai`
- ✅ Required Ollama fields (model, base_url)

### Reference Validation
- ✅ All ID references point to defined components
- ✅ `default_embedder` exists in `embedder` section
- ✅ `profile_memory.llm_model` exists in `Model` section
- ✅ `long_term_memory.embedder` exists in `embedder` section
- ✅ All storage, reranker, and vector_graph_store references valid

### Provider Validation
- ✅ Storage vendor is `postgres`
- ✅ Vector graph store provider is `neo4j`
- ✅ Reranker provider is valid (identity, embedder, bm25, etc.)
- ✅ Logging level is valid (debug, info, error)

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Validate Configuration
  run: python3 tools/validate_config_simple.py configuration.yml
```

### Pre-commit Hook

```bash
#!/bin/bash
python3 tools/validate_config_simple.py configuration.yml
if [ $? -ne 0 ]; then
    echo "Configuration validation failed. Fix errors before committing."
    exit 1
fi
```

## Schema Documentation

See [docs/configuration_schema.md](../docs/configuration_schema.md) for complete schema reference.

## Limitations

- Does not validate environment variable values (only checks syntax)
- Does not test actual connectivity to services
- Does not validate model names against Ollama's available models
- Does not check if embedding dimensions match the actual model

## Advanced Validation

For runtime validation (checking actual service connectivity), use:

```bash
# Start services and test connectivity
memmachine-server --validate-only
```
