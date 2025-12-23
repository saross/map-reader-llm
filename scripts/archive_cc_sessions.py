#!/usr/bin/env python3
"""
Archive Claude Code conversation sessions for the map-reader-llm project.

This script copies Claude Code session files from ~/.claude/projects/ to
the project archive, with optional conversion to human-readable markdown.

Usage:
    python scripts/archive_cc_sessions.py [--markdown] [--dry-run]

Options:
    --markdown  Also generate human-readable markdown versions
    --dry-run   Show what would be done without copying files

Created: 2025-12-23
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


# Configuration
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
PROJECT_PATH_ENCODED = "-home-shawn-Code-map-reader-llm"
ARCHIVE_DIR = Path(__file__).parent.parent / "archive" / "cc-sessions"


def get_session_files() -> list[Path]:
    """
    Find all session files for this project.

    Returns:
        List of Path objects for session JSONL files
    """
    project_dir = CLAUDE_PROJECTS_DIR / PROJECT_PATH_ENCODED
    if not project_dir.exists():
        print(f"Warning: Project directory not found: {project_dir}")
        return []

    session_files = list(project_dir.glob("*.jsonl"))
    return sorted(session_files, key=lambda p: p.stat().st_mtime)


def get_session_metadata(session_path: Path) -> dict:
    """
    Extract metadata from a session file.

    Args:
        session_path: Path to session JSONL file

    Returns:
        Dictionary with session metadata
    """
    metadata = {
        "filename": session_path.name,
        "size_bytes": session_path.stat().st_size,
        "modified": datetime.fromtimestamp(session_path.stat().st_mtime).isoformat(),
        "message_count": 0,
        "start_timestamp": None,
        "end_timestamp": None,
        "is_agent": session_path.name.startswith("agent-"),
    }

    timestamps = []
    with open(session_path, 'r') as f:
        for line in f:
            metadata["message_count"] += 1
            try:
                data = json.loads(line)
                if "timestamp" in data:
                    timestamps.append(data["timestamp"])
                elif "snapshot" in data and "timestamp" in data["snapshot"]:
                    timestamps.append(data["snapshot"]["timestamp"])
            except json.JSONDecodeError:
                continue

    if timestamps:
        metadata["start_timestamp"] = min(timestamps)
        metadata["end_timestamp"] = max(timestamps)

    return metadata


def convert_to_markdown(session_path: Path, output_path: Path) -> None:
    """
    Convert a session JSONL to human-readable markdown.

    Args:
        session_path: Path to session JSONL file
        output_path: Path for output markdown file
    """
    messages = []

    with open(session_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)

                # Skip non-message entries
                if data.get("type") == "file-history-snapshot":
                    continue

                msg = data.get("message", {})
                role = msg.get("role", data.get("type", "unknown"))
                content = msg.get("content", "")
                timestamp = data.get("timestamp", "")

                # Handle assistant messages with thinking blocks
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict):
                            if block.get("type") == "text":
                                text_parts.append(block.get("text", ""))
                            elif block.get("type") == "thinking":
                                # Optionally include thinking (commented out for brevity)
                                pass
                            elif block.get("type") == "tool_use":
                                tool_name = block.get("name", "unknown")
                                text_parts.append(f"[Tool: {tool_name}]")
                    content = "\n".join(text_parts)

                if content and role in ("user", "assistant"):
                    messages.append({
                        "role": role,
                        "content": content[:10000],  # Truncate very long messages
                        "timestamp": timestamp,
                    })

            except json.JSONDecodeError:
                continue

    # Write markdown
    with open(output_path, 'w') as f:
        f.write(f"# Claude Code Session: {session_path.stem}\n\n")
        f.write(f"**Exported**: {datetime.now().isoformat()}\n")
        f.write(f"**Messages**: {len(messages)}\n\n")
        f.write("---\n\n")

        for msg in messages:
            role_label = "**User**" if msg["role"] == "user" else "**Claude**"
            ts = msg["timestamp"][:19] if msg["timestamp"] else ""
            f.write(f"### {role_label} ({ts})\n\n")
            f.write(msg["content"])
            f.write("\n\n---\n\n")

    print(f"  Created: {output_path}")


def archive_sessions(markdown: bool = False, dry_run: bool = False) -> None:
    """
    Archive all session files for this project.

    Args:
        markdown: Whether to also generate markdown versions
        dry_run: If True, only print what would be done
    """
    session_files = get_session_files()

    if not session_files:
        print("No session files found.")
        return

    print(f"Found {len(session_files)} session file(s)")
    print()

    # Create archive directory
    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Create manifest
    manifest = {
        "archived": datetime.now().isoformat(),
        "source": str(CLAUDE_PROJECTS_DIR / PROJECT_PATH_ENCODED),
        "sessions": [],
    }

    for session_path in session_files:
        metadata = get_session_metadata(session_path)
        manifest["sessions"].append(metadata)

        size_mb = metadata["size_bytes"] / (1024 * 1024)
        session_type = "agent" if metadata["is_agent"] else "main"

        print(f"Session: {session_path.name}")
        print(f"  Type: {session_type}")
        print(f"  Size: {size_mb:.2f} MB ({metadata['message_count']} messages)")
        print(f"  Period: {metadata['start_timestamp']} to {metadata['end_timestamp']}")

        if dry_run:
            print(f"  Would copy to: {ARCHIVE_DIR / session_path.name}")
        else:
            # Copy JSONL
            dest = ARCHIVE_DIR / session_path.name
            shutil.copy2(session_path, dest)
            print(f"  Copied to: {dest}")

            # Convert to markdown if requested
            if markdown:
                md_path = ARCHIVE_DIR / f"{session_path.stem}.md"
                convert_to_markdown(session_path, md_path)

        print()

    # Write manifest
    if not dry_run:
        manifest_path = ARCHIVE_DIR / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest written: {manifest_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Archive Claude Code sessions for map-reader-llm project"
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Also generate human-readable markdown versions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without copying files"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Claude Code Session Archiver")
    print("=" * 60)
    print()

    archive_sessions(markdown=args.markdown, dry_run=args.dry_run)

    print()
    print("Done!")


if __name__ == "__main__":
    main()
