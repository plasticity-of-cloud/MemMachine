# Data Models

## Core Data Models

### Episode
**Location:** `src/memmachine/episodic_memory/data_types.py`

```python
@dataclass
class Episode:
    """Represents a single memory episode"""
    content: str | list[str]
    content_type: ContentType
    producer: Identity
    produced_for: Identity | None
    metadata: dict[str, Any]
    timestamp: datetime
```

**Fields:**
- `content` - Episode content (text, or list for multi-turn)
- `content_type` - Content format (TEXT, IMAGE, AUDIO, VIDEO)
- `producer` - Who created the episode (user, agent, system)
- `produced_for` - Intended recipient (optional)
- `metadata` - Arbitrary key-value pairs for filtering
- `timestamp` - When the episode was created

**Usage:**
```python
episode = Episode(
    content="User asked about pricing",
    content_type=ContentType.TEXT,
    producer=Identity(role="user", id="user1"),
    produced_for=Identity(role="agent", id="agent1"),
    metadata={"topic": "pricing"},
    timestamp=datetime.now()
)
```

### Identity
**Location:** `src/memmachine/episodic_memory/data_types.py`

```python
@dataclass
class Identity:
    """Represents an entity identity"""
    role: str  # "user", "agent", "system"
    id: str
```

**Roles:**
- `user` - Human user
- `agent` - AI agent
- `system` - System-generated content

### ContentType
**Location:** `src/memmachine/episodic_memory/data_types.py`

```python
class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
```

### MemoryContext
**Location:** `src/memmachine/episodic_memory/data_types.py`

```python
@dataclass
class MemoryContext:
    """Context for memory operations"""
    user_id: str
    agent_id: str
    session_id: str
    group_id: str | None
```

**Purpose:** Identifies the scope for memory operations

### GroupConfiguration
**Location:** `src/memmachine/episodic_memory/data_types.py`

```python
@dataclass
class GroupConfiguration:
    """Group-level configuration overrides"""
    config: dict[str, Any]
```

**Purpose:** Custom configuration for specific user/agent groups

### SessionInfo
**Location:** `src/memmachine/episodic_memory/data_types.py`

```python
@dataclass
class SessionInfo:
    """Session metadata"""
    user_id: str
    agent_id: str
    session_id: str
    group_id: str | None
    created_at: datetime
```

## Declarative Memory Models

### Derivative
**Location:** `src/memmachine/episodic_memory/declarative_memory/data_types.py`

```python
@dataclass
class Derivative:
    """Processed/transformed episode content"""
    content: str
    content_type: ContentType
    metadata: dict[str, Any]
```

**Purpose:** Represents transformed episode content (summaries, extractions, etc.)

### EpisodeCluster
**Location:** `src/memmachine/episodic_memory/declarative_memory/data_types.py`

```python
@dataclass
class EpisodeCluster:
    """Group of related episodes"""
    episodes: list[Episode]
    relationships: list[tuple[str, str, str]]  # (from_id, relationship, to_id)
```

**Purpose:** Represents graph relationships between episodes

## Graph Store Models

### Node
**Location:** `src/memmachine/common/vector_graph_store/data_types.py`

```python
@dataclass
class Node:
    """Graph node with vector embedding"""
    id: str
    labels: list[str]
    properties: dict[str, Any]
    embedding: list[float] | None
```

**Fields:**
- `id` - Unique node identifier
- `labels` - Node type labels (e.g., ["Episode", "Derivative"])
- `properties` - Arbitrary properties
- `embedding` - Vector embedding for similarity search

**Property Naming:**
- Filterable properties prefixed with `fp_` (e.g., `fp_user_id`)
- Mangling/demangling handled by declarative memory layer

### Edge
**Location:** `src/memmachine/common/vector_graph_store/data_types.py`

```python
@dataclass
class Edge:
    """Graph relationship"""
    from_node_id: str
    to_node_id: str
    relationship_type: str
    properties: dict[str, Any]
```

**Common Relationship Types:**
- `RELATED_TO` - Semantic similarity
- `PREVIOUS` - Temporal predecessor
- `NEXT` - Temporal successor
- `DERIVED_FROM` - Processing lineage

## Profile Memory Models

### ProfileFeature
**Internal representation in storage layer**

```python
{
    "id": "uuid",
    "user_id": "string",
    "agent_id": "string",
    "feature_type": "preference|fact|characteristic",
    "content": "string",
    "embedding": list[float],
    "citations": list[str],
    "created_at": datetime,
    "updated_at": datetime
}
```

### HistoryMessage
**Internal representation in storage layer**

```python
{
    "id": "uuid",
    "user_id": "string",
    "agent_id": "string",
    "role": "user|agent|system",
    "content": "string",
    "ingested": bool,
    "created_at": datetime
}
```

## Session Management Models

### MemSession (SQLAlchemy)
**Location:** `src/memmachine/episodic_memory/session_manager/session_manager.py`

