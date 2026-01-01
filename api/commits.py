"""Commit fetching functions"""
from datetime import datetime


def transform_commit(commit, owner, repo):
    """Transform raw commit data to our format"""
    commit_data = commit.commit
    
    return {
        "type": "commit",
        "sha": commit.sha,
        "short_sha": commit.sha[:7],
        "message": commit_data.message,
        "message_first_line": commit_data.message.split("\n")[0],
        "author_name": commit_data.author.name,
        "author_email": commit_data.author.email,
        "author_date": commit_data.author.date.isoformat().replace("+00:00", "Z") if commit_data.author.date else "",
        "committer_name": commit_data.committer.name,
        "committer_email": commit_data.committer.email,
        "committer_date": commit_data.committer.date.isoformat().replace("+00:00", "Z") if commit_data.committer.date else "",
        "repo": f"{owner}/{repo}",
        "repo_owner": owner,
        "repo_name": repo,
        "url": commit.html_url,
        "api_url": commit.url,
        "node_id": commit.node_id,
        "parents": ";".join([p.sha for p in commit.parents]),
        "stats_additions": getattr(commit.stats, "additions", "") if hasattr(commit, "stats") else "",
        "stats_deletions": getattr(commit.stats, "deletions", "") if hasattr(commit, "stats") else "",
        "stats_total": getattr(commit.stats, "total", "") if hasattr(commit, "stats") else "",
        "files_changed": len(commit.files) if hasattr(commit, "files") else "",
        "verification_verified": commit_data.verification.verified if commit_data.verification else False,
        "verification_reason": commit_data.verification.reason if commit_data.verification else "",
    }


def fetch_commits(github_client, owner, repo, username, since_date=None, show_sample=False):
    """
    Fetch commits from a repository
    
    Args:
        github_client: Authenticated GitHub client
        owner: Repository owner
        repo: Repository name
        username: GitHub username to filter commits
        since_date: Optional ISO date string to filter commits
        show_sample: Whether to print a sample commit object
    
    Returns:
        List of transformed commit dictionaries
    """
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        
        # Build parameters
        params = {"author": username}
        if since_date:
            params["since"] = datetime.fromisoformat(since_date.replace("Z", "+00:00"))
        
        commits = []
        for commit in repository.get_commits(**params):
            commits.append(transform_commit(commit, owner, repo))
        
        # Log first commit to see the shape (only once)
        if commits and show_sample:
            import json
            print("\n=== Sample Commit Object Shape ===")
            print(json.dumps(commits[0], indent=2, default=str))
            print("===================================\n")
        
        return commits
    except Exception as error:
        print(f"Error fetching commits for {owner}/{repo}: {error}")
        return []

