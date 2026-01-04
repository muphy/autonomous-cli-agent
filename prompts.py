"""
Prompt Loading Utilities
========================

Functions for loading prompt templates from the prompts directory.
"""

import shutil
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text()


def get_initializer_prompt() -> str:
    """Load the initializer prompt."""
    return load_prompt("initializer_prompt")


def get_coding_prompt() -> str:
    """Load the coding agent prompt."""
    return load_prompt("coding_prompt")


def copy_spec_to_project(project_dir: Path) -> None:
    """Copy the app spec files into the project directory for the agent to read."""
    # Copy app_spec.txt (required)
    spec_source = PROMPTS_DIR / "app_spec.txt"
    spec_dest = project_dir / "app_spec.txt"
    if spec_source.exists() and not spec_dest.exists():
        shutil.copy(spec_source, spec_dest)
        print("Copied app_spec.txt to project directory")

    # Copy app_details.md (optional)
    details_source = PROMPTS_DIR / "app_details.md"
    details_dest = project_dir / "app_details.md"
    if details_source.exists() and not details_dest.exists():
        shutil.copy(details_source, details_dest)
        print("Copied app_details.md to project directory")
