"""Repository fetching functions"""


def fetch_user_repos(github_client, affiliation):
    """
    Fetch all repositories accessible to the user
    
    Args:
        github_client: Authenticated GitHub client
        affiliation: Comma-separated list of affiliations (owner, collaborator, organization_member)
    
    Returns:
        List of dicts with owner, name, and private fields
    """
    user = github_client.get_user()
    
    # Parse affiliation string
    affiliations = [a.strip() for a in affiliation.split(",")]
    
    repos = []
    for repo in user.get_repos(affiliation=affiliation):
        repos.append({
            "owner": repo.owner.login,
            "name": repo.name,
            "private": repo.private,
        })
    
    return repos

