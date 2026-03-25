# Workflows

## Memory Addition Workflow

### Episodic Memory Addition

```mermaid
sequenceDiagram
    participant C as Client
    participant API as REST API
    participant EM as Episodic Memory
    participant STM as Short-Term Memory
    participant LTM as Long-Term Memory
    participant PM as Profile Memory
    
    C->>API: POST /v1/memories
    API->>EM: add_memory_episode()
    
    par Short-Term Storage
        EM->>STM: add_episode()
        STM->>STM: Check token capacity
        alt Capacity exceeded
            STM->>STM: Summarize old episodes
            STM->>LTM: Store summary
            STM->>STM: Evict old episodes
        end
    and Long-Term Storage
        EM->>LTM: add_episode()
        LTM->>LTM: Derive derivatives
        LTM->>LTM: Mutate derivatives
        LTM->>LTM: Assemble clusters
        LTM->>LTM: Store in graph
    and Profile Ingestion
        EM->>PM: add_persona_message()
        PM->>PM: Queue for background processing
    end
    
    API-->>C: Success response
```

**Steps:**
1. Client sends episode to API
2. API validates and routes to episodic memory
3. Episode added to short-term memory (with eviction if needed)
4. Episode processed and stored in long-term memory graph
5. Episode queued for profile extraction
6. Success response returned to client

### Profile Memory Ingestion

```mermaid
sequenceDiagram
    participant BG as Background Task
    participant PM as Profile Memory
    participant Storage as Profile Storage
    participant LLM as Language Model
    participant Embedder as Embedder
    
    BG->>PM: Periodic trigger
    PM->>Storage: Get uningested messages
    
    alt Messages available
        PM->>LLM: Extract profile features
        LLM-->>PM: Feature list
        
        loop For each feature
            PM->>PM: Deduplicate
            PM->>Embedder: Generate embedding
            Embedder-->>PM: Embedding vector
            PM->>Storage: Store feature
        end
        
        PM->>Storage: Mark messages ingested
    end
```

**Triggers:**
- Message count threshold (default: 10 messages)
- Time threshold (default: 5 minutes since first message)

**Steps:**
1. Background task checks for uningested messages
2. Messages retrieved from storage
3. LLM extracts profile features (facts, preferences, characteristics)
4. Features deduplicated against existing profile
5. Embeddings generated for semantic search
6. Features stored with citations
7. Messages marked as ingested

## Memory Search Workflow

### Episodic Memory Search

```mermaid
sequenceDiagram
    participant C as Client
    participant API as REST API
    participant EM as Episodic Memory
    participant STM as Short-Term Memory
    participant LTM as Long-Term Memory
    
    C->>API: POST /v1/memories/search
    API->>EM: query_memory()
    
    EM->>STM: get_session_memory_context()
    STM-->>EM: Recent context
    
    EM->>EM: formalize_query_with_context()
    
    EM->>LTM: search()
    
    LTM->>LTM: Vector search
    LTM->>LTM: Graph traversal
    LTM->>LTM: Context expansion
    LTM->>LTM: Reranking
    
    LTM-->>EM: Search results
    EM-->>API: Formatted results
    API-->>C: JSON response
```

**Steps:**
1. Client sends search query
2. Recent context retrieved from short-term memory
3. Query formalized with context (LLM-enhanced)
4. Vector search finds similar episodes
5. Graph traversal finds related episodes
6. Context expansion includes previous/next episodes
7. Reranking scores final relevance
8. Results returned to client

### Profile Memory Search

```mermaid
sequenceDiagram
    participant C as Client
    participant API as REST API
    participant PM as Profile Memory
    participant Embedder as Embedder
    participant Storage as Profile Storage
    
    C->>API: POST /v1/memories/profile/search
    API->>PM: semantic_search()
    
    PM->>Embedder: search_embed(query)
    Embedder-->>PM: Query embedding
    
    PM->>Storage: semantic_search()
    Storage->>Storage: Vector similarity search
    Storage-->>PM: Matching features
    
    PM->>Storage: get_citations()
    Storage-->>PM: Citation details
    
    PM-->>API: Features with citations
    API-->>C: JSON response
```

**Steps:**
1. Client sends search query
2. Query embedded using embedder
3. Vector similarity search in PostgreSQL
4. Matching features retrieved
5. Citations fetched for provenance
6. Results returned with source information

## Session Management Workflow

### Session Creation

```mermaid
sequenceDiagram
    participant C as Client
    participant API as REST API
    participant Manager as Memory Manager
    participant SessionMgr as Session Manager
    participant DB as Session DB
    
    C->>API: POST /v1/memories (new session)
    API->>Manager: get_episodic_memory_instance()
    
    Manager->>SessionMgr: create_session_if_not_exist()
    
    SessionMgr->>DB: Check if session exists
    
    alt Session not found
        SessionMgr->>DB: Create user (if needed)
        SessionMgr->>DB: Create agent (if needed)
        SessionMgr->>DB: Create session
    end
    
    SessionMgr-->>Manager: Session info
    Manager->>Manager: Initialize memory components
    Manager-->>API: Memory instance
    API-->>C: Success
```

**Steps:**
1. Client makes request with session context
2. Manager checks for existing memory instance
3. Session manager checks database
4. User and agent created if needed
5. Session record created
6. Memory components initialized
7. Instance cached in manager

### Session Cleanup

```mermaid
sequenceDiagram
    participant API as REST API
    participant Manager as Memory Manager
    participant EM as Episodic Memory
    participant STM as Short-Term Memory
    participant LTM as Long-Term Memory
    
    API->>Manager: close_episodic_memory_instance()
    Manager->>EM: close()
    
    EM->>STM: close()
    STM->>STM: Flush pending summaries
    
    EM->>LTM: (no explicit close)
    
    Manager->>Manager: Remove from cache
```

