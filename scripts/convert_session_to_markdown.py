#!/usr/bin/env python3
"""
Convert Claude Code (CC) session JSONL files to readable Markdown.

This script provides deterministic conversion of CC session transcripts
from JSONL format to human-readable Markdown, suitable for documentation,
review, and archiving.

Usage:
    python scripts/convert_session_to_markdown.py session.jsonl > session.md
    python scripts/convert_session_to_markdown.py session.jsonl --include-thinking
    python scripts/convert_session_to_markdown.py session.jsonl --include-tool-output
    python scripts/convert_session_to_markdown.py session.jsonl --truncate 500

Features:
    - Session metadata header
    - Turn-by-turn conversation display
    - Collapsible thinking blocks (optional)
    - Tool call formatting with truncation options
    - Syntax highlighting for code blocks

Created: 2026-01-08
"""

import argparse
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_TRUNCATE_LENGTH = 2000  # Characters for tool output truncation
THINKING_COLLAPSE_THRESHOLD = 500  # Collapse thinking blocks longer than this


# =============================================================================
# Text Processing Utilities
# =============================================================================

def truncate_text(text: str, max_length: int, suffix: str = "\n\n[... truncated ...]") -> str:
    """Truncate text to max_length characters, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def escape_markdown(text: str) -> str:
    """Escape special Markdown characters in text."""
    # Only escape characters that would break formatting
    # Don't escape inside code blocks (handled separately)
    return text


def format_timestamp(ts: str | None) -> str:
    """Format an ISO timestamp to a human-readable string."""
    if not ts:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        return ts


def format_duration(minutes: int) -> str:
    """Format duration in minutes to a readable string."""
    if minutes < 60:
        return f"{minutes} minutes"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return f"{hours}h {mins}m"


# =============================================================================
# Session Statistics
# =============================================================================

def extract_session_info(entries: list[dict]) -> dict[str, Any]:
    """
    Extract session metadata and statistics from entries.

    Returns:
        Dictionary with session information
    """
    info = {
        "timestamps": [],
        "human_messages": 0,
        "assistant_messages": 0,
        "thinking_blocks": 0,
        "tool_calls": {"total": 0, "by_type": {}},
        "model": None,
        "tokens": {"input": 0, "output": 0}
    }

    for entry in entries:
        # Collect timestamps
        ts = entry.get("timestamp")
        if ts:
            info["timestamps"].append(ts)

        # Count messages
        message = entry.get("message", {})
        role = message.get("role", entry.get("type", ""))

        if role == "user":
            info["human_messages"] += 1
        elif role == "assistant":
            info["assistant_messages"] += 1
            content = message.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "thinking":
                            info["thinking_blocks"] += 1
                        elif block.get("type") == "tool_use":
                            tool_name = block.get("name", "unknown")
                            info["tool_calls"]["total"] += 1
                            info["tool_calls"]["by_type"][tool_name] = \
                                info["tool_calls"]["by_type"].get(tool_name, 0) + 1

            # Extract model
            if not info["model"]:
                model = message.get("model")
                if model:
                    info["model"] = model

        # Token usage
        usage = entry.get("usage", {})
        if usage:
            info["tokens"]["input"] += usage.get("input_tokens", 0)
            info["tokens"]["output"] += usage.get("output_tokens", 0)

    # Compute derived values
    if info["timestamps"]:
        info["started_at"] = min(info["timestamps"])
        info["ended_at"] = max(info["timestamps"])
        try:
            start = datetime.fromisoformat(info["started_at"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(info["ended_at"].replace("Z", "+00:00"))
            info["duration_minutes"] = int((end - start).total_seconds() / 60)
        except (ValueError, TypeError):
            info["duration_minutes"] = 0
    else:
        info["started_at"] = None
        info["ended_at"] = None
        info["duration_minutes"] = 0

    info["turns"] = info["human_messages"]

    return info


# =============================================================================
# Markdown Formatters
# =============================================================================

def format_header(info: dict[str, Any], source_path: Path) -> str:
    """Generate the Markdown header with session metadata."""
    lines = [
        "# CC Session Transcript",
        "",
        "## Session Information",
        "",
        f"- **Source**: `{source_path.name}`",
        f"- **Started**: {format_timestamp(info.get('started_at'))}",
        f"- **Ended**: {format_timestamp(info.get('ended_at'))}",
        f"- **Duration**: {format_duration(info.get('duration_minutes', 0))}",
        f"- **Model**: {info.get('model', 'Unknown')}",
        "",
        "## Statistics",
        "",
        f"- **Turns**: {info.get('turns', 0)}",
        f"- **Human messages**: {info.get('human_messages', 0)}",
        f"- **Assistant messages**: {info.get('assistant_messages', 0)}",
        f"- **Thinking blocks**: {info.get('thinking_blocks', 0)}",
        f"- **Tool calls**: {info.get('tool_calls', {}).get('total', 0)}",
    ]

    # Add tool breakdown if any
    tool_types = info.get("tool_calls", {}).get("by_type", {})
    if tool_types:
        lines.append("")
        lines.append("### Tool Usage")
        lines.append("")
        for tool, count in sorted(tool_types.items(), key=lambda x: -x[1]):
            lines.append(f"- {tool}: {count}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Conversation")
    lines.append("")

    return "\n".join(lines)


def format_thinking_block(
    thinking: str,
    include_thinking: bool,
    collapse_long: bool = True
) -> str:
    """Format a thinking block, optionally collapsed."""
    if not include_thinking:
        return "*[Thinking block omitted]*\n"

    if collapse_long and len(thinking) > THINKING_COLLAPSE_THRESHOLD:
        return f"""<details>
