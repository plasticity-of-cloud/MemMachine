# Interfaces and APIs

## REST API

### Base URL
- Default: `http://localhost:8000`
- Configurable via environment variables

### Authentication
- Optional API key via `Authorization: Bearer <token>` header
- Configured in server settings

### Common Headers
- `Content-Type: application/json`
- `X-User-ID: <user_id>` - Optional user context
- `X-Session-ID: <session_id>` - Optional session context

### Memory Endpoints

#### Add Memory
```http
POST /v1/memories
Content-Type: application/json

{
  "content": "string or list of strings",
  "metadata": {
    "key": "value"
  },
  "session": {
    "user_id": "string or list",
    "agent_id": "string or list",
    "session_id": "string",
    "group_id": "string"
  },
  "producer": {
    "role": "user|agent|system",
    "id": "string"
  },
  "produced_for": {
    "role": "user|agent",
    "id": "string"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Memory added successfully"
}
```

#### Search Memory
```http
POST /v1/memories/search
Content-Type: application/json

{
  "query": "search query string",
  "limit": 10,
  "session": {
    "user_id": "string",
    "agent_id": "string",
    "session_id": "string"
  },
  "filters": {
    "metadata_key": "value"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "string",
      "metadata": {},
      "score": 0.95,
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Add Episodic Memory
```http
POST /v1/memories/episodic
Content-Type: application/json

{
  "content": "string",
  "session": {
    "user_id": "string",
    "agent_id": "string",
    "session_id": "string"
  },
  "producer": {
    "role": "user",
    "id": "user1"
  }
}
```

#### Search Episodic Memory
```http
POST /v1/memories/episodic/search
Content-Type: application/json

{
  "query": "search query",
  "limit": 10,
  "session": {
    "user_id": "string",
    "agent_id": "string"
  }
}
```

#### Add Profile Memory
```http
POST /v1/memories/profile
Content-Type: application/json

{
  "content": "User prefers dark mode",
  "session": {
    "user_id": "user1",
    "agent_id": "agent1"
  }
}
```

#### Search Profile Memory
```http
POST /v1/memories/profile/search
Content-Type: application/json

{
  "query": "user preferences",
  "limit": 5,
  "session": {
    "user_id": "user1"
  }
}
```

#### Delete Memories
```http
DELETE /v1/memories
Content-Type: application/json

