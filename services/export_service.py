"""Service for exporting contributions to CSV"""
import os
from pathlib import Path
from utils.csv_utils import array_to_csv
from config.constants import (
    COMMIT_CSV_HEADERS,
    PULL_REQUEST_CSV_HEADERS,
    CODE_REVIEW_CSV_HEADERS,
)


def export_commits_to_csv(commits):
    """
    Export commits to CSV file
    
    Args:
        commits: List of commit dictionaries
    
    Returns:
        Path to CSV file or None if no commits
    """
    if not commits:
        return None
    
    # Convert to CSV
    print("\n💾 Converting commits to CSV... ", end="", flush=True)
    import time
    csv_start_time = time.time()
    csv_content = array_to_csv(commits, COMMIT_CSV_HEADERS)
    csv_time = f"{(time.time() - csv_start_time):.2f}"
    print(f"✓ ({csv_time}s)")
    
    # Write to file
    print("📝 Writing commits to file... ", end="", flush=True)
    write_start_time = time.time()
    
    # Get the script directory (parent of services)
    script_dir = Path(__file__).parent.parent
    exports_dir = script_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    output_path = exports_dir / "commits.csv"
    output_path.write_text(csv_content, encoding="utf-8")
    
    write_time = f"{(time.time() - write_start_time):.2f}"
    file_size = f"{(len(csv_content) / 1024):.2f}"
    print(f"✓ ({write_time}s, {file_size} KB)")
    
    return str(output_path)


def export_pull_requests_to_csv(pull_requests):
    """
    Export pull requests to CSV file
    
    Args:
        pull_requests: List of pull request dictionaries
    
    Returns:
        Path to CSV file or None if no pull requests
    """
    if not pull_requests:
        return None
    
    # Convert to CSV
    print("\n💾 Converting pull requests to CSV... ", end="", flush=True)
    import time
    csv_start_time = time.time()
    csv_content = array_to_csv(pull_requests, PULL_REQUEST_CSV_HEADERS)
    csv_time = f"{(time.time() - csv_start_time):.2f}"
    print(f"✓ ({csv_time}s)")
    
    # Write to file
    print("📝 Writing pull requests to file... ", end="", flush=True)
    write_start_time = time.time()
    
    # Get the script directory (parent of services)
    script_dir = Path(__file__).parent.parent
    exports_dir = script_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    output_path = exports_dir / "pullRequests.csv"
    output_path.write_text(csv_content, encoding="utf-8")
    
    write_time = f"{(time.time() - write_start_time):.2f}"
    file_size = f"{(len(csv_content) / 1024):.2f}"
    print(f"✓ ({write_time}s, {file_size} KB)")
    
    return str(output_path)


def export_code_reviews_to_csv(code_reviews):
    """
    Export code reviews to CSV file
    
    Args:
        code_reviews: List of code review dictionaries
    
    Returns:
        Path to CSV file or None if no code reviews
    """
    if not code_reviews:
        return None
    
    # Convert to CSV
    print("\n💾 Converting code reviews to CSV... ", end="", flush=True)
    import time
    csv_start_time = time.time()
    csv_content = array_to_csv(code_reviews, CODE_REVIEW_CSV_HEADERS)
    csv_time = f"{(time.time() - csv_start_time):.2f}"
    print(f"✓ ({csv_time}s)")
    
    # Write to file
    print("📝 Writing code reviews to file... ", end="", flush=True)
    write_start_time = time.time()
    
    # Get the script directory (parent of services)
    script_dir = Path(__file__).parent.parent
    exports_dir = script_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    output_path = exports_dir / "codeReviews.csv"
    output_path.write_text(csv_content, encoding="utf-8")
    
    write_time = f"{(time.time() - write_start_time):.2f}"
    file_size = f"{(len(csv_content) / 1024):.2f}"
    print(f"✓ ({write_time}s, {file_size} KB)")
    
    return str(output_path)


def export_to_csv(commits, pull_requests, code_reviews):
    """
    Export commits and/or pull requests and/or code reviews to CSV files
    
    Args:
        commits: List of commit dictionaries
        pull_requests: List of pull request dictionaries
        code_reviews: List of code review dictionaries
    
    Returns:
        List of output file paths
    """
    output_paths = []
    
    if commits:
        commits_path = export_commits_to_csv(commits)
        if commits_path:
            output_paths.append(commits_path)
    
    if pull_requests:
        prs_path = export_pull_requests_to_csv(pull_requests)
        if prs_path:
            output_paths.append(prs_path)
    
    if code_reviews:
        reviews_path = export_code_reviews_to_csv(code_reviews)
        if reviews_path:
            output_paths.append(reviews_path)
    
    return output_paths