**Steps:**
1. API requests session closure
2. Manager retrieves memory instance
3. Short-term memory flushes pending data
4. Resources released
5. Instance removed from cache

## Configuration Loading Workflow

```mermaid
sequenceDiagram
    participant App as Application
    participant Manager as Memory Manager
    participant Builder as Component Builders
    participant Init as Resource Initializer
    
    App->>Manager: Initialize
    Manager->>Manager: Load configuration.yml
    Manager->>Manager: Substitute env variables
    
    Manager->>Builder: Build embedders
    Manager->>Builder: Build language models
    Manager->>Builder: Build rerankers
    Manager->>Builder: Build storage
    
    Manager->>Init: initialize(resources)
    Init->>Init: Resolve dependencies
    Init->>Init: Topological sort
    
    loop For each resource
        Init->>Init: Call startup()
    end
    
    Init-->>Manager: Initialized resources
    Manager-->>App: Ready
```

**Steps:**
1. Application starts
2. Configuration file loaded
3. Environment variables substituted
4. Component builders instantiate configured components
5. Resource initializer resolves dependencies
6. Components initialized in dependency order
7. System ready for requests

## Derivative Processing Workflow

### Derivative Derivation

```mermaid
graph LR
    A[Episode] --> B[Derivative Deriver]
    B --> C[Identity Deriver]
    B --> D[Sentence Deriver]
    B --> E[Concatenation Deriver]
    C --> F[Derivative]
    D --> F
    E --> F
```

**Derivers:**
- **Identity:** Pass-through (no transformation)
- **Sentence:** Split into sentences
- **Concatenation:** Combine multiple episodes

**Purpose:** Extract searchable content from episodes

### Derivative Mutation

```mermaid
graph LR
    A[Derivative] --> B[Derivative Mutator]
    B --> C[Identity Mutator]
    B --> D[LLM Mutator]
    B --> E[Metadata Mutator]
    C --> F[Mutated Derivative]
    D --> F
    E --> F
```

**Mutators:**
- **Identity:** No mutation
- **LLM:** Summarize or transform with LLM
- **Metadata:** Extract metadata fields

**Purpose:** Transform content for better search/storage

### Episode Cluster Assembly

```mermaid
graph TB
    A[Episodes] --> B[Related Episode Postulator]
    B --> C[Null Postulator]
    B --> D[Previous Postulator]
    C --> E[Episode Cluster]
    D --> E
    E --> F[Graph Relationships]
```

**Postulators:**
- **Null:** No relationships
- **Previous:** Link to previous episode in session

**Purpose:** Create graph structure for traversal

## Docker Compose Startup Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant Script as memmachine-compose.sh
    participant Docker as Docker Compose
    participant Neo4j as Neo4j Container
    participant Postgres as Postgres Container
    participant Server as MemMachine Server
    
    U->>Script: ./memmachine-compose.sh
    Script->>Script: Check dependencies
    Script->>Script: Load/create .env
    Script->>Script: Configure models
    Script->>Script: Generate configuration.yml
    
    Script->>Docker: docker compose up -d
    Docker->>Neo4j: Start container
    Docker->>Postgres: Start container
    
    Script->>Script: Wait for Neo4j health
    Script->>Script: Wait for Postgres health
    
    Docker->>Server: Start container
    Server->>Server: Load configuration
    Server->>Server: Initialize resources
    Server->>Server: Start API server
    
    Script-->>U: Services ready
```

**Steps:**
1. User runs compose script
2. Script validates Docker installation
3. Environment file created/loaded
4. User selects LLM and embedding providers
5. Configuration file generated
6. Docker Compose starts services
7. Script waits for database health checks
8. MemMachine server starts
9. API ready for requests

## Testing Workflow

### Unit Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/memmachine/episodic_memory/test_episodic_memory.py

# Run with coverage
pytest --cov=memmachine

# Run integration tests only
pytest -m integration
```

### Integration Test Workflow

```mermaid
sequenceDiagram
    participant Test as Test Suite
    participant TC as Testcontainers
    participant Neo4j as Neo4j Container
    participant Postgres as Postgres Container
    participant Code as Code Under Test
    
    Test->>TC: Start containers
    TC->>Neo4j: Launch Neo4j
    TC->>Postgres: Launch Postgres
    
    TC-->>Test: Connection info
    
    Test->>Code: Run tests
    Code->>Neo4j: Database operations
    Code->>Postgres: Database operations
    
    Test->>TC: Stop containers
    TC->>Neo4j: Cleanup
    TC->>Postgres: Cleanup
```

**Features:**
- Automatic container lifecycle management
- Isolated test environments
- Real database testing

## Migration Workflow (ChatGPT to MemMachine)

```mermaid
sequenceDiagram
    participant Tool as Migration Tool
    participant File as conversations.json
    participant OpenAI as OpenAI API
    participant MM as MemMachine API
    
    Tool->>File: Load conversations
    
    loop For each conversation
        Tool->>Tool: Extract messages
        Tool->>OpenAI: Summarize conversation
        OpenAI-->>Tool: Summary
        
        loop For each message
            Tool->>MM: POST /v1/memories
        end
        
        Tool->>MM: POST /v1/memories (summary)
    end
```

**Tool:** `tools/chatgpt2memmachine/migration.py`

**Steps:**
1. Load ChatGPT export file
2. Parse conversations
3. Generate summaries with OpenAI
4. Upload messages to MemMachine
5. Upload summaries as context
