"""Centralized path resolution — all runtime data lives in ~/.nerv-mesh/."""

import os
from pathlib import Path

_DEFAULT_HOME = Path.home() / ".nerv-mesh"


def home_dir() -> Path:
    """Return the nerv-mesh home directory (default: ~/.nerv-mesh/)."""
    env = os.getenv("NERV_MESH_HOME")
    return Path(env) if env else _DEFAULT_HOME


def ensure_home() -> Path:
    """Create the home directory structure if it doesn't exist."""
    h = home_dir()
    for sub in ["skills/custom", "threads", "memory"]:
        (h / sub).mkdir(parents=True, exist_ok=True)
    return h


def builtin_skills_dir() -> Path:
    """Return the package-internal builtin skills directory."""
    return Path(__file__).parent.parent / "_builtin_skills"
