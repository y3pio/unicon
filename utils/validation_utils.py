"""Validation utilities"""
import os
from .date_utils import validate_date


def validate_affiliation(affiliation_str):
    """
    Validate affiliation parameter
    
    Args:
        affiliation_str: Comma-separated string of affiliations
    
    Returns:
        Validated affiliation string
    
    Raises:
        ValueError: If affiliation is invalid
    """
    if not affiliation_str:
        return None
    
    valid_values = ["owner", "collaborator", "organization_member"]
    affiliations = [a.strip() for a in affiliation_str.split(",")]
    
    for aff in affiliations:
        if aff not in valid_values:
            raise ValueError(
                f"Invalid affiliation: {aff}. Valid values are: {', '.join(valid_values)}"
            )
    
    return ",".join(affiliations)


def validate_environment():
    """
    Validate environment variables
    
    Raises:
        ValueError: If required environment variables are missing
    """
    if not os.getenv("GITHUB_TOKEN"):
        raise ValueError("GITHUB_TOKEN is required. Create a .env file with your token.")
    
    if not os.getenv("GITHUB_USERNAME"):
        raise ValueError("GITHUB_USERNAME is required. Add it to your .env file.")

