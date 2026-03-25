#!/usr/bin/env python3
"""Validate a MemMachine YAML configuration file.

Checks:
  1. Required top-level sections exist.
  2. Resource provider/config structure is valid with correct provider names.
  3. All ID references (embedder, reranker, llm_model, database, vector_graph_store)
     resolve to defined resources.
  4. Provider-specific requirements (e.g. openai needs api_key, amazon-bedrock needs region).
  5. Database references in semantic_memory, session_manager, and episode_store are valid.

Exit codes:
  0 - valid
  1 - validation errors found
  2 - file not found or invalid YAML
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Known providers per resource kind
# ---------------------------------------------------------------------------
EMBEDDER_PROVIDERS = {"openai", "amazon-bedrock", "sentence-transformer"}
LM_PROVIDERS = {"openai-responses", "openai-chat-completions", "amazon-bedrock"}
RERANKER_PROVIDERS = {
    "bm25",
    "amazon-bedrock",
    "cohere",
    "cross-encoder",
    "embedder",
    "identity",
    "rrf-hybrid",
}
DB_PROVIDERS = {"neo4j", "postgres", "sqlite", "nebula_graph"}

REQUIRED_SECTIONS = {
    "logging",
    "episodic_memory",
    "semantic_memory",
    "session_manager",
    "resources",
    "episode_store",
}


def _errors_prefix(prefix: str, errors: list[str]) -> list[str]:
    return [f"{prefix}: {e}" for e in errors]


def _get(d: dict, *keys, default=None):
    """Nested dict get."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d


# ---------------------------------------------------------------------------
# Collect all defined resource IDs
# ---------------------------------------------------------------------------


def _collect_resource_ids(resources: dict) -> dict[str, set[str]]:
    return {
        kind: set((resources.get(kind) or {}).keys())
        for kind in ("databases", "embedders", "language_models", "rerankers")
    }


# ---------------------------------------------------------------------------
# Validate resource entries
# ---------------------------------------------------------------------------


