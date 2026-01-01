"""Command line argument parsing for import"""
import sys
from pathlib import Path


def file_exists(file_path):
    """Check if a file exists"""
    return Path(file_path).exists()


def parse_import_args():
    """
    Parse command line arguments for import
    
    Returns:
        Dictionary with parsed import arguments
    """
    # Get the script directory (parent of cli/)
    script_dir = Path(__file__).parent.parent
    exports_dir = script_dir / "exports"
    commits_csv_path = exports_dir / "commits.csv"
    prs_csv_path = exports_dir / "pullRequests.csv"
    reviews_csv_path = exports_dir / "codeReviews.csv"
    
    has_commits = file_exists(commits_csv_path)
    has_prs = file_exists(prs_csv_path)
    has_reviews = file_exists(reviews_csv_path)
    
    types_arg = sys.argv[2] if len(sys.argv) > 2 else None
    
    import_commits = has_commits
    import_pull_requests = has_prs
    import_code_reviews = has_reviews
    
    # If no CSV files exist, show error
    if not has_commits and not has_prs and not has_reviews:
        print("❌ Error: No CSV files found in exports/ directory")
        print("   Expected: commits.csv and/or pullRequests.csv and/or codeReviews.csv")
        sys.exit(1)
    
    # If argument provided, use it to filter
    if types_arg:
        normalized = types_arg.lower()
        types = [t.strip() for t in normalized.split(",")]
        
        # Reset all flags
        import_commits = False
        import_pull_requests = False
        import_code_reviews = False
        
        # Handle special cases
        if normalized == "all":
            import_commits = has_commits
            import_pull_requests = has_prs
            import_code_reviews = has_reviews
        elif normalized == "both":
            import_commits = has_commits
            import_pull_requests = has_prs
        else:
            # Set flags based on individual types
            if "commits" in types or "commit" in types:
                if not has_commits:
                    print("❌ Error: commits.csv not found")
                    sys.exit(1)
                import_commits = True
            if "prs" in types or "pr" in types or "pullrequests" in types:
                if not has_prs:
                    print("❌ Error: pullRequests.csv not found")
                    sys.exit(1)
                import_pull_requests = True
            if "reviews" in types or "review" in types or "codereviews" in types:
                if not has_reviews:
                    print("❌ Error: codeReviews.csv not found")
                    sys.exit(1)
                import_code_reviews = True
            
            # If no valid types found, show error
            if not import_commits and not import_pull_requests and not import_code_reviews:
                print(f"❌ Error: Invalid type \"{types_arg}\"")
                print("Usage: python -m cli import [commits|prs|reviews|all]")
                print("Example: python -m cli import commits,prs,reviews")
                sys.exit(1)
    
    return {
        "importCommits": import_commits,
        "importPullRequests": import_pull_requests,
        "importCodeReviews": import_code_reviews,
        "hasArgs": bool(types_arg),
    }

