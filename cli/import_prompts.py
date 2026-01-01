"""Interactive prompts for import options"""
import questionary
from pathlib import Path


def file_exists(file_path):
    """Check if a file exists"""
    return Path(file_path).exists()


def prompt_import_options():
    """
    Interactive prompt for import options
    
    Returns:
        Dictionary with import selections
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
    
    if not has_commits and not has_prs and not has_reviews:
        raise FileNotFoundError("No CSV files found in exports/ directory")
    
    # Build available options
    choices = []
    if has_commits:
        choices.append({"name": "Commits", "value": "commits", "checked": True})
    if has_prs:
        choices.append({"name": "Pull Requests", "value": "pullRequests", "checked": True})
    if has_reviews:
        choices.append({"name": "Code Reviews", "value": "codeReviews", "checked": True})
    
    # If only one option, skip prompt
    if len(choices) == 1:
        return {
            "importCommits": has_commits,
            "importPullRequests": has_prs,
            "importCodeReviews": has_reviews,
        }
    
    import_types = questionary.checkbox(
        "Which contributions would you like to import?",
        choices=choices,
        validate=lambda x: len(x) > 0 or "Please select at least one option",
    ).ask()
    
    return {
        "importCommits": "commits" in import_types,
        "importPullRequests": "pullRequests" in import_types,
        "importCodeReviews": "codeReviews" in import_types,
    }

