"""Multi-file config loading from ~/.nerv-mesh/.

All runtime config lives in a single global directory (default: ~/.nerv-mesh/).
On first run, default config files are created automatically.

Files:
  config.yaml    → Infra (sandbox, gateway)
  models.yaml    → LLM providers
  mcp.json       → MCP server definitions
  settings.json  → User preferences
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any

import yaml

from .models import AppConfig
from .paths import ensure_home

_DEFAULTS_DIR = Path(__file__).parent.parent / "_defaults"


def load_config(config_dir: Path | None = None) -> AppConfig:
    """Load and assemble config from ~/.nerv-mesh/ (or explicit dir for tests)."""
    root = config_dir if config_dir and config_dir.is_dir() else ensure_home()
    _ensure_defaults(root)

    merged: dict[str, Any] = {}

    infra = _load_yaml(root / "config.yaml")
    if infra:
        merged.update(infra)

    models_data = _load_yaml(root / "models.yaml")
    if models_data:
        merged["models"] = models_data

    if "models" not in merged:
        if infra and "models" in infra:
            merged["models"] = infra["models"]
        else:
            raise FileNotFoundError(f"No models.yaml found in {root}.")

    mcp_data = _load_json(root / "mcp.json")
    if mcp_data:
        merged["mcp"] = mcp_data

    settings_data = _load_json(root / "settings.json")
    if settings_data:
        merged["settings"] = settings_data

    resolved = _resolve_env_vars(merged)
    return AppConfig.model_validate(resolved)


def _ensure_defaults(root: Path) -> None:
    """Copy default config files on first run (won't overwrite existing)."""
    if not _DEFAULTS_DIR.exists():
        return
    for src in _DEFAULTS_DIR.iterdir():
        dst = root / src.name
        if not dst.exists():
            shutil.copy2(src, dst)


def _load_yaml(path: Path) -> dict | None:
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")) or {}


def _resolve_env_vars(obj: Any) -> Any:
    """Recursively replace $VAR references with environment values."""
    if isinstance(obj, str) and obj.startswith("$"):
        return os.getenv(obj[1:], "")
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    return obj
