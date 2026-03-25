#!/usr/bin/env python3
"""Configuration validator for MemMachine configuration.yml (Ollama-focused)"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)


def validate_config(config_path: Path) -> tuple[bool, list[str]]:
    """Validate configuration file for Ollama setup"""
    errors = []

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        return False, [f"Configuration file not found: {config_path}"]
    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {e}"]

    # Required top-level sections
    required_sections = ["logging", "SessionDB", "Model", "storage", "embedder", "reranker", 
                        "vector_graph_store", "profile_memory", "sessionMemory", "long_term_memory"]
    
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    if errors:
        return False, errors

    # Validate logging
    if "level" in config["logging"]:
        if config["logging"]["level"] not in ["debug", "info", "error"]:
            errors.append("logging.level must be debug, info, or error")

    # Validate Model (Ollama)
    for model_id, model_cfg in config.get("Model", {}).items():
        if model_cfg.get("model_vendor") != "openai-compatible":
            errors.append(f"Model.{model_id}.model_vendor must be 'openai-compatible' for Ollama")
        if "model" not in model_cfg:
            errors.append(f"Model.{model_id} missing 'model' field")
        if "base_url" not in model_cfg:
            errors.append(f"Model.{model_id} missing 'base_url' field")

    # Validate embedder (Ollama)
    for emb_id, emb_cfg in config.get("embedder", {}).items():
        if emb_cfg.get("provider") != "openai":
            errors.append(f"embedder.{emb_id}.provider must be 'openai' for Ollama")
        if "config" in emb_cfg:
            if "model" not in emb_cfg["config"]:
                errors.append(f"embedder.{emb_id}.config missing 'model' field")
            if "base_url" not in emb_cfg["config"]:
                errors.append(f"embedder.{emb_id}.config missing 'base_url' field")

    # Validate reranker
    for rnk_id, rnk_cfg in config.get("reranker", {}).items():
        valid_providers = ["identity", "embedder", "cross-encoder", "bm25", "rrf-hybrid"]
        if rnk_cfg.get("provider") not in valid_providers:
            errors.append(f"reranker.{rnk_id}.provider must be one of {valid_providers}")

    # Validate storage
    for stor_id, stor_cfg in config.get("storage", {}).items():
        if stor_cfg.get("vendor_name") != "postgres":
            errors.append(f"storage.{stor_id}.vendor_name must be 'postgres'")
        required_fields = ["host", "port", "user", "db_name", "password"]
        for field in required_fields:
            if field not in stor_cfg:
                errors.append(f"storage.{stor_id} missing '{field}' field")

    # Validate vector_graph_store
    for vgs_id, vgs_cfg in config.get("vector_graph_store", {}).items():
        if vgs_cfg.get("provider") != "neo4j":
            errors.append(f"vector_graph_store.{vgs_id}.provider must be 'neo4j'")
        if "config" in vgs_cfg:
            required_fields = ["uri", "username", "password"]
            for field in required_fields:
                if field not in vgs_cfg["config"]:
                    errors.append(f"vector_graph_store.{vgs_id}.config missing '{field}' field")

    # Validate references
    embedders = set(config.get("embedder", {}).keys())
    models = set(config.get("Model", {}).keys())
    storages = set(config.get("storage", {}).keys())
    rerankers = set(config.get("reranker", {}).keys())
    vgs = set(config.get("vector_graph_store", {}).keys())

    # Check default_embedder
    if "default_embedder" in config and config["default_embedder"] not in embedders:
        errors.append(f"default_embedder '{config['default_embedder']}' not found in embedder section")

    # Check long_term_memory references
    ltm = config.get("long_term_memory", {})
    if "embedder" in ltm and ltm["embedder"] not in embedders:
        errors.append(f"long_term_memory.embedder '{ltm['embedder']}' not found in embedder section")
    if "reranker" in ltm and ltm["reranker"] not in rerankers:
        errors.append(f"long_term_memory.reranker '{ltm['reranker']}' not found in reranker section")
    if "vector_graph_store" in ltm and ltm["vector_graph_store"] not in vgs:
        errors.append(f"long_term_memory.vector_graph_store '{ltm['vector_graph_store']}' not found in vector_graph_store section")
    if "database" in ltm and ltm["database"] not in storages:
        errors.append(f"long_term_memory.database '{ltm['database']}' not found in storage section")

    # Check profile_memory references
    pm = config.get("profile_memory", {})
    if "llm_model" in pm and pm["llm_model"] not in models:
        errors.append(f"profile_memory.llm_model '{pm['llm_model']}' not found in Model section")
    if "embedding_model" in pm and pm["embedding_model"] not in embedders:
        errors.append(f"profile_memory.embedding_model '{pm['embedding_model']}' not found in embedder section")
    if "database" in pm and pm["database"] not in storages:
        errors.append(f"profile_memory.database '{pm['database']}' not found in storage section")

    # Check sessionMemory references
    sm = config.get("sessionMemory", {})
    if "model_name" in sm and sm["model_name"] not in models:
        errors.append(f"sessionMemory.model_name '{sm['model_name']}' not found in Model section")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate MemMachine configuration.yml (Ollama-focused)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Validate configuration.yml in current directory
  %(prog)s config/production.yml    # Validate specific file
        """
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="configuration.yml",
        help="Path to configuration.yml (default: configuration.yml)",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    valid, messages = validate_config(config_path)

    if valid:
        print(f"✅ Configuration is valid: {config_path}")
        sys.exit(0)
    else:
        print(f"❌ Configuration validation failed: {config_path}\n")
        for msg in messages:
            print(f"  • {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
