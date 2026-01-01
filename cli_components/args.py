"""Command line argument parsing"""
import sys
from utils.date_utils import validate_date
from utils.validation_utils import validate_affiliation
from config.constants import DEFAULT_AFFILIATION


def parse_args():
    """
    Parse command line arguments
    
    Returns:
        Dictionary with parsed arguments
    """
    args_list = sys.argv[2:]  # Skip script name and operation
    
    date_arg = args_list[0] if len(args_list) > 0 else None
    affiliation_arg = args_list[1] if len(args_list) > 1 else None
    types_arg = args_list[2] if len(args_list) > 2 else None
    
    since_date = None
    affiliation = DEFAULT_AFFILIATION
    fetch_commits = True
    fetch_pull_requests = False
    fetch_code_reviews = False
    
    if date_arg:
        try:
            since_date = validate_date(date_arg)
        except ValueError as error:
            print(f"❌ Error: {error}")
            print("\nUsage: python -m cli fetch [YYYY-MM-DDTHH:MM:SSZ] [affiliation] [types]")
            print("Example: python -m cli fetch 2024-01-01T00:00:00Z owner,collaborator commits")
            print("Types: commits, prs, reviews, all, or comma-separated (default: commits)")
            sys.exit(1)
    
    if affiliation_arg:
        try:
            affiliation = validate_affiliation(affiliation_arg)
        except ValueError as error:
            print(f"❌ Error: {error}")
            print("\nUsage: python -m unicon.cli fetch [YYYY-MM-DDTHH:MM:SSZ] [affiliation] [types]")
            print("Valid affiliations: owner, collaborator, organization_member")
            sys.exit(1)
    
    if types_arg:
        normalized = types_arg.lower()
        types = [t.strip() for t in normalized.split(",")]
        
        # Reset all flags
        fetch_commits = False
        fetch_pull_requests = False
        fetch_code_reviews = False
        
        # Handle special cases
        if normalized == "all" or "all" in types:
            fetch_commits = True
            fetch_pull_requests = True
            fetch_code_reviews = True
        elif normalized == "both":
            fetch_commits = True
            fetch_pull_requests = True
        else:
            # Set flags based on individual types
            if "commits" in types or "commit" in types:
                fetch_commits = True
            if "prs" in types or "pr" in types or "pullrequests" in types:
                fetch_pull_requests = True
            if "reviews" in types or "review" in types or "codereviews" in types:
                fetch_code_reviews = True
            
            # If no valid types found, default to commits
            if not fetch_commits and not fetch_pull_requests and not fetch_code_reviews:
                print(f"❌ Error: Invalid type \"{types_arg}\". Valid types: commits, prs, reviews, all, or comma-separated")
                sys.exit(1)
    
    return {
        "sinceDate": since_date,
        "affiliation": affiliation,
        "fetchCommits": fetch_commits,
        "fetchPullRequests": fetch_pull_requests,
        "fetchCodeReviews": fetch_code_reviews,
        "hasArgs": bool(date_arg or affiliation_arg or types_arg),
    }

