#!/usr/bin/env python3
"""
Generate session catalog files from archived CC sessions.

This script scans all archived sessions and generates:
- CATALOG.json: Machine-readable session index
- CATALOG.md: Human-readable session listing

Usage:
    python scripts/generate_session_catalog.py

The script reads session.meta.json files from all project subdirectories
in archive/cc-sessions/ and regenerates the catalog files.

Created: 2026-01-08
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


# =============================================================================
# Configuration
# =============================================================================

ARCHIVE_DIR = Path(__file__).parent.parent / "archive" / "cc-sessions"
CATALOG_JSON = ARCHIVE_DIR / "CATALOG.json"
CATALOG_MD = ARCHIVE_DIR / "CATALOG.md"
SCHEMA_VERSION = "1.1"


# =============================================================================
# Catalog Generation
# =============================================================================

def scan_sessions() -> list[dict[str, Any]]:
    """
    Scan all archived sessions and collect metadata.

    Returns:
        List of session metadata dictionaries
    """
    sessions = []

    # Scan all project directories
    for project_dir in ARCHIVE_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        # Skip special directories
        if project_dir.name in ("queries",):
            continue

        # Scan session directories within project
        for session_dir in project_dir.iterdir():
            if not session_dir.is_dir():
                continue

            meta_file = session_dir / "session.meta.json"
            if not meta_file.exists():
                # Try to find metadata in old format or skip
                continue

            try:
                metadata = json.loads(meta_file.read_text())
                sessions.append({
                    "metadata": metadata,
                    "path": session_dir,
                    "project": project_dir.name
                })
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not read {meta_file}: {e}")

    return sessions


def generate_catalog_json(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Generate the CATALOG.json structure (v1.1).

    Args:
        sessions: List of session data from scan_sessions()

    Returns:
        Complete catalog dictionary
    """
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().isoformat(),
        "total_sessions": len(sessions),
        "projects": {},
        "sessions": [],
        "tag_index": {},
        "relationship_graph": {}  # v1.1: Track inverse relationships
    }

    # Build session ID to directory mapping for relationship resolution
    id_to_dir: dict[str, str] = {}

    # Build project and session lists
    for session_data in sessions:
        meta = session_data["metadata"]
        project = session_data["project"]
        rel_path = session_data["path"].relative_to(ARCHIVE_DIR)
        session_id = meta.get("session", {}).get("id", "unknown")

        # Track ID to directory mapping
        id_to_dir[session_id] = str(rel_path)

        # Add to projects
        if project not in catalog["projects"]:
            catalog["projects"][project] = {
                "name": project,
                "session_count": 0,
                "total_duration_minutes": 0
            }
        catalog["projects"][project]["session_count"] += 1
        catalog["projects"][project]["total_duration_minutes"] += \
            meta.get("session", {}).get("duration_minutes", 0)

        # Extract v1.1 fields
        relationships = meta.get("relationships", {})
        artifacts = meta.get("artifacts", {})
        thinking_blocks = meta.get("thinking_blocks", {})

        # Count artifacts
        artifact_counts = {
            "created": len(artifacts.get("created", [])),
            "modified": len(artifacts.get("modified", [])),
            "referenced": len(artifacts.get("referenced", []))
        }

        # Build session entry with v1.1 fields
        session_entry = {
            "id": session_id,
            "project": project,
            "directory": str(rel_path),
            "title": meta.get("auto_generated", {}).get("title", "Untitled"),
            "purpose": meta.get("auto_generated", {}).get("purpose", ""),
            "tags": meta.get("auto_generated", {}).get("tags", []),
            "started_at": meta.get("session", {}).get("started_at"),
            "duration_minutes": meta.get("session", {}).get("duration_minutes", 0),
            "model": meta.get("model", {}).get("model_id", "unknown"),
            "statistics": {
                "turns": meta.get("statistics", {}).get("turns", 0),
                "tool_calls": meta.get("statistics", {}).get("tool_calls", {}).get("total", 0),
                "thinking_blocks": meta.get("statistics", {}).get("thinking_blocks", 0)
            },
            # v1.1 fields
            "relationships": {
                "continues": relationships.get("continues"),
                "isPartOf": relationships.get("isPartOf", [])
            },
            "artifact_counts": artifact_counts,
            "thinking_blocks_tokens": thinking_blocks.get("total_tokens", 0)
        }
        catalog["sessions"].append(session_entry)

        # Build tag index
        for tag in session_entry["tags"]:
            if tag not in catalog["tag_index"]:
                catalog["tag_index"][tag] = []
            catalog["tag_index"][tag].append(session_id)

        # Build relationship graph (v1.1)
        # Track forward relationships to build inverse lookups
        continues_target = relationships.get("continues")
        if continues_target:
            if continues_target not in catalog["relationship_graph"]:
                catalog["relationship_graph"][continues_target] = {"continuedBy": []}
            catalog["relationship_graph"][continues_target]["continuedBy"].append(session_id)

    # Sort sessions by date (newest first)
    catalog["sessions"].sort(
        key=lambda s: s.get("started_at") or "",
        reverse=True
    )

    # Sort tag index alphabetically
    catalog["tag_index"] = dict(sorted(catalog["tag_index"].items()))

    return catalog


