"""Service for fetching contributions from GitHub"""
import time
from ..api.repositories import fetch_user_repos
from ..api.commits import fetch_commits
from ..api.pull_requests import search_user_pull_requests
from ..api.code_reviews import search_user_code_reviews


def process_repositories(
    github_client,
    username,
    affiliation,
    since_date=None,
    fetch_commits_flag=True,
    fetch_prs_flag=False,
    fetch_code_reviews_flag=False
):
    """
    Process all repositories and collect commits
    PRs and code reviews are fetched separately using the Search API
    
    Args:
        github_client: Authenticated GitHub client
        username: GitHub username
        affiliation: Repository affiliation filter
        since_date: Optional date filter
        fetch_commits_flag: Whether to fetch commits
        fetch_prs_flag: Whether to fetch pull requests
        fetch_code_reviews_flag: Whether to fetch code reviews
    
    Returns:
        Dictionary with commits, pullRequests, codeReviews, and stats
    """
    all_commits = []
    all_pull_requests = []
    all_code_reviews = []
    repos_with_commits = 0
    total_repos_processed = 0
    start_time = time.time()
    
    # Fetch commits by iterating through repos (if enabled)
    if fetch_commits_flag:
        # Get user's repos
        print("🔍 Fetching repositories... ", end="", flush=True)
        repo_start_time = time.time()
        repos = fetch_user_repos(github_client, affiliation)
        fetch_time = f"{(time.time() - repo_start_time):.2f}"
        print(f"✓ Found {len(repos)} repositories ({fetch_time}s)\n")
        
        # Process repositories with progress
        for i, repo in enumerate(repos, 1):
            current = i
            total = len(repos)
            percentage = f"{(current / total * 100):.1f}"
            
            print(
                f"[{current}/{total}] ({percentage}%) Processing: {repo['owner']}/{repo['name']} "
                f"{'(private)' if repo['private'] else ''}... ",
                end="",
                flush=True
            )
            
            repo_process_start_time = time.time()
            show_sample = i == 1
            
            commits = fetch_commits(
                github_client,
                repo["owner"],
                repo["name"],
                username,
                since_date,
                show_sample
            )
            
            repo_time = f"{(time.time() - repo_process_start_time):.2f}"
            
            if commits:
                repos_with_commits += 1
                print(f"✓ {len(commits)} commits ({repo_time}s)")
            else:
                print(f"✓ 0 commits ({repo_time}s)")
            
            all_commits.extend(commits)
            total_repos_processed += 1
    
    # Fetch PRs using the Search API (if enabled)
    # This finds PRs across ALL repos, not just the user's repo list
    if fetch_prs_flag:
        prs = search_user_pull_requests(github_client, username, since_date, False)
        all_pull_requests.extend(prs)
    
    # Fetch code reviews using the Search API (if enabled)
    # This finds reviews across ALL repos, not just the user's repo list
    if fetch_code_reviews_flag:
        reviews = search_user_code_reviews(github_client, username, since_date, False)
        all_code_reviews.extend(reviews)
    
    return {
        "commits": all_commits,
        "pullRequests": all_pull_requests,
        "codeReviews": all_code_reviews,
        "stats": {
            "totalReposProcessed": total_repos_processed,
            "reposWithCommits": repos_with_commits,
            "reposWithPRs": 1 if all_pull_requests else 0,  # Simplified since we use search
            "reposWithReviews": 1 if all_code_reviews else 0,  # Simplified since we use search
            "startTime": start_time,
        },
    }