{
  "session": {
    "user_id": "string",
    "agent_id": "string",
    "session_id": "string"
  },
  "filters": {
    "metadata_key": "value"
  }
}
```

### Session Endpoints

#### Get User Sessions
```http
GET /v1/sessions/user/{user_id}
```

**Response:**
```json
{
  "sessions": [
    {
      "user_id": "user1",
      "agent_id": "agent1",
      "session_id": "session1",
      "group_id": "group1",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Agent Sessions
```http
GET /v1/sessions/agent/{agent_id}
```

#### Get Group Sessions
```http
GET /v1/sessions/group/{group_id}
```

#### Get All Sessions
```http
GET /v1/sessions
```

### Health and Metrics

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

#### Prometheus Metrics
```http
GET /metrics
```

**Response:** Prometheus text format

## MCP Protocol

### Tools

#### add_memory
**Description:** Store new memories in the memory system

**Parameters:**
```json
{
  "content": "string or list of strings",
  "user_id": "string (from env or parameter)",
  "agent_id": "string (optional)",
  "session_id": "string (optional)",
  "group_id": "string (optional)",
  "metadata": {
    "key": "value"
  },
  "producer_role": "user|agent|system",
  "producer_id": "string"
}
```

**Returns:**
```json
{
  "status": "success",
  "message": "Memory added successfully"
}
```

#### search_memory
**Description:** Search for relevant memories

**Parameters:**
```json
{
  "query": "search query string",
  "user_id": "string (from env or parameter)",
  "agent_id": "string (optional)",
  "session_id": "string (optional)",
  "limit": 10,
  "memory_type": "episodic|profile|all"
}
```

**Returns:**
```json
{
  "results": [
    {
      "content": "string",
      "score": 0.95,
      "metadata": {}
    }
  ]
}
```

### Environment Variables
- `MEMMACHINE_USER_ID` - Default user ID for MCP operations

### Transport Options

#### stdio Transport
```bash
memmachine-mcp-stdio
```

#### HTTP Transport
```bash
memmachine-mcp-http --port 8001
```

## Python SDK

### Installation
```bash
pip install memmachine
```

### Client Initialization

```python
from memmachine.rest_client import MemMachineClient

# Basic initialization
client = MemMachineClient(
    base_url="http://localhost:8000"
)

# With API key
client = MemMachineClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# With custom headers
client = MemMachineClient(
    base_url="http://localhost:8000",
    headers={"X-Custom-Header": "value"}
)
```

### Memory Operations

```python
# Create memory context
memory = client.memory(
    user_id="user1",
    agent_id="agent1",
    session_id="session1",
    group_id="group1"
)

# Add memory
memory.add(
    content="User prefers dark mode",
    producer="user",
    metadata={"category": "preference"}
)

# Add multiple memories
memory.add(
    content=["Message 1", "Message 2"],
    producer="user"
)

# Search memory
results = memory.search(
    query="user preferences",
    limit=10
)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")

# Get memory context for LLM
context = memory.get_context()
print(context)
```

### Context Manager

```python
with MemMachineClient(base_url="http://localhost:8000") as client:
    memory = client.memory(user_id="user1")
    memory.add(content="Hello world", producer="user")
```

### Error Handling

```python
from memmachine.rest_client import MemMachineClient
import requests

try:
    client = MemMachineClient(base_url="http://localhost:8000")
    memory = client.memory(user_id="user1")
    memory.add(content="Test", producer="user")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
```

## Configuration API

### Configuration File Format

```yaml
# Logging configuration
logging:
  path: /tmp/memory_log
  level: info

# Default embedder
default_embedder: my_embedder_id

# Long-term memory configuration
long_term_memory:
  embedder: my_embedder_id
  reranker: my_reranker_id
  vector_graph_store: my_storage_id
  database: profile_storage

# Session database
SessionDB:
  uri: sqlite:///sessions.db

# Language models
Model:
  my_model_id:
    model_vendor: openai
    model: gpt-4
    api_key: ${OPENAI_API_KEY}

# Storage backends
storage:
  my_storage_id:
    vendor_name: neo4j
    uri: bolt://localhost:7687
    user: neo4j
    password: ${NEO4J_PASSWORD}
  
  profile_storage:
    vendor_name: postgres
    host: localhost
    port: 5432
    user: memmachine
    db_name: memmachine
    password: ${POSTGRES_PASSWORD}

# Profile memory configuration
profile_memory:
  llm_model: my_model_id
  embedding_model: my_embedder_id
  database: profile_storage
  prompt: profile_prompt

# Session memory configuration
sessionMemory:
  model_name: my_model_id
  message_capacity: 500
  max_message_length: 16000
  max_token_num: 8000

# Embedder configuration
embedder:
  my_embedder_id:
    provider: openai
    model: text-embedding-3-small
    api_key: ${OPENAI_API_KEY}

# Reranker configuration
reranker:
  my_reranker_id:
    provider: cross-encoder
    model: cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Environment Variable Substitution

Configuration values can reference environment variables using `${VAR_NAME}` syntax:

```yaml
Model:
  my_model:
    api_key: ${OPENAI_API_KEY}
```

### Component Configuration

#### Embedder Providers
- `openai` - OpenAI embeddings
- `sentence-transformer` - Local sentence transformers
- `amazon-bedrock` - AWS Bedrock embeddings

#### Language Model Providers
- `openai` - OpenAI API
- `openai-compatible` - Ollama, vLLM, etc.
- `amazon-bedrock` - AWS Bedrock

#### Reranker Providers
- `identity` - No reranking
- `embedder` - Embedding-based
- `cross-encoder` - Cross-encoder models
- `bm25` - BM25 keyword matching
- `rrf-hybrid` - Reciprocal rank fusion
- `amazon-bedrock` - AWS Bedrock reranking

#### Storage Providers
- `neo4j` - Neo4j graph database
- `postgres` - PostgreSQL with pgvector

## Data Types

### Episode
```python
@dataclass
class Episode:
    content: str | list[str]
    content_type: ContentType  # TEXT, IMAGE, AUDIO, VIDEO
    producer: Identity  # role and id
    produced_for: Identity | None
    metadata: dict[str, Any]
    timestamp: datetime
```

### Identity
```python
@dataclass
class Identity:
    role: str  # "user", "agent", "system"
    id: str
```

### MemoryContext
```python
@dataclass
class MemoryContext:
    user_id: str
    agent_id: str
    session_id: str
    group_id: str | None
```

### SearchResult
```python
@dataclass
class SearchResult:
    content: str
    score: float
    metadata: dict[str, Any]
    timestamp: datetime
```