def format_duration(minutes: int) -> str:
    """Format duration in minutes to a readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def format_date(iso_date: str | None) -> str:
    """Format ISO date to readable format."""
    if not iso_date:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_date[:16] if iso_date else "Unknown"


def generate_catalog_md(catalog: dict[str, Any]) -> str:
    """
    Generate the human-readable CATALOG.md content.

    Args:
        catalog: Catalog dictionary from generate_catalog_json()

    Returns:
        Markdown string
    """
    lines = [
        "# CC Session Catalog",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "## Overview",
        "",
        f"- **Total sessions**: {catalog['total_sessions']}",
        f"- **Projects**: {len(catalog['projects'])}",
        ""
    ]

    # Project summary
    if catalog["projects"]:
        lines.extend([
            "### Projects",
            "",
            "| Project | Sessions | Total Duration |",
            "|---------|----------|----------------|"
        ])
        for project, info in sorted(catalog["projects"].items()):
            duration = format_duration(info["total_duration_minutes"])
            lines.append(f"| {project} | {info['session_count']} | {duration} |")
        lines.append("")

    # Sessions by date
    lines.extend([
        "## Sessions",
        ""
    ])

    current_project = None
    for session in catalog["sessions"]:
        # Group by project
        if session["project"] != current_project:
            current_project = session["project"]
            lines.extend([
                f"### {current_project}",
                ""
            ])

        # Session entry
        date = format_date(session["started_at"])
        duration = format_duration(session["duration_minutes"])
        tags = ", ".join(session["tags"]) if session["tags"] else "-"
        stats = session["statistics"]

        # v1.1 fields
        artifact_counts = session.get("artifact_counts", {})
        artifacts_str = (
            f"{artifact_counts.get('created', 0)} created, "
            f"{artifact_counts.get('modified', 0)} modified, "
            f"{artifact_counts.get('referenced', 0)} referenced"
        )
        thinking_tokens = session.get("thinking_blocks_tokens", 0)

        lines.extend([
            f"#### {session['title']}",
            "",
            f"- **Date**: {date}",
            f"- **Duration**: {duration}",
            f"- **Directory**: `{session['directory']}`",
            f"- **Model**: {session['model']}",
            f"- **Statistics**: {stats['turns']} turns, {stats['tool_calls']} tool calls, "
            f"{stats['thinking_blocks']} thinking blocks (~{thinking_tokens:,} tokens)",
            f"- **Artifacts**: {artifacts_str}",
            f"- **Tags**: {tags}",
            ""
        ])

        if session["purpose"]:
            lines.extend([
                f"> {session['purpose']}",
                ""
            ])

    # Tag index
    if catalog["tag_index"]:
        lines.extend([
            "## Tag Index",
            ""
        ])
        for tag, session_ids in sorted(catalog["tag_index"].items()):
            lines.append(f"- **{tag}**: {len(session_ids)} session(s)")
        lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        "*This catalog is auto-generated. Do not edit manually.*",
        "*Regenerate with: `python scripts/generate_session_catalog.py`*",
        ""
    ])

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    print("CC Session Catalog Generator")
    print("=" * 40)
    print()

    # Ensure archive directory exists
    if not ARCHIVE_DIR.exists():
        print(f"Error: Archive directory not found: {ARCHIVE_DIR}")
        return

    # Scan sessions
    print("Scanning archived sessions...")
    sessions = scan_sessions()
    print(f"Found {len(sessions)} session(s)")

    if not sessions:
        print("No sessions to catalog.")
        # Still create empty catalog
        catalog = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": datetime.now().isoformat(),
            "total_sessions": 0,
            "projects": {},
            "sessions": [],
            "tag_index": {}
        }
    else:
        # Generate catalog
        print("Generating catalog...")
        catalog = generate_catalog_json(sessions)

    # Write CATALOG.json
    CATALOG_JSON.write_text(json.dumps(catalog, indent=2))
    print(f"Wrote: {CATALOG_JSON}")

    # Write CATALOG.md
    markdown = generate_catalog_md(catalog)
    CATALOG_MD.write_text(markdown)
    print(f"Wrote: {CATALOG_MD}")

    # Summary
    print()
    print("Summary:")
    print(f"  Sessions: {catalog['total_sessions']}")
    print(f"  Projects: {len(catalog['projects'])}")
    print(f"  Tags: {len(catalog['tag_index'])}")
    print()
    print("Done!")


if __name__ == "__main__":
    main()
