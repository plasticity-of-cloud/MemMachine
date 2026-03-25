# System Architecture

## Overview

MemMachine implements a three-tier memory architecture for AI agents, combining short-term working memory, long-term episodic memory, and persistent profile memory. The system is designed as a pluggable memory layer that can integrate with any AI agent framework.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[AI Agent] --> B[REST API]
        A --> C[MCP Protocol]
        A --> D[Python SDK]
    end
    
    subgraph "Memory Core"
        B --> E[Memory Manager]
        C --> E
        D --> E
        E --> F[Episodic Memory]
        E --> G[Profile Memory]
        
        F --> H[Short-Term Memory]
        F --> I[Long-Term Memory]
        
        H --> J[Session Memory]
        I --> K[Declarative Memory]
    end
    
    subgraph "Storage Layer"
        J --> L[SQLite/PostgreSQL]
        K --> M[Neo4j Graph DB]
        G --> N[PostgreSQL]
    end
    
    subgraph "AI Services"
        E --> O[LLM Provider]
        E --> P[Embedder]
        E --> Q[Reranker]
    end
```

## Core Components

### 1. Memory Manager (`episodic_memory_manager.py`)

**Responsibilities:**
- Lifecycle management of memory instances
- Configuration loading and validation
- Session and group management
- Resource initialization and cleanup

**Key Operations:**
- `create_episodic_memory_instance()` - Create new memory context
- `get_episodic_memory_instance()` - Retrieve existing memory
- `close_episodic_memory_instance()` - Clean up resources
- `create_group()` - Initialize user/agent groups

### 2. Episodic Memory (`episodic_memory.py`)

**Architecture:**
```mermaid
graph LR
    A[Episodic Memory] --> B[Short-Term Memory]
    A --> C[Long-Term Memory]
    B --> D[Session Memory]
    C --> E[Declarative Memory]
```

**Components:**
- **Short-Term Memory:** Recent conversation context (token-limited buffer)
- **Long-Term Memory:** Persistent episodic storage with semantic search

**Key Operations:**
- `add_memory_episode()` - Store new episode
- `query_memory()` - Search with context formalization
- `formalize_query_with_context()` - Enhance queries with recent context
- `get_memory_context()` - Retrieve formatted context for LLM

### 3. Profile Memory (`profile_memory.py`)

**Purpose:** Learn and store long-term user facts, preferences, and characteristics

**Architecture:**
```mermaid
graph TB
    A[Profile Memory] --> B[Ingestion Pipeline]
    A --> C[Storage Layer]
    A --> D[Query Interface]
    
    B --> E[Message Buffer]
    B --> F[LLM Processor]
    B --> G[Deduplication]
    
    C --> H[PostgreSQL]
    C --> I[Vector Search]
```

**Key Features:**
- Background ingestion of conversation history
- LLM-powered profile extraction
- Semantic search over user facts
- Citation tracking for provenance

**Key Operations:**
- `process_messages()` - Extract profile features from conversations
- `semantic_search()` - Find relevant user facts
- `add_new_profile()` - Store user profile data
- `get_user_profile()` - Retrieve complete profile

### 4. Declarative Memory (`declarative_memory.py`)

**Purpose:** Graph-based episodic storage with semantic relationships

**Architecture:**
```mermaid
graph TB
    A[Add Episode] --> B[Derivative Derivation]
    B --> C[Derivative Mutation]
    C --> D[Episode Cluster Assembly]
    D --> E[Graph Storage]
    
    F[Search] --> G[Vector Search]
    G --> H[Graph Traversal]
    H --> I[Context Expansion]
    I --> J[Reranking]
