#!/usr/bin/env python3
"""Configuration validator for MemMachine configuration.yml"""

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


class LoggingConfig(BaseModel):
    path: str
    level: str

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        if v not in ["debug", "info", "error"]:
            raise ValueError("level must be debug, info, or error")
        return v


class SessionDBConfig(BaseModel):
    uri: str


class OllamaModelConfig(BaseModel):
    model_vendor: str
    model: str
    api_key: str
    base_url: str

    @field_validator("model_vendor")
    @classmethod
    def validate_vendor(cls, v: str) -> str:
        if v != "openai-compatible":
            raise ValueError("Ollama uses openai-compatible vendor")
        return v


class OllamaEmbedderConfig(BaseModel):
    provider: str
    config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v != "openai":
            raise ValueError("Ollama embedder uses openai provider")
        return v

    @model_validator(mode="after")
    def validate_config(self) -> "OllamaEmbedderConfig":
        cfg = self.config
        if "model" not in cfg:
            raise ValueError("embedder config must have model")
        if "base_url" not in cfg:
            raise ValueError("embedder config must have base_url")
        return self


class RerankerConfig(BaseModel):
    provider: str
    config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        valid = ["identity", "embedder", "cross-encoder", "bm25", "rrf-hybrid"]
        if v not in valid:
            raise ValueError(f"provider must be one of {valid}")
        return v


class StorageConfig(BaseModel):
    vendor_name: str
    host: str
    port: int
    user: str
    db_name: str
    password: str

    @field_validator("vendor_name")
    @classmethod
    def validate_vendor(cls, v: str) -> str:
        if v != "postgres":
            raise ValueError("storage vendor_name must be postgres")
        return v


class VectorGraphStoreConfig(BaseModel):
    provider: str
    config: dict[str, Any]

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v != "neo4j":
            raise ValueError("vector_graph_store provider must be neo4j")
        return v

    @model_validator(mode="after")
    def validate_config(self) -> "VectorGraphStoreConfig":
        cfg = self.config
        if "uri" not in cfg:
            raise ValueError("neo4j config must have uri")
        if "username" not in cfg:
            raise ValueError("neo4j config must have username")
        if "password" not in cfg:
            raise ValueError("neo4j config must have password")
        return self


class ProfileMemoryConfig(BaseModel):
    llm_model: str
    embedding_model: str
    database: str
    prompt: str


class SessionMemoryConfig(BaseModel):
    model_name: str
    message_capacity: int
    max_message_length: int
    max_token_num: int


class LongTermMemoryConfig(BaseModel):
    embedder: str
    reranker: str
    vector_graph_store: str
    database: str


class MemMachineConfig(BaseModel):
    logging: LoggingConfig
    default_embedder: str
    long_term_memory: LongTermMemoryConfig
    SessionDB: SessionDBConfig
    Model: dict[str, OllamaModelConfig]
    storage: dict[str, StorageConfig]
    profile_memory: ProfileMemoryConfig
    sessionMemory: SessionMemoryConfig
    embedder: dict[str, OllamaEmbedderConfig]
    reranker: dict[str, RerankerConfig]
    vector_graph_store: dict[str, VectorGraphStoreConfig]

    @model_validator(mode="after")
    def validate_references(self) -> "MemMachineConfig":
        # Validate embedder references
        if self.default_embedder not in self.embedder:
            raise ValueError(f"default_embedder '{self.default_embedder}' not in embedder")
        if self.long_term_memory.embedder not in self.embedder:
            raise ValueError(f"long_term_memory.embedder '{self.long_term_memory.embedder}' not in embedder")
        if self.profile_memory.embedding_model not in self.embedder:
            raise ValueError(f"profile_memory.embedding_model '{self.profile_memory.embedding_model}' not in embedder")

        # Validate model references
        if self.profile_memory.llm_model not in self.Model:
            raise ValueError(f"profile_memory.llm_model '{self.profile_memory.llm_model}' not in Model")
        if self.sessionMemory.model_name not in self.Model:
            raise ValueError(f"sessionMemory.model_name '{self.sessionMemory.model_name}' not in Model")

        # Validate storage references
        if self.long_term_memory.database not in self.storage:
            raise ValueError(f"long_term_memory.database '{self.long_term_memory.database}' not in storage")
        if self.profile_memory.database not in self.storage:
            raise ValueError(f"profile_memory.database '{self.profile_memory.database}' not in storage")

        # Validate reranker references
        if self.long_term_memory.reranker not in self.reranker:
            raise ValueError(f"long_term_memory.reranker '{self.long_term_memory.reranker}' not in reranker")

        # Validate vector_graph_store references
        if self.long_term_memory.vector_graph_store not in self.vector_graph_store:
            raise ValueError(f"long_term_memory.vector_graph_store '{self.long_term_memory.vector_graph_store}' not in vector_graph_store")

        return self


def validate_config(config_path: Path) -> tuple[bool, str]:
    """Validate configuration file"""
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        MemMachineConfig(**config_data)
        return True, "✅ Configuration is valid"
    except FileNotFoundError:
        return False, f"❌ Configuration file not found: {config_path}"
    except yaml.YAMLError as e:
        return False, f"❌ YAML parsing error: {e}"
    except Exception as e:
        return False, f"❌ Validation error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Validate MemMachine configuration.yml")
    parser.add_argument(
        "config",
        nargs="?",
        default="configuration.yml",
        help="Path to configuration.yml (default: configuration.yml)",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    valid, message = validate_config(config_path)

    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