def _validate_resource_entries(
    kind: str,
    entries: dict,
    valid_providers: set[str],
    all_ids: dict[str, set[str]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(entries, dict):
        return [f"resources.{kind} must be a mapping"]

    for rid, defn in entries.items():
        pfx = f"resources.{kind}.{rid}"
        if not isinstance(defn, dict):
            errors.append(f"{pfx}: must be a mapping with 'provider' and 'config'")
            continue

        provider = defn.get("provider")
        if not provider:
            errors.append(f"{pfx}: missing 'provider'")
        elif provider not in valid_providers:
            errors.append(
                f"{pfx}: unknown provider '{provider}' "
                f"(valid: {', '.join(sorted(valid_providers))})"
            )
        else:
            errors.extend(
                _validate_provider_config(
                    pfx, provider, defn.get("config") or {}, all_ids
                )
            )
    return errors


def _validate_provider_config(
    pfx: str,
    provider: str,
    config: dict,
    all_ids: dict[str, set[str]],
) -> list[str]:
    """Check provider-specific required fields."""
    errors: list[str] = []
    if not isinstance(config, dict):
        # identity reranker has no config
        if provider != "identity":
            errors.append(f"{pfx}: 'config' must be a mapping")
        return errors

    # OpenAI-compatible providers need api_key (may be env ref)
    if provider in ("openai", "openai-responses", "openai-chat-completions"):
        if not config.get("api_key") and not config.get("base_url"):
            errors.append(
                f"{pfx}: openai-compatible provider needs 'api_key' or 'base_url'"
            )

    # Amazon Bedrock needs region
    if provider == "amazon-bedrock" and not config.get("region"):
        errors.append(f"{pfx}: amazon-bedrock provider requires 'region'")

    # Postgres/sqlite specifics
    if provider == "postgres" and not config.get("host"):
        errors.append(f"{pfx}: postgres provider requires 'host'")
    if provider == "sqlite" and not config.get("path"):
        errors.append(f"{pfx}: sqlite provider requires 'path'")

    # Sentence-transformer needs model
    if provider == "sentence-transformer" and not config.get("model"):
        errors.append(f"{pfx}: sentence-transformer provider requires 'model'")

    # Cohere reranker needs cohere_key
    if provider == "cohere" and not config.get("cohere_key"):
        errors.append(f"{pfx}: cohere provider requires 'cohere_key'")

    # rrf-hybrid needs reranker_ids that exist
    if provider == "rrf-hybrid":
        rids = config.get("reranker_ids")
        if not rids:
            errors.append(f"{pfx}: rrf-hybrid requires 'reranker_ids'")
        elif isinstance(rids, list):
            errors.extend(
                f"{pfx}: rrf-hybrid references unknown reranker '{ref}'"
                for ref in rids
                if ref not in all_ids["rerankers"]
            )

    # embedder reranker needs embedder_id that exists
    if provider == "embedder":
        eid = config.get("embedder_id")
        if not eid:
            errors.append(f"{pfx}: embedder reranker requires 'embedder_id'")
        elif eid not in all_ids["embedders"]:
            errors.append(f"{pfx}: references unknown embedder '{eid}'")

    return errors


# ---------------------------------------------------------------------------
# Validate ID references
# ---------------------------------------------------------------------------


def _check_ref(
    errors: list[str],
    cfg: dict,
    key: str,
    pool: set[str],
    pool_label: str,
    section: str,
) -> None:
    val = cfg.get(key)
    if val and val not in pool:
        errors.append(f"{section}.{key}: references unknown {pool_label} '{val}'")


def _validate_references(cfg: dict, all_ids: dict[str, set[str]]) -> list[str]:
    errors: list[str] = []
    em = cfg.get("episodic_memory") or {}
    ltm = em.get("long_term_memory") or {}
    stm = em.get("short_term_memory") or {}

    _check_ref(
        errors,
        ltm,
        "embedder",
        all_ids["embedders"],
        "embedder",
        "episodic_memory.long_term_memory",
    )
    _check_ref(
        errors,
        ltm,
        "reranker",
        all_ids["rerankers"],
        "reranker",
        "episodic_memory.long_term_memory",
    )
    _check_ref(
        errors,
        ltm,
        "vector_graph_store",
        all_ids["databases"],
        "database",
        "episodic_memory.long_term_memory",
    )
    _check_ref(
        errors,
        stm,
        "llm_model",
        all_ids["language_models"],
        "language_model",
        "episodic_memory.short_term_memory",
    )

    sm = cfg.get("semantic_memory") or {}
    _check_ref(
        errors,
        sm,
        "llm_model",
        all_ids["language_models"],
        "language_model",
        "semantic_memory",
    )
    _check_ref(
        errors,
        sm,
        "embedding_model",
        all_ids["embedders"],
        "embedder",
        "semantic_memory",
    )
    _check_ref(
        errors, sm, "database", all_ids["databases"], "database", "semantic_memory"
    )
    _check_ref(
        errors,
        sm,
        "config_database",
        all_ids["databases"],
        "database",
        "semantic_memory",
    )

    sess = cfg.get("session_manager") or {}
    _check_ref(
        errors, sess, "database", all_ids["databases"], "database", "session_manager"
    )

    es = cfg.get("episode_store") or {}
    _check_ref(
        errors, es, "database", all_ids["databases"], "database", "episode_store"
    )

    ra = cfg.get("retrieval_agent") or {}
    _check_ref(
        errors,
        ra,
        "llm_model",
        all_ids["language_models"],
        "language_model",
        "retrieval_agent",
    )

    return errors


# ---------------------------------------------------------------------------
# Validate semantic_memory required fields
# ---------------------------------------------------------------------------


def _validate_semantic_memory(cfg: dict) -> list[str]:
    sm = cfg.get("semantic_memory")
    if not isinstance(sm, dict):
        return ["semantic_memory: must be a mapping"]
    errors: list[str] = []
    if "config_database" not in sm:
        errors.append("semantic_memory: missing required field 'config_database'")
    return errors


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------


def validate(cfg: dict) -> list[str]:
    """Return a list of error strings (empty = valid)."""
    errors: list[str] = []

    # 1. Required top-level sections
    missing = REQUIRED_SECTIONS - set(cfg.keys())
    if missing:
        errors.append(
            f"missing required top-level sections: {', '.join(sorted(missing))}"
        )

    resources = cfg.get("resources")
    if not isinstance(resources, dict):
        errors.append("resources: must be a mapping")
        return errors  # can't continue without resources

    # 2. Collect all defined IDs (needed for cross-references)
    all_ids = _collect_resource_ids(resources)

    # 3. Validate each resource kind
    for kind, providers in [
        ("embedders", EMBEDDER_PROVIDERS),
        ("language_models", LM_PROVIDERS),
        ("rerankers", RERANKER_PROVIDERS),
        ("databases", DB_PROVIDERS),
    ]:
        entries = resources.get(kind)
        if entries:
            errors.extend(_validate_resource_entries(kind, entries, providers, all_ids))

    # 4. Validate ID references
    errors.extend(_validate_references(cfg, all_ids))

    # 5. Validate semantic_memory required fields
    errors.extend(_validate_semantic_memory(cfg))

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config.yaml>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML: {exc}", file=sys.stderr)
        return 2

    if not isinstance(cfg, dict):
        print("ERROR: YAML root must be a mapping", file=sys.stderr)
        return 2

    # Lowercase all keys to match Configuration.load_yml_file behavior
    def lower_keys(d):
        if isinstance(d, dict):
            return {k.lower(): lower_keys(v) for k, v in d.items()}
        if isinstance(d, list):
            return [lower_keys(i) for i in d]
        return d

    cfg = lower_keys(cfg)

    errors = validate(cfg)
    if errors:
        print(f"Found {len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("Configuration is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
