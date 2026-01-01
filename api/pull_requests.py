"""Pull request fetching functions"""
import re
from datetime import datetime


def transform_pull_request(pr):
    """Transform raw pull request data to our format"""
    # Extract owner/repo from the repository
    owner = pr.base.repo.owner.login
    repo = pr.base.repo.name
    
    # Use merge commit SHA if merged, otherwise use head SHA
    sha = pr.merge_commit_sha if pr.merged else (pr.head.sha if pr.head else "")
    short_sha = sha[:7] if sha else f"pr-{pr.number}"
    
    # Sanitize title to single line (remove newlines)
    title = (pr.title or "").replace("\n", " ").replace("\r", " ").strip()
    
    return {
        "type": "pull-request",
        "number": pr.number,
        "sha": sha,
        "short_sha": short_sha,
        "title": title,
        "state": pr.state,
        "created_at": pr.created_at.isoformat().replace("+00:00", "Z") if pr.created_at else "",
        "merged_at": pr.merged_at.isoformat().replace("+00:00", "Z") if pr.merged_at else "",
        "closed_at": pr.closed_at.isoformat().replace("+00:00", "Z") if pr.closed_at else "",
        "author_name": pr.user.login if pr.user else "",
        "author_date": pr.created_at.isoformat().replace("+00:00", "Z") if pr.created_at else "",
        "repo": f"{owner}/{repo}",
        "repo_owner": owner,
        "repo_name": repo,
        "url": pr.html_url,
        "api_url": pr.url,
        "node_id": pr.node_id,
        "merged": pr.merged,
        "draft": pr.draft,
        "head_sha": pr.head.sha if pr.head else "",
        "merge_commit_sha": pr.merge_commit_sha if pr.merged else "",
    }


def fetch_pull_request_details(github_client, owner, repo, pr_number):
    """Fetch full PR details to get merge_commit_sha and other fields"""
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(pr_number)
        return pr
    except Exception as error:
        print(f"  Warning: Could not fetch details for {owner}/{repo}#{pr_number}: {error}")
        return None


def search_user_pull_requests(github_client, username, since_date=None, show_sample=False):
    """
    Search for all pull requests authored by a user using the Search API
    This finds PRs across ALL repositories the user has access to
    
    Args:
        github_client: Authenticated GitHub client
        username: GitHub username
        since_date: Optional ISO date string to filter PRs
        show_sample: Whether to print a sample PR object
    
    Returns:
        List of transformed pull request dictionaries
    """
    try:
        # Build search query
        query = f"author:{username} type:pr"
        
        # Add date filter if provided
        if since_date:
            date_str = since_date.split("T")[0]  # Get just the date part
            query += f" created:>={date_str}"
        
        print(f"\n🔍 Searching PRs with query: \"{query}\"")
        
        # Search API returns max 1000 results
        search_results = github_client.search_issues(query, sort="created", order="desc")
        
        prs = []
        count = 0
        for issue in search_results:
            if issue.pull_request:  # Ensure it's a PR
                # Extract owner/repo from URL
                match = re.match(r".*/([^/]+)/([^/]+)/pull/(\d+)", issue.html_url)
                if not match:
                    print(f"  Warning: Could not parse PR URL: {issue.html_url}")
                    continue
                
                owner, repo, pr_number = match.groups()
                
                # Fetch full PR details
                full_pr = fetch_pull_request_details(github_client, owner, repo, int(pr_number))
                
                if full_pr:
                    prs.append(transform_pull_request(full_pr))
                else:
                    # Fall back to issue if details fetch fails
                    # Note: This won't have all PR-specific fields
                    prs.append({
                        "type": "pull-request",
                        "number": issue.number,
                        "sha": "",
                        "short_sha": f"pr-{issue.number}",
                        "title": issue.title.replace("\n", " ").replace("\r", " ").strip(),
                        "state": issue.state,
                        "created_at": issue.created_at.isoformat() + "Z" if issue.created_at else "",
                        "merged_at": "",
                        "closed_at": issue.closed_at.isoformat() + "Z" if issue.closed_at else "",
                        "author_name": issue.user.login if issue.user else "",
                        "author_date": issue.created_at.isoformat() + "Z" if issue.created_at else "",
                        "repo": f"{owner}/{repo}",
                        "repo_owner": owner,
                        "repo_name": repo,
                        "url": issue.html_url,
                        "api_url": issue.url,
                        "node_id": issue.node_id,
                        "merged": False,
                        "draft": False,
                        "head_sha": "",
                        "merge_commit_sha": "",
                    })
                
                count += 1
                if count % 10 == 0:
                    print(f"  Processed {count} PRs...", end="\r")
        
        print(f"\n📊 Found {len(prs)} total PRs")
        
        if prs and show_sample:
            import json
            print("\n=== Sample Pull Request Object Shape ===")
            print(json.dumps(prs[0], indent=2, default=str))
            print("========================================\n")
        
        return prs
    except Exception as error:
        print(f"Error searching PRs for {username}: {error}")
        return []


def fetch_pull_requests(github_client, owner, repo, username, since_date=None, show_sample=False):
    """
    Fetch pull requests from a specific repository (legacy method)
    Kept for backwards compatibility
    """
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        
        prs = []
        for pr in repository.get_pulls(state="all", sort="created", direction="desc"):
            # Filter PRs by the authenticated user
            if pr.user and pr.user.login == username:
                # Filter by date if provided
                if since_date:
                    since = datetime.fromisoformat(since_date.replace("Z", "+00:00"))
                    if pr.created_at and pr.created_at < since:
                        continue
                
                prs.append(transform_pull_request(pr))
        
        # Log first PR to see the shape (only once)
        if prs and show_sample:
            import json
            print("\n=== Sample Pull Request Object Shape ===")
            print(json.dumps(prs[0], indent=2, default=str))
            print("========================================\n")
        
        return prs
    except Exception as error:
        print(f"Error fetching PRs for {owner}/{repo}: {error}")
        return []

