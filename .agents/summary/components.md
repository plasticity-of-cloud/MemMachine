# Components

## Memory Components

### Episodic Memory Manager
**Location:** `src/memmachine/episodic_memory/episodic_memory_manager.py`

**Responsibilities:**
- Singleton manager for all episodic memory instances
- Configuration management and validation
- Session lifecycle management
- Group and user management

**Key Classes:**
- `EpisodicMemoryManager` - Main manager singleton
- `SessionInfo` - Session metadata container
- `GroupConfiguration` - Group-level configuration

**Key Methods:**
- `create_episodic_memory_instance(user_id, agent_id, session_id, group_id)` - Create new memory
- `get_episodic_memory_instance(user_id, agent_id, session_id)` - Retrieve existing
- `close_episodic_memory_instance(user_id, agent_id, session_id)` - Cleanup
- `create_group(group_id, config)` - Initialize group with custom config

### Episodic Memory
**Location:** `src/memmachine/episodic_memory/episodic_memory.py`

**Responsibilities:**
- Unified interface for short-term and long-term memory
- Query formalization with context
- Memory context generation for LLM prompts

**Key Classes:**
- `EpisodicMemory` - Synchronous interface
- `AsyncEpisodicMemory` - Async context manager interface

**Key Methods:**
- `add_memory_episode(episode)` - Store new episode in both memory tiers
- `query_memory(query, limit, filters)` - Search long-term memory
- `formalize_query_with_context(query)` - Enhance query with recent context
- `get_memory_context()` - Get formatted context for LLM
- `delete_data(filters)` - Remove episodes matching criteria

### Profile Memory
**Location:** `src/memmachine/profile_memory/profile_memory.py`

**Responsibilities:**
- Extract and store long-term user facts
- Background ingestion of conversation history
- Semantic search over user profiles
- Deduplication and consolidation

**Key Classes:**
- `ProfileMemory` - Main profile memory interface
- `ProfileUpdateTracker` - Rate limiting for profile updates
- `ConsolidateMemory` - Metadata for consolidation tasks

**Key Methods:**
- `add_persona_message(message)` - Queue message for ingestion
- `process_messages(user_id, agent_id)` - Extract profile features
- `semantic_search(query, user_id, limit)` - Search user facts
- `get_user_profile(user_id, agent_id)` - Retrieve complete profile
- `delete_user_profile(user_id, agent_id)` - Remove profile data

**Background Processing:**
- Automatic ingestion triggered by message count or time threshold
- LLM-powered extraction of facts, preferences, and characteristics
- Citation tracking for provenance

### Declarative Memory
**Location:** `src/memmachine/episodic_memory/declarative_memory/declarative_memory.py`

**Responsibilities:**
- Graph-based episodic storage
- Semantic search with graph traversal
- Episode processing pipeline

**Key Classes:**
- `DeclarativeMemory` - Main declarative memory interface
- `Workflow` - Processing pipeline abstraction

**Key Methods:**
- `add_episode(episode)` - Process and store episode
- `search(query, limit, filters)` - Multi-stage search
- `forget_all()` - Clear all episodes
- `forget_filtered_episodes(filters)` - Selective deletion

**Processing Workflows:**
1. **Derivative Derivation:** Extract searchable content
2. **Derivative Mutation:** Transform/summarize content
3. **Episode Cluster Assembly:** Create graph relationships

### Session Memory
**Location:** `src/memmachine/episodic_memory/short_term_memory/session_memory.py`

**Responsibilities:**
- Token-limited conversation buffer
- Automatic eviction with summarization
- Recent context management

**Key Classes:**
- `SessionMemory` - Session-scoped memory buffer

**Key Methods:**
- `add_episode(episode)` - Add to buffer with eviction check
- `get_session_memory_context()` - Get formatted context
- `clear_memory()` - Reset buffer
- `close()` - Cleanup resources

**Eviction Strategy:**
- Token counting for capacity management
- LLM-powered summarization of evicted content
- Summary stored in long-term memory

### Session Manager
**Location:** `src/memmachine/episodic_memory/session_manager/session_manager.py`

**Responsibilities:**
- Persistent session state management
- User and agent identity management
- Group management

**Key Classes:**
- `SessionManager` - Database-backed session manager
- `MemSession` - SQLAlchemy session model
- `User` - User identity model
- `Agent` - Agent identity model
- `GroupInfo` - Group configuration model

**Key Methods:**
- `create_session(user_id, agent_id, session_id, group_id)` - Create session
- `open_session(user_id, agent_id, session_id)` - Retrieve session
- `delete_session(user_id, agent_id, session_id)` - Remove session
- `create_new_group(group_id, config)` - Initialize group

## AI Service Components

### Embedder
**Location:** `src/memmachine/common/embedder/`

**Implementations:**
- `OpenAIEmbedder` - OpenAI embeddings API
- `SentenceTransformerEmbedder` - Local sentence transformers
- `AmazonBedrockEmbedder` - AWS Bedrock embeddings

**Interface:**
- `ingest_embed(texts)` - Generate embeddings for storage
- `search_embed(text)` - Generate query embedding
- `dimensions` - Embedding dimensionality
- `similarity_metric` - Distance metric (cosine, euclidean, etc.)

**Builder:** `EmbedderBuilder` - Configuration-driven instantiation

### Language Model
**Location:** `src/memmachine/common/language_model/`

**Implementations:**
- `OpenAILanguageModel` - OpenAI API
- `OpenAICompatibleLanguageModel` - Ollama, vLLM, etc.
- `AmazonBedrockLanguageModel` - AWS Bedrock

