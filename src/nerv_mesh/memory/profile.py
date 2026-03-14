"""Profile loader — reads NERV.md, SOUL.md, USER.md into the system prompt.

File layout in ~/.nerv-mesh/:
  NERV.md           → Global instructions (like CLAUDE.md)
  memory/SOUL.md    → Agent identity and principles
  memory/USER.md    → User profile (updated over time)
"""

from pathlib import Path

from nerv_mesh.config.paths import home_dir

_LANGUAGE_MAP = {
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
}


def load_profile(language: str = "zh-CN") -> str:
    """Assemble the identity prompt from NERV.md + SOUL.md + USER.md."""
    h = home_dir()
    sections: list[str] = []

    lang_name = _LANGUAGE_MAP.get(language, language)
    sections.append(f"Always respond in {lang_name}.")

    nerv = _read_md(h / "NERV.md")
    if nerv:
        sections.append(nerv)

    soul = _read_md(h / "memory" / "SOUL.md")
    if soul:
        sections.append(soul)

    user = _read_md(h / "memory" / "USER.md")
    if user:
        sections.append(user)

    return "\n\n".join(sections)


def _read_md(path: Path) -> str:
    """Read a markdown file, return empty string if missing."""
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""
