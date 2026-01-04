#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo (CLI Version)
===========================================

A minimal harness demonstrating long-running autonomous coding with Claude.
This version uses Claude CLI subprocess instead of SDK, so NO API KEY is required.
Just login with: claude /connect

Example Usage:
    python autonomous_agent_cli_demo.py --project-dir ./claude_clone_demo
    python autonomous_agent_cli_demo.py --project-dir ./claude_clone_demo --max-iterations 5
"""

import argparse
import asyncio
from pathlib import Path

from agent_cli import run_autonomous_agent
from client_cli import check_claude_cli


# Configuration
DEFAULT_MODEL = "sonnet"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent Demo (CLI Mode) - No API key required!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start fresh project
  python autonomous_agent_cli_demo.py --project-dir ./claude_clone

  # Use a specific model
  python autonomous_agent_cli_demo.py --project-dir ./claude_clone --model opus

  # Limit iterations for testing
  python autonomous_agent_cli_demo.py --project-dir ./claude_clone --max-iterations 5

  # Continue existing project
  python autonomous_agent_cli_demo.py --project-dir ./claude_clone

Prerequisites:
  1. Install Claude CLI: npm install -g @anthropic-ai/claude-code
  2. Login: claude /connect (use Claude Pro/Max subscription)

No ANTHROPIC_API_KEY required!
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