**Interface:**
- `generate_response(messages, tools, tool_choice)` - Generate completion

**Features:**
- Tool/function calling support
- Automatic retry with exponential backoff
- Metrics collection (Prometheus)
- Error mapping and handling

**Builder:** `LanguageModelBuilder` - Configuration-driven instantiation

### Reranker
**Location:** `src/memmachine/common/reranker/`

**Implementations:**
- `IdentityReranker` - No reranking (pass-through)
- `EmbedderReranker` - Embedding-based similarity
- `CrossEncoderReranker` - Cross-encoder models
- `BM25Reranker` - BM25 keyword matching
- `RRFHybridReranker` - Reciprocal rank fusion
- `AmazonBedrockReranker` - AWS Bedrock reranking

**Interface:**
- `score(query, candidates)` - Score and rerank candidates
- `rerank(query, candidates)` - Convenience method

**Builder:** `RerankerBuilder` - Configuration-driven instantiation

## Storage Components

### Vector Graph Store
**Location:** `src/memmachine/common/vector_graph_store/`

**Implementations:**
- `Neo4jVectorGraphStore` - Neo4j graph database

**Interface:**
- `add_nodes(nodes)` - Insert nodes with embeddings
- `add_edges(edges)` - Create relationships
- `search_similar_nodes(embedding, limit)` - Vector search
- `search_related_nodes(node_id, relationship, limit)` - Graph traversal
- `search_directional_nodes(node_id, direction, limit)` - Directional traversal
- `search_matching_nodes(filters)` - Property-based search
- `delete_nodes(filters)` - Remove nodes
- `clear_data()` - Delete all data

**Data Types:**
- `Node` - Graph node with properties and embedding
- `Edge` - Graph relationship with properties

**Builder:** `VectorGraphStoreBuilder` - Configuration-driven instantiation

### Profile Storage
**Location:** `src/memmachine/profile_memory/storage/`

**Implementations:**
- `AsyncPgProfileStorage` - PostgreSQL with pgvector

**Interface:**
- `add_profile_feature(user_id, agent_id, feature)` - Store profile fact
- `get_profile(user_id, agent_id)` - Retrieve profile
- `semantic_search(query_embedding, user_id, limit)` - Vector search
- `add_history(user_id, agent_id, message)` - Queue message
- `get_history_messages_by_ingestion_status(user_id, agent_id, ingested)` - Get messages
- `mark_messages_ingested(message_ids)` - Update ingestion status
- `delete_profile(user_id, agent_id)` - Remove profile

**Schema Management:**
- `syncschema.py` - Database schema synchronization tool

## Server Components

### REST API Server
**Location:** `src/memmachine/server/app.py`

**Framework:** FastAPI

**Endpoints:**
- `POST /v1/memories` - Add memories
- `POST /v1/memories/search` - Search memories
- `POST /v1/memories/episodic` - Add episodic memories
- `POST /v1/memories/episodic/search` - Search episodic
- `POST /v1/memories/profile` - Add profile memories
- `POST /v1/memories/profile/search` - Search profile
- `DELETE /v1/memories` - Delete memories
- `GET /v1/sessions/user/{user_id}` - Get user sessions
- `GET /v1/sessions/agent/{agent_id}` - Get agent sessions
- `GET /v1/sessions/group/{group_id}` - Get group sessions
- `GET /v1/sessions` - Get all sessions
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

**Middleware:**
- `UserIDContextMiddleware` - User ID context propagation
- CORS middleware
- Prometheus metrics middleware

### MCP Server
**Location:** `src/memmachine/server/mcp_stdio.py`, `mcp_http.py`

**Protocol:** Model Context Protocol (MCP)

**Tools:**
- `add_memory` - Store new memories
- `search_memory` - Query memory stores

**Transports:**
- stdio - Standard input/output
- HTTP - HTTP server

### Python SDK
**Location:** `src/memmachine/rest_client/`

**Classes:**
- `MemMachineClient` - Main client interface
- `Memory` - Memory operations for specific context

**Usage:**
```python
client = MemMachineClient(base_url="http://localhost:8000")
memory = client.memory(user_id="user1", agent_id="agent1")
memory.add(content="Hello world", producer="user")
results = memory.search(query="greeting")
```

## Utility Components

### Resource Initializer
**Location:** `src/memmachine/common/resource_initializer.py`

**Responsibilities:**
- Dependency resolution for components
- Ordered initialization based on dependencies
- Startup/cleanup lifecycle management

**Key Methods:**
- `initialize(resources)` - Initialize all resources in dependency order
- `order_resources(resources)` - Topological sort by dependencies

### Metrics Factory
**Location:** `src/memmachine/common/metrics_factory/`

**Implementations:**
- `PrometheusMetricsFactory` - Prometheus metrics

**Interface:**
- `get_counter(name, description, labels)` - Create counter
- `get_gauge(name, description, labels)` - Create gauge
- `get_histogram(name, description, labels, buckets)` - Create histogram
- `get_summary(name, description, labels)` - Create summary

### Builder Pattern
**Location:** `src/memmachine/common/builder.py`

**Base Class:** `Builder`

**Interface:**
- `build(config)` - Instantiate component from configuration
- `get_dependency_ids(config)` - Extract dependency identifiers

**Implementations:**
- `EmbedderBuilder`
- `LanguageModelBuilder`
- `RerankerBuilder`
- `VectorGraphStoreBuilder`
- `MetricsFactoryBuilder`