```

**Processing Pipeline:**
1. **Derivative Derivation:** Extract searchable content from episodes
2. **Derivative Mutation:** Transform content (summarization, metadata extraction)
3. **Episode Cluster Assembly:** Create graph relationships
4. **Storage:** Persist to Neo4j vector graph

**Search Strategy:**
- Vector similarity search for initial candidates
- Graph traversal for related episodes
- Context expansion (previous/next episodes)
- Reranking for relevance scoring

### 5. Session Memory (`session_memory.py`)

**Purpose:** Token-limited buffer for recent conversation context

**Features:**
- Automatic eviction when token limit exceeded
- LLM-powered summarization of evicted content
- Maintains conversation continuity

**Eviction Strategy:**
```mermaid
sequenceDiagram
    participant A as Add Episode
    participant B as Token Counter
    participant C as Eviction Logic
    participant D as LLM Summarizer
    participant E as Long-Term Memory
    
    A->>B: Check capacity
    B->>C: Exceeds limit
    C->>D: Summarize old episodes
    D->>E: Store summary
    C->>A: Remove old episodes
```

## Storage Architecture

### Neo4j Graph Database (Episodic Memory)

**Node Types:**
- **Episode:** Individual memory units with embeddings
- **Derivative:** Processed/transformed episode content

**Relationships:**
- **RELATED_TO:** Semantic similarity
- **PREVIOUS/NEXT:** Temporal ordering
- **DERIVED_FROM:** Processing lineage

**Indexes:**
- Vector index on episode embeddings
- Property indexes on metadata fields

### PostgreSQL (Profile Memory)

**Tables:**
- `profile_features` - User facts and preferences
- `history_messages` - Conversation history buffer
- `citations` - Source tracking for profile features

**Extensions:**
- `pgvector` - Vector similarity search

### SQLite/PostgreSQL (Session Management)

**Tables:**
- `groups` - User/agent group definitions
- `users` - User identities
- `agents` - Agent identities
- `sessions` - Active memory sessions

## Integration Patterns

### REST API Integration

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API Server
    participant M as Memory Manager
    participant E as Episodic Memory
    participant P as Profile Memory
    
    C->>A: POST /v1/memories
    A->>M: Get memory instance
    M->>E: Add episode
    M->>P: Queue for ingestion
    E-->>A: Success
    A-->>C: 200 OK
```

### MCP Protocol Integration

```mermaid
sequenceDiagram
    participant A as AI Agent
    participant M as MCP Server
    participant E as Memory Core
    
    A->>M: add_memory(content, context)
    M->>E: Process and store
    E-->>M: Success
    M-->>A: Tool result
    
    A->>M: search_memory(query, context)
    M->>E: Search with context
    E-->>M: Relevant memories
    M-->>A: Formatted results
```

## Extensibility Points

### Custom Components

**Embedders:** Implement `Embedder` interface
- `ingest_embed()` - Generate embeddings for storage
- `search_embed()` - Generate query embeddings

**Language Models:** Implement `LanguageModel` interface
- `generate_response()` - Generate completions with tool support

**Rerankers:** Implement `Reranker` interface
- `score()` - Rerank search results

**Storage:** Implement `VectorGraphStore` or `ProfileStorageBase`
- Custom database backends

### Configuration-Driven Architecture

All components are instantiated via configuration files using the builder pattern:
- `EmbedderBuilder`
- `LanguageModelBuilder`
- `RerankerBuilder`
- `VectorGraphStoreBuilder`

## Deployment Architecture

### Docker Compose Deployment

```mermaid
graph TB
    A[memmachine-server] --> B[Neo4j]
    A --> C[PostgreSQL]
    A --> D[LLM Provider]
    E[Client] --> A
```

**Services:**
- `memmachine-server` - Main API server
- `neo4j` - Graph database
- `postgres` - Profile storage

**Networking:**
- Internal network for service communication
- Exposed ports for client access

### Scaling Considerations

**Horizontal Scaling:**
- Stateless API servers (session state in database)
- Shared Neo4j and PostgreSQL instances

**Vertical Scaling:**
- GPU support for local embeddings
- Increased memory for larger session buffers

**Performance Optimization:**
- Connection pooling for databases
- Async I/O throughout
- Background processing for profile ingestion
