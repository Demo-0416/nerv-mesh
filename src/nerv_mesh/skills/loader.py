"""Skill discovery and loading from SKILL.md files."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Skill:
    """A parsed skill definition."""

    name: str
    description: str
    instructions: str
    path: Path
    version: str = "0.1.0"
    tags: list[str] = field(default_factory=list)


class SkillLoader:
    """Discover and load skills from configured directories.

    Each skill is a directory containing a SKILL.md with YAML frontmatter:

        ---
        name: research
        description: Deep research on a topic
        version: 0.1.0
        tags: [research, web]
        ---

        ## Instructions
        ...
    """

    def __init__(self, dirs: list[str] | None = None):
        from nerv_mesh.config.paths import builtin_skills_dir, home_dir

        self._dirs: list[Path] = [builtin_skills_dir()]
        self._dirs.append(home_dir() / "skills" / "custom")
        if dirs:
            self._dirs.extend(Path(d) for d in dirs)
        self._skills: dict[str, Skill] = {}
        self._discover()

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def list_skills(self) -> list[dict]:
        """Return skill summaries (name + description) for API / prompt injection."""
        return [
            {"name": s.name, "description": s.description, "version": s.version}
            for s in self._skills.values()
        ]

    def prompt_fragment(self) -> str:
        """Generate a prompt block listing available skills."""
        if not self._skills:
            return ""
        lines = ["## Available Skills"]
        for s in self._skills.values():
            lines.append(f"- **{s.name}**: {s.description}")
        return "\n".join(lines)

    def load_instructions(self, name: str) -> str | None:
        """Lazy-load the full instruction text for a skill."""
        skill = self._skills.get(name)
        return skill.instructions if skill else None

    # ── Private ───────────────────────────────────────────────────────────

    def _discover(self) -> None:
        for d in self._dirs:
            if not d.exists():
                continue
            for skill_dir in sorted(d.iterdir()):
                skill_file = skill_dir / "SKILL.md"
                if skill_file.is_file():
                    skill = _parse_skill_file(skill_file)
                    if skill:
                        self._skills[skill.name] = skill


def _parse_skill_file(path: Path) -> Skill | None:
    """Parse a SKILL.md with YAML frontmatter + markdown body."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return None

    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()

    name = meta.get("name")
    description = meta.get("description", "")
    if not name:
        return None

    return Skill(
        name=name,
        description=description,
        instructions=body,
        path=path,
        version=meta.get("version", "0.1.0"),
        tags=meta.get("tags", []),
    )
