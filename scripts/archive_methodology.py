
import os
import shutil
import glob
from pathlib import Path

def archive_methodology():
    """
    Archives Gemini interaction logs and artifacts for Open Science methodology tracking.
    Copies files from ~/.gemini/antigravity to methodology/logs/.
    """
    # 1. Paths
    home_dir = Path.home()
    gemini_base = home_dir / ".gemini" / "antigravity"
    
    repo_root = Path(__file__).parent.parent
    dest_base = repo_root / "methodology" / "logs"
    dest_convs = dest_base / "conversations"
    dest_artifacts = dest_base / "artifacts"
    
    if not gemini_base.exists():
        print(f"Error: Gemini directory not found at {gemini_base}")
        return

    # Ensure destinations exist
    dest_convs.mkdir(parents=True, exist_ok=True)
    dest_artifacts.mkdir(parents=True, exist_ok=True)
    
    print(f"Archiving metodology from {gemini_base} to {dest_base}...")

    # 2. Archive Conversations (*.pb)
    conversations_dir = gemini_base / "conversations"
    pb_files = list(conversations_dir.glob("*.pb"))
    
    print(f"Found {len(pb_files)} conversation logs.")
    for pb in pb_files:
        dest_file = dest_convs / pb.name
        # Simple copy - overwrite to ensure latest version
        shutil.copy2(pb, dest_file)
        
    # 3. Archive Artifacts (brain/<UUID>/*.md)
    brain_dir = gemini_base / "brain"
    brain_uuid_dirs = [d for d in brain_dir.iterdir() if d.is_dir()]
    
    print(f"Found {len(brain_uuid_dirs)} artifact sessions.")
    for session_dir in brain_uuid_dirs:
        uuid = session_dir.name
        
        # We only care about sessions matching our conversations, or all? 
        # Let's archive all found in brain to be safe.
        
        dest_session_dir = dest_artifacts / uuid
        dest_session_dir.mkdir(exist_ok=True)
        
        # Copy Markdown Artifacts
        artifacts = list(session_dir.glob("*.md"))
        for art in artifacts:
            # We skip specific resolved versions to save space? 
            # e.g. task.md.resolved.1 is probably overkill. 
            # Let's stick to the main artifacts for now: task.md, implementation_plan.md, walkthrough.md
            # Or just copy all .md files that don't have .resolved in them?
            if ".resolved" in art.name:
                continue
                
            shutil.copy2(art, dest_session_dir / art.name)

    print("Methodology archiving complete.")

if __name__ == "__main__":
    archive_methodology()
