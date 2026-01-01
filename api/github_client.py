"""GitHub API client initialization"""
import os
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_github_client():
    """
    Initialize and return GitHub API client
    Supports both public GitHub and GitHub Enterprise via GITHUB_API_URL
    """
    token = os.getenv("GITHUB_TOKEN")
    api_url = os.getenv("GITHUB_API_URL")
    
    if api_url:
        # GitHub Enterprise
        return Github(base_url=api_url, login_or_token=token)
    else:
        # Public GitHub
        return Github(token)


def get_github_username():
    """Get GitHub username from environment"""
    return os.getenv("GITHUB_USERNAME")

