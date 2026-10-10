"""Prompt template loading helpers."""

from pathlib import Path
from string import Template
from typing import Any


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt_template(template_name: str) -> str:
    """Load a prompt template from the project prompts directory."""
    template_path = PROMPT_DIR / template_name
    return template_path.read_text(encoding="utf-8")


def render_prompt(template_name: str, **context: Any) -> str:
    """Render a prompt template with shared rules and stringified context."""
    values = {
        key: "" if value is None else str(value)
        for key, value in context.items()
    }
    values.setdefault("shared_rules", load_prompt_template("shared_rules.md"))
    template = Template(load_prompt_template(template_name))
    return template.safe_substitute(values)
