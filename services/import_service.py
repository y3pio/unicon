"""Service for importing contributions from CSV to markdown files"""
import csv
from pathlib import Path
from datetime import datetime


def is_valid_commit(commit):
    """Validate commit has required fields"""
    return bool(commit.get("author_date") and commit.get("short_sha"))


def is_valid_pull_request(pr):
    """Validate pull request has required fields"""
    return bool(pr.get("author_date") and pr.get("short_sha"))


def is_valid_code_review(review):
    """Validate code review has required fields"""
    return bool(review.get("submitted_at") and review.get("review_id"))


def format_date_for_filename(date_str):
    """
    Format date for filename: YYYY-MM-DDTHH-MM-SS
    
    Args:
        date_str: ISO 8601 format date string (e.g., 2025-05-07T17:16:40Z)
    
    Returns:
        Filename-safe date string (e.g., 2025-05-07T17-16-40)
    """
    # Convert ISO 8601 format (2025-05-07T17:16:40Z) to filename format (2025-05-07T17-16-40)
    return date_str.replace(":", "-").replace("Z", "")


def generate_commit_markdown(commit):
    """Generate markdown content for a commit"""
    try:
        date_obj = datetime.fromisoformat(commit["author_date"].replace("Z", "+00:00"))
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date = commit["author_date"]
    
    return f"""# Commit

- **Date**: {date}
- **SHA**: `{commit['short_sha']}`
- **Full SHA**: `{commit['sha']}`
- **Author**: {commit.get('author_name', '')}
"""


def generate_pull_request_markdown(pr):
    """Generate markdown content for a pull request"""
    try:
        date_obj = datetime.fromisoformat(pr["author_date"].replace("Z", "+00:00"))
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date = pr["author_date"]
    
    sha_line = f"- **Full SHA**: `{pr['sha']}`\n" if pr.get("sha") else ""
    
    return f"""# Pull Request

- **Date**: {date}
- **SHA**: `{pr['short_sha']}`
{sha_line}- **Author**: {pr.get('author_name', '')}
"""


def generate_code_review_markdown(review):
    """Generate markdown content for a code review"""
    try:
        date_obj = datetime.fromisoformat(review["submitted_at"].replace("Z", "+00:00"))
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except:
        date = review["submitted_at"]
    
    return f"""# Code Review

- **Date**: {date}
- **Review ID**: `{review['review_id']}`
- **State**: {review.get('state', '')}
"""


