#!/usr/bin/env python3
"""Test configuration validator"""

import tempfile
from pathlib import Path

import yaml

# Import validator
import sys
sys.path.insert(0, str(Path(__file__).parent))
from validate_config_simple import validate_config


def test_valid_config():
    """Test valid Ollama configuration"""
    config = {
        "logging": {"path": "/tmp/log", "level": "info"},
        "default_embedder": "ollama_embedder",
        "long_term_memory": {
            "embedder": "ollama_embedder",
            "reranker": "my_reranker",
            "vector_graph_store": "neo4j_store",
            "database": "profile_storage"
        },
        "SessionDB": {"uri": "sqlite:///test.db"},
        "Model": {
            "ollama_model": {
                "model_vendor": "openai-compatible",
                "model": "phi4-mini",
                "api_key": "EMPTY",
                "base_url": "http://localhost:11434/v1"
            }
        },
        "storage": {
            "profile_storage": {
                "vendor_name": "postgres",
                "host": "localhost",
                "port": 5432,
                "user": "test",
                "db_name": "test",
                "password": "test"
            }
        },
        "profile_memory": {
            "llm_model": "ollama_model",
            "embedding_model": "ollama_embedder",
            "database": "profile_storage",
            "prompt": "profile_prompt"
        },
        "sessionMemory": {
            "model_name": "ollama_model",
            "message_capacity": 500,
            "max_message_length": 16000,
            "max_token_num": 8000
        },
        "embedder": {
            "ollama_embedder": {
                "provider": "openai",
                "config": {
                    "model": "nomic-embed-text",
                    "api_key": "EMPTY",
                    "base_url": "http://localhost:11434/v1",
                    "dimensions": 768
                }
            }
        },
        "reranker": {
            "my_reranker": {
                "provider": "embedder",
                "config": {"embedder_id": "ollama_embedder"}
            }
        },
        "vector_graph_store": {
            "neo4j_store": {
                "provider": "neo4j",
                "config": {
                    "uri": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "test"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config, f)
        temp_path = Path(f.name)
    
    try:
        valid, errors = validate_config(temp_path)
        assert valid, f"Valid config failed: {errors}"
        print("✅ Valid config test passed")
    finally:
        temp_path.unlink()


def test_invalid_model_vendor():
    """Test invalid model vendor"""
    config = {
        "logging": {"path": "/tmp/log", "level": "info"},
        "default_embedder": "ollama_embedder",
        "long_term_memory": {
            "embedder": "ollama_embedder",
            "reranker": "my_reranker",
            "vector_graph_store": "neo4j_store",
            "database": "profile_storage"
        },
        "SessionDB": {"uri": "sqlite:///test.db"},
        "Model": {
            "ollama_model": {
                "model_vendor": "openai",  # Wrong vendor
                "model": "phi4-mini",
                "api_key": "EMPTY",
                "base_url": "http://localhost:11434/v1"
            }
        },
        "storage": {
            "profile_storage": {
                "vendor_name": "postgres",
                "host": "localhost",
                "port": 5432,
                "user": "test",
                "db_name": "test",
                "password": "test"
            }
        },
        "profile_memory": {
            "llm_model": "ollama_model",
            "embedding_model": "ollama_embedder",
            "database": "profile_storage",
            "prompt": "profile_prompt"
        },
        "sessionMemory": {
            "model_name": "ollama_model",
            "message_capacity": 500,
            "max_message_length": 16000,
            "max_token_num": 8000
        },
        "embedder": {
            "ollama_embedder": {
                "provider": "openai",
                "config": {
                    "model": "nomic-embed-text",
                    "api_key": "EMPTY",
                    "base_url": "http://localhost:11434/v1",
                    "dimensions": 768
                }
            }
        },
        "reranker": {
            "my_reranker": {
                "provider": "embedder",
                "config": {"embedder_id": "ollama_embedder"}
            }
        },
        "vector_graph_store": {
            "neo4j_store": {
                "provider": "neo4j",
                "config": {
                    "uri": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "test"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config, f)
        temp_path = Path(f.name)
    
    try:
        valid, errors = validate_config(temp_path)
        assert not valid, "Invalid config should fail"
        assert any("openai-compatible" in e for e in errors), f"Expected vendor error, got: {errors}"
        print("✅ Invalid model vendor test passed")
    finally:
        temp_path.unlink()


def test_broken_reference():
    """Test broken reference"""
    config = {
        "logging": {"path": "/tmp/log", "level": "info"},
        "default_embedder": "ollama_embedder",
        "long_term_memory": {
            "embedder": "ollama_embedder",
            "reranker": "my_reranker",
            "vector_graph_store": "neo4j_store",
            "database": "profile_storage"
        },
        "SessionDB": {"uri": "sqlite:///test.db"},
        "Model": {
            "ollama_model": {
                "model_vendor": "openai-compatible",
                "model": "phi4-mini",
                "api_key": "EMPTY",
                "base_url": "http://localhost:11434/v1"
            }
        },
        "storage": {
            "profile_storage": {
                "vendor_name": "postgres",
                "host": "localhost",
                "port": 5432,
                "user": "test",
                "db_name": "test",
                "password": "test"
            }
        },
        "profile_memory": {
            "llm_model": "missing_model",  # Broken reference
            "embedding_model": "ollama_embedder",
            "database": "profile_storage",
            "prompt": "profile_prompt"
        },
        "sessionMemory": {
            "model_name": "ollama_model",
            "message_capacity": 500,
            "max_message_length": 16000,
            "max_token_num": 8000
        },
        "embedder": {
            "ollama_embedder": {
                "provider": "openai",
                "config": {
                    "model": "nomic-embed-text",
                    "api_key": "EMPTY",
                    "base_url": "http://localhost:11434/v1",
                    "dimensions": 768
                }
            }
        },
        "reranker": {
            "my_reranker": {
                "provider": "embedder",
                "config": {"embedder_id": "ollama_embedder"}
            }
        },
        "vector_graph_store": {
            "neo4j_store": {
                "provider": "neo4j",
                "config": {
                    "uri": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "test"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config, f)
        temp_path = Path(f.name)
    
    try:
        valid, errors = validate_config(temp_path)
        assert not valid, "Config with broken reference should fail"
        assert any("missing_model" in e for e in errors), f"Expected reference error, got: {errors}"
        print("✅ Broken reference test passed")
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    print("Running validator tests...\n")
    test_valid_config()
    test_invalid_model_vendor()
    test_broken_reference()
    print("\n✅ All tests passed!")
