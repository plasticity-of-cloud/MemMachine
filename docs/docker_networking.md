# Docker Compose Networking Quick Reference

## Service Name Resolution

In Docker Compose, containers communicate using **service names** as hostnames.

### From docker-compose.yml

```yaml
services:
  postgres:        # Service name → hostname "postgres"
  neo4j:          # Service name → hostname "neo4j"
  memmachine:     # Service name → hostname "memmachine"
```

## Configuration Mapping

| Service | Docker Compose | Configuration Value |
|---------|---------------|---------------------|
| PostgreSQL | `postgres` | `host: postgres` |
| Neo4j | `neo4j` | `uri: bolt://neo4j:7687` |
| Ollama (host) | N/A | `base_url: http://host.docker.internal:11434/v1` |

## Common Mistakes

### ❌ Wrong - Using localhost
```yaml
storage:
  profile_storage:
    host: localhost  # WRONG - doesn't work between containers
```

### ✅ Correct - Using service name
```yaml
storage:
  profile_storage:
    host: postgres  # CORRECT - uses Docker service name
```

### ❌ Wrong - Using localhost for Neo4j
```yaml
vector_graph_store:
  neo4j_store:
    config:
      uri: bolt://localhost:7687  # WRONG
```

### ✅ Correct - Using service name for Neo4j
```yaml
vector_graph_store:
  neo4j_store:
    config:
      uri: bolt://neo4j:7687  # CORRECT
```

### ✅ Correct - Accessing host Ollama
```yaml
Model:
  ollama_model:
    base_url: http://host.docker.internal:11434/v1  # CORRECT - accesses host
```

## Network Architecture

```
┌─────────────────────────────────────────────────┐
│ Host Machine                                     │
│                                                  │
│  Ollama (port 11434)                            │
│     ↑                                            │
│     │ host.docker.internal                       │
│     │                                            │
│  ┌──┴──────────────────────────────────────┐   │
│  │ Docker Network: memmachine-network       │   │
│  │                                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌────────┐│   │
│  │  │memmachine│←→│ postgres │  │ neo4j  ││   │
│  │  │   app    │  │          │  │        ││   │
│  │  └──────────┘  └──────────┘  └────────┘│   │
│  │       ↑              ↑            ↑      │   │
│  │       │              │            │      │   │
│  │   Service names: postgres, neo4j         │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Port Mapping

Ports are mapped from container to host in docker-compose.yml:

```yaml
postgres:
  ports:
    - "5432:5432"  # host:container

neo4j:
  ports:
    - "7687:7687"  # Bolt protocol
    - "7474:7474"  # HTTP UI

memmachine:
  ports:
    - "8080:8080"  # API server
```

**From host machine:** Use `localhost:5432`, `localhost:7687`, etc.  
**From containers:** Use service names `postgres:5432`, `neo4j:7687`, etc.

## Troubleshooting

### Cannot connect to postgres
**Problem:** Using `localhost` instead of service name  
**Solution:** Change `host: localhost` to `host: postgres`

### Cannot connect to neo4j
**Problem:** Using `localhost` instead of service name  
**Solution:** Change `bolt://localhost:7687` to `bolt://neo4j:7687`

### Cannot connect to Ollama
**Problem:** Using `localhost` from container  
**Solution:** Use `http://host.docker.internal:11434/v1`

### Ollama not accessible
**Problem:** Ollama not running on host  
**Solution:** Start Ollama on host: `ollama serve`

## Validation

Always validate your configuration:

```bash
python3 tools/validate_config_simple.py configuration.yml
```

The validator checks structure but not network connectivity. Test actual connectivity after starting services.