<summary>🧠 Thinking ({len(thinking)} characters)</summary>

{thinking}

</details>
"""
    else:
        return f"""<details>
<summary>🧠 Thinking</summary>

{thinking}

</details>
"""


def format_tool_use(
    tool_name: str,
    tool_input: dict[str, Any],
    truncate_length: int
) -> str:
    """Format a tool use block."""
    input_str = json.dumps(tool_input, indent=2)

    if len(input_str) > truncate_length:
        input_str = truncate_text(input_str, truncate_length)

    return f"""**🔧 Tool: {tool_name}**

```json
{input_str}
```
"""


def format_tool_result(
    tool_name: str,
    result: str | list | dict,
    include_output: bool,
    truncate_length: int
) -> str:
    """Format a tool result block."""
    if not include_output:
        # Just indicate there was output
        if isinstance(result, str):
            lines = result.count('\n') + 1
            chars = len(result)
            return f"*[Tool output: {lines} lines, {chars} characters]*\n"
        else:
            return "*[Tool output omitted]*\n"

    # Format the result
    if isinstance(result, dict) or isinstance(result, list):
        result_str = json.dumps(result, indent=2)
    else:
        result_str = str(result)

    if len(result_str) > truncate_length:
        result_str = truncate_text(result_str, truncate_length)

    return f"""<details>
<summary>📤 Tool Result ({len(result_str)} chars)</summary>

```text
{result_str}
```

