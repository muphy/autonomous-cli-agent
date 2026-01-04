"""
Claude CLI Client
=================

Functions for running Claude Code via CLI subprocess instead of SDK.
This allows using Claude Pro/Max subscription without API key.
"""

import asyncio
import json
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional


# Built-in tools to allow
BUILTIN_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
    "WebSearch",
    "WebFetch",
]

# Puppeteer MCP tools for browser automation
PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_fill",
    "mcp__puppeteer__puppeteer_select",
    "mcp__puppeteer__puppeteer_hover",
    "mcp__puppeteer__puppeteer_evaluate",
]


def check_claude_cli() -> bool:
    """Check if claude CLI is available."""
    return shutil.which("claude") is not None


async def run_claude_cli(
    prompt: str,
    project_dir: Path,
    model: str = "sonnet",
    allowed_tools: Optional[list[str]] = None,
    system_prompt: Optional[str] = None,
    max_turns: int = 1000,
    resume_session: Optional[str] = None,
) -> AsyncGenerator[dict, None]:
    """
    Run Claude CLI as subprocess and stream JSON output.

    Args:
        prompt: The prompt to send to Claude
        project_dir: Working directory for the session
        model: Claude model to use (sonnet, opus, haiku)
        allowed_tools: List of tools to allow
        system_prompt: Optional system prompt
        max_turns: Maximum conversation turns
        resume_session: Optional session ID to resume

    Yields:
        Parsed JSON messages from Claude CLI stream
    """
    if allowed_tools is None:
        allowed_tools = BUILTIN_TOOLS.copy()

    # Build command
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",  # Required for stream-json with --print
        "--allowed-tools", ",".join(allowed_tools),
        "--permission-mode", "bypassPermissions",
        "--model", model,
    ]

    # Add system prompt if provided
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    # Resume session if specified
    if resume_session:
        cmd.extend(["--resume", resume_session])

    # Create subprocess with larger buffer
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(project_dir.resolve()),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=1024 * 1024,  # 1MB buffer limit
    )

    session_id = None

    # Stream stdout line by line with readline
    while True:
        try:
            line = await process.stdout.readline()
            if not line:
                break

            line_str = line.decode().strip()
            if not line_str:
                continue

            try:
                data = json.loads(line_str)

                # Capture session ID from init message
                if data.get("type") == "system" and data.get("subtype") == "init":
                    session_id = data.get("session_id")

                yield data
            except json.JSONDecodeError:
                # Non-JSON output, skip
                continue
        except Exception as e:
            # Handle any readline errors gracefully
            yield {
                "type": "error",
                "error": f"Stream read error: {str(e)}"
            }
            break

    # Wait for process to complete
    await process.wait()

    # Check for errors
    if process.returncode != 0:
        stderr = await process.stderr.read()
        if stderr:
            yield {
                "type": "error",
                "error": stderr.decode().strip(),
                "returncode": process.returncode
            }


class ClaudeCLIClient:
    """
    Claude CLI client that mimics SDK interface.

    Usage:
        client = ClaudeCLIClient(project_dir, model="sonnet")
        async with client:
            await client.query("Fix the bug")
            async for msg in client.receive_response():
                print(msg)
    """

    def __init__(
        self,
        project_dir: Path,
        model: str = "sonnet",
        system_prompt: Optional[str] = None,
        allowed_tools: Optional[list[str]] = None,
    ):
        self.project_dir = project_dir
        self.model = model
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools or BUILTIN_TOOLS.copy()
        self.session_id: Optional[str] = None
        self._current_prompt: Optional[str] = None
        self._response_generator = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def query(self, prompt: str) -> None:
        """Send a query to Claude (prepares the generator)."""
        self._current_prompt = prompt

    async def receive_response(self) -> AsyncGenerator[dict, None]:
        """Receive streaming response from Claude CLI."""
        if self._current_prompt is None:
            return

        async for msg in run_claude_cli(
            prompt=self._current_prompt,
            project_dir=self.project_dir,
            model=self.model,
            allowed_tools=self.allowed_tools,
            system_prompt=self.system_prompt,
            resume_session=self.session_id,
        ):
            # Capture session ID
            if msg.get("type") == "system" and msg.get("subtype") == "init":
                self.session_id = msg.get("session_id")

            yield msg

        self._current_prompt = None


def create_cli_client(project_dir: Path, model: str) -> ClaudeCLIClient:
    """
    Create a Claude CLI client.

    Args:
        project_dir: Directory for the project
        model: Claude model to use

    Returns:
        Configured ClaudeCLIClient
    """
    if not check_claude_cli():
        raise RuntimeError(
            "Claude CLI not found.\n"
            "Install it with: npm install -g @anthropic-ai/claude-code\n"
            "Then login with: claude /connect"
        )

    # Ensure project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)

    print(f"Using Claude CLI client")
    print(f"   - Model: {model}")
    print(f"   - Working directory: {project_dir.resolve()}")
    print(f"   - Tools: {', '.join(BUILTIN_TOOLS)}")
    print()

    return ClaudeCLIClient(
        project_dir=project_dir,
        model=model,
        system_prompt="You are an expert full-stack developer building a production-quality web application.",
        allowed_tools=BUILTIN_TOOLS,
    )
