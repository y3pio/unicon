"""Interactive prompts for user input"""
import questionary
from utils.date_utils import validate_date
from utils.validation_utils import validate_affiliation


def prompt_user():
    """
    Interactive prompt for user input
    
    Returns:
        Dictionary with user selections
    """
    fetch_types = questionary.checkbox(
        "What would you like to fetch?",
        choices=[
            {"name": "Commits", "value": "commits", "checked": True},
            {"name": "Pull Requests", "value": "pullRequests", "checked": False},
            {"name": "Code Reviews", "value": "codeReviews", "checked": False},
        ],
        validate=lambda x: len(x) > 0 or "Please select at least one option",
    ).ask()
    
    use_date_filter = questionary.confirm(
        "Do you want to filter by date?",
        default=False,
    ).ask()
    
    since_date = None
    if use_date_filter:
        since_date = questionary.text(
            "Enter start date (YYYY-MM-DDTHH:MM:SSZ):",
            validate=lambda x: validate_date(x) is not None or "Invalid date format",
        ).ask()
        since_date = validate_date(since_date)
    
    affiliation = questionary.select(
        "Which repositories should be included?",
        choices=[
            {
                "name": "All (owner + collaborator + organization member)",
                "value": "owner,collaborator,organization_member",
            },
            {
                "name": "Owned + Collaborator (exclude organization repos)",
                "value": "owner,collaborator",
            },
            {"name": "Only owned repositories", "value": "owner"},
            {"name": "Only collaborator repositories", "value": "collaborator"},
            {"name": "Custom (comma-separated)", "value": "custom"},
        ],
        default="owner,collaborator",
    ).ask()
    
    if affiliation == "custom":
        custom_affiliation = questionary.text(
            "Enter affiliations (comma-separated: owner,collaborator,organization_member):",
            validate=lambda x: validate_affiliation(x) is not None or "Invalid affiliation",
        ).ask()
        affiliation = validate_affiliation(custom_affiliation)
    
    return {
        "fetchCommits": "commits" in fetch_types,
        "fetchPullRequests": "pullRequests" in fetch_types,
        "fetchCodeReviews": "codeReviews" in fetch_types,
        "sinceDate": since_date,
        "affiliation": affiliation,
    }

