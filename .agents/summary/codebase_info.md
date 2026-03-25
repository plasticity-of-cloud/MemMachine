# Codebase Information

## Project Overview

**Name:** MemMachine  
**Version:** 0.1.0  
**License:** Apache-2.0  
**Description:** Open-source memory layer for AI agents, providing short-term, long-term, and personalization memory capabilities

## Technology Stack

### Primary Language
- **Python 3.12+** (100% of codebase)

### Core Dependencies
- **FastAPI** (0.116.1+) - REST API framework
- **FastMCP** (2.12.0+) - Model Context Protocol support
- **Neo4j** (5.28.2+) - Graph database for episodic memory
- **AsyncPG** (0.30.0+) - PostgreSQL async driver for profile storage
- **SQLAlchemy** (2.0.43+) - ORM for session management
- **OpenAI** (1.104.2+) - LLM integration
- **Boto3** (1.40.40+) - AWS Bedrock support
- **Sentence Transformers** (5.1.0+, GPU optional) - Local embeddings
- **Prometheus Client** (0.22.1+) - Metrics collection
- **Pydantic** (2.11.7+) - Data validation

### Development Tools
- **pytest** (8.4.2+) - Testing framework
- **pytest-asyncio** (1.2.0+) - Async test support
- **mypy** (1.18.2+) - Type checking
- **ruff** (0.13.2+) - Linting and formatting
- **testcontainers** (4.13.1+) - Integration testing

## Project Structure

```
MemMachine/
├── src/memmachine/           # Core library code
│   ├── episodic_memory/      # Short-term and long-term episodic memory
│   ├── profile_memory/       # User profile and personalization memory
│   ├── common/               # Shared utilities (embedders, LLMs, rerankers)
│   ├── server/               # REST API and MCP server implementations
│   └── rest_client/          # Python client SDK
├── examples/                 # Example applications and use cases
│   ├── crm/                  # CRM agent with Slack integration
│   ├── writing_assistant/    # Writing style learning assistant
│   ├── health_assistant/     # Healthcare navigation agent
│   ├── financial_analyst/    # Financial advisory agent
│   └── frontend/             # Web UI example
├── tests/                    # Unit and integration tests
├── evaluation/               # Benchmark and evaluation scripts
├── tools/                    # Migration and utility tools
├── docs/                     # Documentation (Mintlify format)
└── sample_configs/           # Configuration templates
```

## Codebase Statistics

- **Total Files:** 324
- **Prioritized Files:** 170
- **Total Functions:** 942
- **Total Classes:** 149
- **Lines of Code:** ~29,000

## Entry Points

### Command-Line Scripts
- `memmachine-server` - Start REST API server
- `memmachine-mcp-stdio` - Start MCP server (stdio transport)
- `memmachine-mcp-http` - Start MCP server (HTTP transport)
- `memmachine-sync-profile-schema` - Sync PostgreSQL schema
- `memmachine-nltk-setup` - Download NLTK data

### Docker Deployment
- `memmachine-compose.sh` - Interactive Docker Compose setup
- `build-docker.sh` - Multi-platform Docker image builder
- `docker-compose.yml` - Service orchestration

## Configuration

### Primary Config File
- `configuration.yml` - Main configuration for memory components, models, and storage

### Environment Variables
- `.env` - API keys, database credentials, service URLs

### Sample Configurations
- `episodic_memory_config.cpu.sample` - CPU-based embeddings
- `episodic_memory_config.gpu.sample` - GPU-accelerated embeddings
- `server_config.sample` - Server settings template

## Supported Platforms

### LLM Providers
- OpenAI (GPT-4, GPT-3.5)
- OpenAI-compatible APIs (Ollama, vLLM, etc.)
- Amazon Bedrock (Claude, Titan, etc.)

### Embedding Providers
- OpenAI embeddings
- Sentence Transformers (local)
- Amazon Bedrock embeddings

### Storage Backends
- Neo4j (episodic memory graph)
- PostgreSQL (profile memory)
- SQLite (session management)

## API Interfaces

### REST API
- `/v1/memories` - Add and search memories
- `/v1/memories/episodic` - Episodic memory operations
- `/v1/memories/profile` - Profile memory operations
- `/v1/sessions` - Session management
- `/health` - Health check endpoint
- `/metrics` - Prometheus metrics

### MCP Protocol
- `add_memory` - Store new memories
- `search_memory` - Query memory stores

### Python SDK
- `MemMachineClient` - High-level client interface
- `Memory` - Memory operations for specific contexts
