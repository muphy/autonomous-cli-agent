"""
Progress Tracking Utilities
===========================

Functions for tracking and displaying progress of the autonomous coding agent.
"""

import json
from pathlib import Path


def count_passing_tests(project_dir: Path) -> tuple[int, int]:
    """
    Count passing and total tests in feature_list.json.

    Args:
        project_dir: Directory containing feature_list.json

    Returns:
        (passing_count, total_count)
    """
    tests_file = project_dir / "feature_list.json"

    if not tests_file.exists():
        return 0, 0

    try:
        with open(tests_file, "r") as f:
            tests = json.load(f)

        total = len(tests)
        passing = sum(1 for test in tests if test.get("passes", False))

        return passing, total
    except (json.JSONDecodeError, IOError):
        return 0, 0


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """Print a formatted header for the session."""
    session_type = "INITIALIZER" if is_initializer else "CODING AGENT"

    print("\n" + "=" * 70)
    print(f"  SESSION {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_progress_summary(project_dir: Path) -> None:
    """Print a summary of current progress."""
    passing, total = count_passing_tests(project_dir)

    if total > 0:
        percentage = (passing / total) * 100
        print(f"\nProgress: {passing}/{total} tests passing ({percentage:.1f}%)")
    else:
        print("\nProgress: feature_list.json not yet created")


def update_progress_file(
    project_dir: Path,
    session_num: int,
    is_initializer: bool,
) -> None:
    """
    Automatically update claude-progress.txt after each session.

    This is called deterministically after each session ends,
    ensuring progress is always tracked regardless of what the agent did.

    Args:
        project_dir: Project directory
        session_num: Current session number
        is_initializer: Whether this was an initializer session
    """
    from datetime import datetime

    progress_file = project_dir / "claude-progress.txt"
    passing, total = count_passing_tests(project_dir)

    # Build session entry
    session_type = "Initializer" if is_initializer else "Coding Agent"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    if total > 0:
        percentage = (passing / total) * 100
        progress_str = f"{passing}/{total} tests passing ({percentage:.1f}%)"
    else:
        progress_str = "feature_list.json not yet created"

    entry = f"""
=== Session {session_num}: {session_type} ===
Date: {date_str}

Progress: {progress_str}

---
"""

    # Append to file
    try:
        if progress_file.exists():
            existing = progress_file.read_text()
        else:
            existing = "# Claude Progress Log\n\nAutomatically generated after each session.\n"

        progress_file.write_text(existing + entry)
        print(f"\n[Auto] Updated claude-progress.txt")
    except IOError as e:
        print(f"\n[Warning] Could not update claude-progress.txt: {e}")