```python
class MemSession(Base):
    __tablename__ = "sessions"
    
    id: int  # Primary key
    session_id: str
    user_id: str
    agent_id: str
    group_id: str | None
    created_at: datetime
```

### User (SQLAlchemy)
**Location:** `src/memmachine/episodic_memory/session_manager/session_manager.py`

```python
class User(Base):
    __tablename__ = "users"
    
    id: int  # Primary key
    user_id: str  # Unique
    created_at: datetime
```

### Agent (SQLAlchemy)
**Location:** `src/memmachine/episodic_memory/session_manager/session_manager.py`

```python
class Agent(Base):
    __tablename__ = "agents"
    
    id: int  # Primary key
    agent_id: str  # Unique
    created_at: datetime
```

### GroupInfo (SQLAlchemy)
**Location:** `src/memmachine/episodic_memory/session_manager/session_manager.py`

```python
class GroupInfo(Base):
    __tablename__ = "groups"
    
    id: int  # Primary key
    group_id: str  # Unique
    config_json: str  # JSON-serialized configuration
    created_at: datetime
```

## API Request/Response Models

### AddMemoryRequest
```python
{
    "content": str | list[str],
    "metadata": dict[str, Any],
    "session": {
        "user_id": str | list[str],
        "agent_id": str | list[str],
        "session_id": str,
        "group_id": str
    },
    "producer": {
        "role": str,
        "id": str
    },
    "produced_for": {
        "role": str,
        "id": str
    }
}
```

### SearchMemoryRequest
```python
{
    "query": str,
    "limit": int,
    "session": {
        "user_id": str,
        "agent_id": str,
        "session_id": str
    },
    "filters": dict[str, Any]
}
```

### SearchMemoryResponse
```python
{
    "results": [
        {
            "content": str,
            "metadata": dict[str, Any],
            "score": float,
            "timestamp": str  # ISO format
        }
    ]
}
```

### DeleteDataRequest
```python
{
    "session": {
        "user_id": str,
        "agent_id": str,
        "session_id": str
    },
    "filters": dict[str, Any]
}
```

### SessionsResponse
```python
{
    "sessions": [
        {
            "user_id": str,
            "agent_id": str,
            "session_id": str,
            "group_id": str | None,
            "created_at": str  # ISO format
        }
    ]
}
```

## Configuration Models

### EmbedderConfig
```python
{
    "provider": str,  # "openai", "sentence-transformer", "amazon-bedrock"
    "model": str,
    "api_key": str,  # Optional
    "base_url": str,  # Optional for openai-compatible
    "dimensions": int,  # Optional
    "similarity_metric": str  # "cosine", "euclidean", "dot_product"
}
```

### LanguageModelConfig
```python
{
    "model_vendor": str,  # "openai", "openai-compatible", "amazon-bedrock"
    "model": str,
    "api_key": str,
    "base_url": str,  # Optional for openai-compatible
    "max_retry_interval_seconds": int,  # Optional
    "user_metrics_labels": dict[str, str]  # Optional
}
```

### RerankerConfig
```python
{
    "provider": str,  # "identity", "embedder", "cross-encoder", "bm25", "rrf-hybrid", "amazon-bedrock"
    "model": str,  # Optional, depends on provider
    "embedder": str,  # Required for "embedder" provider
    "rerankers": list[str],  # Required for "rrf-hybrid" provider
    "k": int  # Optional for "rrf-hybrid"
}
```

### VectorGraphStoreConfig
```python
{
    "vendor_name": str,  # "neo4j"
    "uri": str,
    "user": str,
    "password": str,
    "database": str  # Optional
}
```

### ProfileStorageConfig
```python
{
    "vendor_name": str,  # "postgres"
    "host": str,
    "port": int,
    "user": str,
    "password": str,
    "db_name": str
}
```

## Metadata Conventions

### Episode Metadata
Common metadata keys for episodes:

```python
{
    "topic": str,  # Conversation topic
    "intent": str,  # User intent
    "sentiment": str,  # Sentiment analysis
    "language": str,  # Content language
    "source": str,  # Data source
    "priority": int,  # Importance level
    "tags": list[str]  # Arbitrary tags
}
```

### Profile Feature Types
Standard feature types for profile memory:

- `preference` - User preferences
- `fact` - Factual information about user
- `characteristic` - User characteristics
- `goal` - User goals or objectives
- `constraint` - User constraints or limitations

## Filtering

### Filter Syntax
Filters use property-based matching:

```python
filters = {
    "fp_user_id": "user1",  # Exact match
    "fp_topic": "pricing",  # Exact match
    "fp_priority": 5  # Numeric match
}
```

**Note:** Filterable properties in graph store are prefixed with `fp_` internally

### Range Filters
For profile memory semantic search:

```python
range_filter = {
    "created_at": {
        "gte": "2024-01-01T00:00:00Z",
        "lte": "2024-12-31T23:59:59Z"
    }
}
```
