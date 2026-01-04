#!/usr/bin/env python3
"""
Autonomous CLI Agent
====================

A minimal harness demonstrating long-running autonomous coding with Claude CLI.
NO API KEY required - just login with: claude /connect

Example Usage:
    python main.py --project-dir ./my_project
    python main.py --project-dir ./my_project --max-iterations 5
"""

import argparse
import asyncio
from pathlib import Path

from agent import run_autonomous_agent
from client import check_claude_cli


# Configuration
DEFAULT_MODEL = "sonnet"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous CLI Agent - No API key required!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --project-dir ./my_project
  python main.py --project-dir ./my_project --model opus
  python main.py --project-dir ./my_project --max-iterations 5

Prerequisites:
  1. Install Claude CLI: npm install -g @anthropic-ai/claude-code
  2. Login: claude /connect (use Claude Pro/Max subscription)
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./autonomous_demo_project"),
        help="Directory for the project (default: generations/autonomous_demo_project)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use: sonnet, opus, haiku (default: {DEFAULT_MODEL})",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Check for Claude CLI
    if not check_claude_cli():
        print("Error: Claude CLI not found")
        print("\nInstall it with:")
        print("  npm install -g @anthropic-ai/claude-code")
        print("\nThen login with:")
        print("  claude /connect")
        return

    # Automatically place projects in generations/ directory unless already specified
    project_dir = args.project_dir
    if not str(project_dir).startswith("generations/"):
        if project_dir.is_absolute():
            pass
        else:
            project_dir = Path("generations") / project_dir

    # Run the agent
    try:
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                model=args.model,
                max_iterations=args.max_iterations,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("To resume, run the same command again")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
