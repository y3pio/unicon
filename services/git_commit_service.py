"""Service for committing contributions to git with original timestamps"""
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime


def parse_date_from_filename(filename):
    """
    Parse date from filename: YYYY-MM-DDTHH-MM-SS-{sha}.md
    Returns ISO 8601 format date string
    
    Args:
        filename: Markdown filename
    
    Returns:
        ISO 8601 date string or None if invalid
    """
    # Extract date part: YYYY-MM-DDTHH-MM-SS
    match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})-", filename)
    if not match:
        return None
    
    # Convert to ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
    date_str = match.group(1).replace("-", ":", 3).replace(":", "-", 2)
    # Replace the time separators (after T) with colons
    parts = date_str.split("T")
    if len(parts) == 2:
        date_part = parts[0]
        time_part = parts[1].replace("-", ":")
        date_str = f"{date_part}T{time_part}Z"
    
    return date_str


def format_date_for_git(iso_date):
    """
    Convert ISO 8601 date to git date format: YYYY-MM-DD HH:MM:SS +0000 (UTC)
    GitHub contributions chart uses UTC, so we need to ensure dates are in UTC
    
    Args:
        iso_date: ISO 8601 date string
    
    Returns:
        Git date format string
    """
    try:
        date = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        year = date.year
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"
        hours = f"{date.hour:02d}"
        minutes = f"{date.minute:02d}"
        seconds = f"{date.second:02d}"
        
        # Return in UTC format: YYYY-MM-DD HH:MM:SS +0000
        return f"{year}-{month}-{day} {hours}:{minutes}:{seconds} +0000"
    except:
        return iso_date


def get_markdown_files(directory):
    """
    Get all markdown files from a directory
    
    Args:
        directory: Directory path
    
    Returns:
        List of dicts with filename and filepath
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    files = []
    for file in directory.glob("*.md"):
        if file.name != "README.md":
            files.append({
                "filename": file.name,
                "filepath": str(file),
            })
    
    return files


def commit_file(filepath, relative_path, date, repo_root):
    """
    Commit a single file with its original timestamp
    
    Args:
        filepath: Full path to file
        relative_path: Relative path from repo root
        date: ISO date string
        repo_root: Repository root directory
    """
    git_date = format_date_for_git(date)
    commit_message = f"Add contribution: {Path(filepath).name}"
    
    # Stage the file
    subprocess.run(
        ["git", "add", relative_path],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    
    # Commit with original date
    env = {
        **dict(os.environ),
        "GIT_AUTHOR_DATE": git_date,
        "GIT_COMMITTER_DATE": git_date,
    }
    
    subprocess.run(
        ["git", "commit", "-m", commit_message],
        env=env,
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def commit_contributions(commit_types=None):
    """
    Process and commit all contribution files with their original timestamps
    
    Args:
        commit_types: Dictionary with commits, pullRequests, codeReviews flags
    
    Returns:
        Dictionary with commit statistics
    """
    
    if commit_types is None:
        commit_types = {"commits": True, "pullRequests": True, "codeReviews": True}
    
    script_dir = Path(__file__).parent.parent
    repo_root = script_dir.parent
    commits_dir = repo_root / "contributions" / "commits"
    prs_dir = repo_root / "contributions" / "pull-requests"
    reviews_dir = repo_root / "contributions" / "code-reviews"
    
    all_files = []
    
    # Get commit files
    if commit_types.get("commits"):
        commit_files = get_markdown_files(commits_dir)
        all_files.extend([
            {
                **file,
                "type": "commit",
                "relativePath": str(Path(file["filepath"]).relative_to(repo_root)),
            }
            for file in commit_files
        ])
    
    # Get pull request files
    if commit_types.get("pullRequests"):
        pr_files = get_markdown_files(prs_dir)
        all_files.extend([
            {
                **file,
                "type": "pull-request",
                "relativePath": str(Path(file["filepath"]).relative_to(repo_root)),
            }
            for file in pr_files
        ])
    
    # Get code review files
    if commit_types.get("codeReviews"):
        review_files = get_markdown_files(reviews_dir)
        all_files.extend([
            {
                **file,
                "type": "code-review",
                "relativePath": str(Path(file["filepath"]).relative_to(repo_root)),
            }
            for file in review_files
        ])
    
    if not all_files:
        print("⚠️  No contribution files found to commit")
        return {"committed": 0, "skipped": 0, "errors": 0}
    
    # Sort by date to commit in chronological order
    def get_date_key(file):
        date = parse_date_from_filename(file["filename"])
        return datetime.fromisoformat(date.replace("Z", "+00:00")) if date else datetime.min
    
    all_files.sort(key=get_date_key)
    
    print(f"\n📝 Found {len(all_files)} contribution file(s) to commit\n")
    
    committed = 0
    skipped = 0
    errors = 0
    
    for i, file in enumerate(all_files, 1):
        current = i
        total = len(all_files)
        percentage = f"{(current / total * 100):.1f}"
        
        date = parse_date_from_filename(file["filename"])
        if not date:
            print(f"⚠️  [{current}/{total}] Skipping {file['filename']}: Invalid date format")
            skipped += 1
            continue
        
        # Check if file is already committed
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--", file["relativePath"]],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                print(f"[{current}/{total}] ({percentage}%) Skipping: {file['filename']} (already committed)... ⏭️")
                skipped += 1
                continue
        except:
            # File not in git history, proceed
            pass
        
        try:
            print(f"[{current}/{total}] ({percentage}%) Committing: {file['filename']} ({date})... ", end="", flush=True)
            commit_file(file["filepath"], file["relativePath"], date, str(repo_root))
            committed += 1
            print("✓")
        except Exception as error:
            errors += 1
            print("✗")
            print(f"   Error: {error}")
    
    print(f"\n{'═' * 60}")
    print("📊 Commit Summary:")
    print(f"   Total files: {len(all_files)}")
    print(f"   Committed: {committed}")
    print(f"   Skipped (already committed): {skipped}")
    if errors > 0:
        print(f"   Errors: {errors}")
    print(f"{'═' * 60}\n")
    
    return {"committed": committed, "skipped": skipped, "errors": errors}