</details>
"""


def format_text_block(text: str) -> str:
    """Format a text block from the assistant."""
    # Don't modify the text, just return it
    # Markdown formatting is preserved
    return text + "\n"


def format_user_message(content: str | list) -> str:
    """Format a user message."""
    lines = ["### 👤 User", ""]

    if isinstance(content, str):
        lines.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    lines.append(block.get("text", ""))
                elif block.get("type") == "tool_result":
                    # Tool results in user messages are responses to tool calls
                    tool_id = block.get("tool_use_id", "unknown")
                    result = block.get("content", "")
                    if isinstance(result, list):
                        # Handle nested content (e.g., image blocks)
                        for item in result:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    lines.append(item.get("text", ""))
                                elif item.get("type") == "image":
                                    lines.append("*[Image content]*")
                    else:
                        lines.append(f"*[Tool result for {tool_id[:8]}...]*")
            elif isinstance(block, str):
                lines.append(block)

    lines.append("")
    return "\n".join(lines)


def format_assistant_message(
    content: str | list,
    include_thinking: bool,
    include_tool_output: bool,
    truncate_length: int
) -> str:
    """Format an assistant message."""
    lines = ["### 🤖 Assistant", ""]

    if isinstance(content, str):
        lines.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                block_type = block.get("type")

                if block_type == "text":
                    text = block.get("text", "")
                    lines.append(format_text_block(text))

                elif block_type == "thinking":
                    thinking = block.get("thinking", "")
                    lines.append(format_thinking_block(thinking, include_thinking))

                elif block_type == "tool_use":
                    tool_name = block.get("name", "unknown")
                    tool_input = block.get("input", {})
                    lines.append(format_tool_use(tool_name, tool_input, truncate_length))

            elif isinstance(block, str):
                lines.append(block)

    lines.append("")
    return "\n".join(lines)


# =============================================================================
# Main Conversion
# =============================================================================

def convert_session(
    session_path: Path,
    output: TextIO,
    include_thinking: bool = False,
    include_tool_output: bool = False,
    truncate_length: int = DEFAULT_TRUNCATE_LENGTH
) -> None:
    """
    Convert a session JSONL file to Markdown.

    Args:
        session_path: Path to the JSONL file
        output: Output file object (e.g., sys.stdout)
        include_thinking: Whether to include thinking blocks
        include_tool_output: Whether to include full tool output
        truncate_length: Maximum length for tool output truncation
    """
    # Load entries
    entries = []
    opener = gzip.open if session_path.suffix == ".gz" else open

    with opener(session_path, "rt", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        output.write("# Empty Session\n\nNo entries found in session file.\n")
        return

    # Extract session info
    info = extract_session_info(entries)

    # Write header
    output.write(format_header(info, session_path))

    # Process entries
    turn_number = 0
    for entry in entries:
        # Skip non-message entries
        if entry.get("type") == "file-history-snapshot":
            continue

        message = entry.get("message", {})
        role = message.get("role", entry.get("type", ""))
        content = message.get("content", "")

        if role == "user":
            turn_number += 1
            output.write(f"---\n\n## Turn {turn_number}\n\n")
            output.write(format_user_message(content))

        elif role == "assistant":
            output.write(format_assistant_message(
                content,
                include_thinking,
                include_tool_output,
                truncate_length
            ))

    # Footer
    output.write("\n---\n\n")
    output.write(f"*Generated from `{session_path.name}` on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert CC session JSONL files to readable Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s session.jsonl > session.md
    %(prog)s session.jsonl --include-thinking
    %(prog)s session.jsonl --include-tool-output --truncate 1000
    %(prog)s session.jsonl.gz -o output.md
        """
    )

    parser.add_argument(
        "session_file",
        type=Path,
        help="Path to the session JSONL file (supports .gz)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--include-thinking", "-t",
        action="store_true",
        help="Include thinking blocks (collapsed by default)"
    )
    parser.add_argument(
        "--include-tool-output", "-u",
        action="store_true",
        help="Include full tool output (collapsed)"
    )
    parser.add_argument(
        "--truncate", "-T",
        type=int,
        default=DEFAULT_TRUNCATE_LENGTH,
        help=f"Truncate tool output after N characters (default: {DEFAULT_TRUNCATE_LENGTH})"
    )
    parser.add_argument(
        "--no-collapse",
        action="store_true",
        help="Don't use collapsible sections for thinking blocks"
    )

    args = parser.parse_args()

    # Validate input
    if not args.session_file.exists():
        print(f"Error: File not found: {args.session_file}", file=sys.stderr)
        sys.exit(1)

    # Open output
    if args.output:
        output = open(args.output, "w", encoding="utf-8")
    else:
        output = sys.stdout

    try:
        convert_session(
            args.session_file,
            output,
            include_thinking=args.include_thinking,
            include_tool_output=args.include_tool_output,
            truncate_length=args.truncate
        )
    finally:
        if args.output:
            output.close()


if __name__ == "__main__":
    main()
