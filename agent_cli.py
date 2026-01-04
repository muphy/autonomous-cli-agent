"""
Agent Session Logic (CLI Version)
==================================

Core agent interaction functions for running autonomous coding sessions
using Claude CLI subprocess instead of SDK.
"""

import asyncio
from pathlib import Path
from typing import Optional

from client_cli import ClaudeCLIClient, create_cli_client
from progress import print_session_header, print_progress_summary
from prompts import get_initializer_prompt, get_coding_prompt, copy_spec_to_project


# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_agent_session(
    client: ClaudeCLIClient,
    message: str,
    project_dir: Path,
) -> tuple[str, str]:
    """
    Run a single agent session using Claude CLI.

    Args:
        client: Claude CLI client
        message: The prompt to send
        project_dir: Project directory path

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
    """
    print("Sending prompt to Claude CLI...\n")

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            msg_type = msg.get("type", "")

            # Handle assistant messages
            if msg_type == "assistant":
                content = msg.get("message", {}).get("content", [])
                for block in content:
                    block_type = block.get("type", "")

                    if block_type == "text":
                        text = block.get("text", "")
                        response_text += text
                        print(text, end="", flush=True)
                    elif block_type == "tool_use":
                        tool_name = block.get("name", "unknown")
                        print(f"\n[Tool: {tool_name}]", flush=True)
                        tool_input = block.get("input", {})
                        input_str = str(tool_input)
                        if len(input_str) > 200:
                            print(f"   Input: {input_str[:200]}...", flush=True)
                        else:
                            print(f"   Input: {input_str}", flush=True)

            # Handle tool results
            elif msg_type == "user":
                content = msg.get("message", {}).get("content", [])
                for block in content:
                    block_type = block.get("type", "")

                    if block_type == "tool_result":
                        is_error = block.get("is_error", False)
                        result_content = block.get("content", "")

                        # Check if command was blocked
                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            print("   [Done]", flush=True)

            # Handle result messages (final output)
            elif msg_type == "result":
                result_text = msg.get("result", "")
                if result_text and result_text not in response_text:
                    response_text += result_text
                    print(result_text, end="", flush=True)

            # Handle errors
            elif msg_type == "error":
                error_msg = msg.get("error", "Unknown error")
                print(f"\n[Error] {error_msg}", flush=True)
                return "error", error_msg

            # Handle system messages (session init, etc.)
            elif msg_type == "system":
                subtype = msg.get("subtype", "")
                if subtype == "init":
                    session_id = msg.get("session_id", "")
                    print(f"[Session: {session_id[:8]}...]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Run the autonomous agent loop using Claude CLI.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT DEMO (CLI Mode)")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print(f"Model: {model}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    print()
    print("NOTE: Using Claude CLI - no API key required!")
    print("      Make sure you're logged in with: claude /connect")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    if is_first_run:
        print("Fresh start - will use initializer agent")
        print()
        print("=" * 70)
        print("  NOTE: First session takes 10-20+ minutes!")
        print("  The agent is generating 200 detailed test cases.")
        print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
        print("=" * 70)
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir)
    else:
        print("Continuing existing project")
        print_progress_summary(project_dir)

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Print session header
        print_session_header(iteration, is_first_run)

        # Create client (fresh context)
        client = create_cli_client(project_dir, model)

        # Choose prompt based on session type
        if is_first_run:
            prompt = get_initializer_prompt()
            is_first_run = False  # Only use initializer once
        else:
            prompt = get_coding_prompt()

        # Run session with async context manager
        async with client:
            status, response = await run_agent_session(client, prompt, project_dir)

        # Handle status
        if status == "continue":
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            print("\nSession encountered an error")
            print("Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")