def parse_csv_file(csv_path):
    """
    Parse CSV file and return array of dictionaries
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        List of dictionaries with CSV data
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return []
    
    items = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Strip whitespace from values
            items.append({k: v.strip() if v else "" for k, v in row.items()})
    
    return items


def import_items_from_csv(
    csv_path,
    output_dir,
    item_type,
    is_valid_item,
    generate_markdown,
    get_file_name,
):
    """
    Import items from CSV to markdown files (generic function)
    
    Args:
        csv_path: Path to CSV file
        output_dir: Directory to write markdown files
        item_type: Type name for logging (e.g., "commits")
        is_valid_item: Function to validate items
        generate_markdown: Function to generate markdown content
        get_file_name: Function to generate filename from item
    
    Returns:
        Dictionary with import statistics
    """
    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    
    # Check if CSV file exists
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse CSV
    print(f"📖 Reading {item_type} CSV file...")
    all_items = parse_csv_file(csv_path)
    print(f"✓ Found {len(all_items)} {item_type}\n")
    
    # Filter out invalid items
    items = [item for item in all_items if is_valid_item(item)]
    discarded = len(all_items) - len(items)
    
    if discarded > 0:
        print(f"⚠️  Discarded {discarded} invalid {item_type}(s) (missing required fields)\n")
    
    if not items:
        print(f"⚠️  No valid {item_type} to import")
        return {"total": 0, "valid": 0, "discarded": 0, "imported": 0, "skipped": 0}
    
    # Process each item
    imported = 0
    skipped = 0
    
    for i, item in enumerate(items, 1):
        current = i
        total = len(items)
        percentage = f"{(current / total * 100):.1f}"
        
        # Generate filename
        filename = get_file_name(item)
        file_path = output_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            skipped += 1
            print(f"[{current}/{total}] ({percentage}%) Skipping: {filename} (already exists)... ⏭️")
            continue
        
        # Generate markdown content
        markdown = generate_markdown(item)
        
        # Write file
        print(f"[{current}/{total}] ({percentage}%) Creating: {filename}... ", end="", flush=True)
        file_path.write_text(markdown, encoding="utf-8")
        imported += 1
        print("✓")
    
    print(f"\n{'═' * 60}")
    print(f"📊 {item_type.title()} Import Summary:")
    print(f"   Total {item_type} in CSV: {len(all_items)}")
    print(f"   Valid {item_type}: {len(items)}")
    if discarded > 0:
        print(f"   Discarded (invalid): {discarded}")
    print(f"   Imported: {imported}")
    print(f"   Skipped (already exist): {skipped}")
    print(f"{'═' * 60}\n")
    
    # Delete CSV file
    print(f"🗑️  Deleting {item_type} CSV file...")
    csv_path.unlink()
    print(f"✓ CSV file deleted\n")
    
    return {
        "total": len(all_items),
        "valid": len(items),
        "discarded": discarded,
        "imported": imported,
        "skipped": skipped,
    }


def import_commits_from_csv():
    """Import commits from CSV to markdown files"""
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / "exports" / "commits.csv"
    commits_dir = script_dir.parent / "contributions" / "commits"
    
    return import_items_from_csv(
        csv_path=csv_path,
        output_dir=commits_dir,
        item_type="commits",
        is_valid_item=is_valid_commit,
        generate_markdown=generate_commit_markdown,
        get_file_name=lambda commit: f"{format_date_for_filename(commit['author_date'])}-{commit['short_sha']}.md",
    )


def import_pull_requests_from_csv():
    """Import pull requests from CSV to markdown files"""
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / "exports" / "pullRequests.csv"
    prs_dir = script_dir.parent / "contributions" / "pull-requests"
    
    return import_items_from_csv(
        csv_path=csv_path,
        output_dir=prs_dir,
        item_type="pull requests",
        is_valid_item=is_valid_pull_request,
        generate_markdown=generate_pull_request_markdown,
        get_file_name=lambda pr: f"{format_date_for_filename(pr['author_date'])}-{pr['short_sha']}.md",
    )


def import_code_reviews_from_csv():
    """Import code reviews from CSV to markdown files"""
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / "exports" / "codeReviews.csv"
    reviews_dir = script_dir.parent / "contributions" / "code-reviews"
    
    return import_items_from_csv(
        csv_path=csv_path,
        output_dir=reviews_dir,
        item_type="code reviews",
        is_valid_item=is_valid_code_review,
        generate_markdown=generate_code_review_markdown,
        get_file_name=lambda review: f"{format_date_for_filename(review['submitted_at'])}-{review['review_id']}.md",
    )


def file_exists(file_path):
    """Check if a file exists"""
    return Path(file_path).exists()


def import_contributions(import_commits=True, import_pull_requests=True, import_code_reviews=True):
    """
    Import contributions based on options
    
    Args:
        import_commits: Whether to import commits
        import_pull_requests: Whether to import pull requests
        import_code_reviews: Whether to import code reviews
    
    Returns:
        Dictionary with import results
    """
    results = {
        "commits": None,
        "pullRequests": None,
        "codeReviews": None,
    }
    
    # Import commits if requested
    if import_commits:
        try:
            results["commits"] = import_commits_from_csv()
        except Exception as error:
            raise Exception(f"Failed to import commits: {error}")
    
    # Import pull requests if requested
    if import_pull_requests:
        try:
            results["pullRequests"] = import_pull_requests_from_csv()
        except Exception as error:
            raise Exception(f"Failed to import pull requests: {error}")
    
    # Import code reviews if requested
    if import_code_reviews:
        try:
            results["codeReviews"] = import_code_reviews_from_csv()
        except Exception as error:
            raise Exception(f"Failed to import code reviews: {error}")
    
    return results

