from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


NODE_TIER_POLICY_PATH = Path("backend/registry/skill_registry/node_tier_policy.yaml")
LOCAL_SKILL_OVERRIDES_PATH = Path("backend/registry/skill_registry/local_skill_overrides.yaml")
VALID_NODE_MODES = {"parent", "lite", "standard", "execution"}
VALID_NODE_PROFILES = {"routing_parent", "lite_research_leaf", "evidence_leaf", "hard_gate"}
VALID_EXECUTION_PROFILES = {"experiment_execution", "result_synthesis"}
NODE_ARCHETYPE_FAMILIES = {
    "parent": "parent_coordination_family",
    "lite": "lite_research_leaf_family",
    "standard": "standard_research_leaf_family",
    "execution": "execution_leaf_family",
}


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_node_tier_policy(root: Path) -> dict[str, Any]:
    path = root / NODE_TIER_POLICY_PATH
    payload = read_yaml(path)
    if not payload:
        raise RuntimeError(f"missing node tier policy: {path}")
    return payload


def load_local_skill_overrides(root: Path) -> dict[str, Any]:
    path = root / LOCAL_SKILL_OVERRIDES_PATH
    payload = read_yaml(path)
    if not payload:
        raise RuntimeError(f"missing local skill overrides: {path}")
    return payload


def node_config_for(path: str, overrides: dict[str, Any]) -> dict[str, Any]:
    nodes = overrides.get("nodes") or {}
    cfg = nodes.get(path)
    return cfg if isinstance(cfg, dict) else {}


def node_mode_for(path: str, overrides: dict[str, Any]) -> str:
    mode = str(node_config_for(path, overrides).get("node_mode", "")).strip()
    if mode not in VALID_NODE_MODES:
        raise RuntimeError(f"node `{path}` is missing a valid node_mode")
    return mode


def node_profile_for(path: str, overrides: dict[str, Any]) -> str | None:
    profile = str(node_config_for(path, overrides).get("node_profile", "")).strip()
    mode = node_mode_for(path, overrides)
    if not profile or profile in VALID_EXECUTION_PROFILES:
        return {
            "parent": "routing_parent",
            "lite": "lite_research_leaf",
            "standard": "evidence_leaf",
            "execution": "evidence_leaf",
        }[mode]
    if profile not in VALID_NODE_PROFILES:
        raise RuntimeError(f"node `{path}` declares an unknown node_profile `{profile}`")
    return profile


def execution_profile_for(path: str, overrides: dict[str, Any]) -> str | None:
    cfg = node_config_for(path, overrides)
    profile = str(cfg.get("execution_profile", "")).strip()
    if not profile:
        legacy = str(cfg.get("node_profile", "")).strip()
        profile = legacy if legacy in VALID_EXECUTION_PROFILES else ""
    if not profile:
        return None
    if profile not in VALID_EXECUTION_PROFILES:
        raise RuntimeError(f"node `{path}` declares an unknown execution_profile `{profile}`")
    return profile


def archetype_family_for_mode(mode: str) -> str:
    family = NODE_ARCHETYPE_FAMILIES.get(mode)
    if not family:
        raise RuntimeError(f"unknown node_mode for archetype family: {mode}")
    return family


def archetype_family_for(path: str, overrides: dict[str, Any]) -> str:
    return archetype_family_for_mode(node_mode_for(path, overrides))


def mode_policy_for(mode: str, policy: dict[str, Any]) -> dict[str, Any]:
    modes = policy.get("node_modes") or {}
    cfg = modes.get(mode)
    if not isinstance(cfg, dict):
        raise RuntimeError(f"node tier policy is missing node_modes.{mode}")
    return cfg


def required_files_for(mode: str, policy: dict[str, Any]) -> list[str]:
    cfg = mode_policy_for(mode, policy)
    return [str(item) for item in (cfg.get("required_files") or [])]


def optional_files_for(mode: str, policy: dict[str, Any]) -> list[str]:
    cfg = mode_policy_for(mode, policy)
    return [str(item) for item in (cfg.get("optional_files") or [])]


def forbidden_default_files_for(mode: str, policy: dict[str, Any]) -> list[str]:
    cfg = mode_policy_for(mode, policy)
    return [str(item) for item in (cfg.get("forbidden_default_files") or [])]


def binder_any_of_for(mode: str, policy: dict[str, Any]) -> list[str]:
    cfg = mode_policy_for(mode, policy)
    return [str(item) for item in (cfg.get("binder_any_of") or [])]


def requires_node_skill(mode: str) -> bool:
    return mode in {"standard", "execution"}


def requires_sop(mode: str, cfg: dict[str, Any] | None = None) -> bool:
    return mode == "execution"


def allows_wrapper(mode: str) -> bool:
    return mode in {"standard", "execution"}


def allows_execution(mode: str) -> bool:
    return mode == "execution"


def prompt_assets_for(mode: str, policy: dict[str, Any]) -> list[str]:
    required = required_files_for(mode, policy)
    optional = optional_files_for(mode, policy)
    return [path for path in required + optional if path.startswith("prompts/")]


def file_exists(root: Path, node_path: str, rel_path: str) -> bool:
    return (root / node_path / rel_path).is_file()


def declared_wrapper(node_path: str, overrides: dict[str, Any]) -> bool:
    return node_path in (overrides.get("wrappers") or {})


def declared_execution(node_path: str, overrides: dict[str, Any]) -> bool:
    return node_path in (overrides.get("executions") or {})


def binder_files_present(root: Path, node_path: str) -> list[str]:
    present: list[str] = []
    for rel_path in ("skills/local_wrapper.md", "skills/local_execution.md"):
        if file_exists(root, node_path, rel_path):
            present.append(rel_path)
    return present


def has_required_execution_binder(root: Path, node_path: str, mode: str, policy: dict[str, Any]) -> bool:
    binder_any_of = binder_any_of_for(mode, policy)
    if not binder_any_of:
        return True
    return any(file_exists(root, node_path, rel_path) for rel_path in binder_any_of)
