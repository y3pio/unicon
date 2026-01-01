"""Code review fetching functions"""
import re
from datetime import datetime


def transform_code_review(review, pr):
    """Transform raw review data to our format"""
    # Extract owner/repo from PR data
    owner = pr.base.repo.owner.login
    repo = pr.base.repo.name
    
    # Sanitize review body to single line
    body = (review.body or "").replace("\n", " ").replace("\r", " ").strip()
    
    return {
        "type": "code-review",
        "review_id": review.id,
        "state": review.state,  # APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED
        "submitted_at": review.submitted_at.isoformat().replace("+00:00", "Z") if review.submitted_at else "",
        "pr_number": pr.number,
        "pr_title": (pr.title or "").replace("\n", " ").replace("\r", " ").strip(),
        "repo": f"{owner}/{repo}",
        "repo_owner": owner,
        "repo_name": repo,
        "reviewer_name": review.user.login if review.user else "",
        "review_body": body,
        "pr_url": pr.html_url,
        "review_url": review.html_url,
        "commit_id": review.commit_id,
    }


def fetch_pull_request_reviews(github_client, owner, repo, pr_number):
    """Fetch reviews for a specific pull request"""
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(pr_number)
        return list(pr.get_reviews())
    except Exception as error:
        print(f"  Warning: Could not fetch reviews for {owner}/{repo}#{pr_number}: {error}")
        return []


def fetch_pull_request_details(github_client, owner, repo, pr_number):
    """Fetch full PR details to get complete information"""
    try:
        repository = github_client.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(pr_number)
        return pr
    except Exception as error:
        print(f"  Warning: Could not fetch details for {owner}/{repo}#{pr_number}: {error}")
        return None


def search_user_code_reviews(github_client, username, since_date=None, show_sample=False):
    """
    Search for all pull requests reviewed by a user using the Search API
    This finds PRs where the user has submitted at least one review.
    
    Args:
        github_client: Authenticated GitHub client
        username: GitHub username
        since_date: Optional ISO date string to filter reviews
        show_sample: Whether to print a sample review object
    
    Returns:
        List of transformed code review dictionaries
    """
    try:
        # Build search query
        query = f"reviewed-by:{username} type:pr"
        
        # Add date filter if provided
        # Note: Search API doesn't support filtering by review date directly
        # We'll filter after fetching
        if since_date:
            date_str = since_date.split("T")[0]
            query += f" created:>={date_str}"
        
        print(f"\n🔍 Searching code reviews with query: \"{query}\"")
        
        # Search API returns max 1000 results
        search_results = github_client.search_issues(query, sort="created", order="desc")
        
        all_reviews = []
        processed = 0
        
        for issue in search_results:
            if not issue.pull_request:
                continue
            
            # Extract owner/repo from URL
            match = re.match(r".*/([^/]+)/([^/]+)/pull/(\d+)", issue.html_url)
            if not match:
                print(f"  Warning: Could not parse PR URL: {issue.html_url}")
                continue
            
            owner, repo, pr_number = match.groups()
            
            # Fetch full PR details for complete information
            full_pr = fetch_pull_request_details(github_client, owner, repo, int(pr_number))
            if not full_pr:
                continue
            
            # Fetch all reviews for this PR
            reviews = fetch_pull_request_reviews(github_client, owner, repo, int(pr_number))
            
            # Filter reviews by the target user and exclude dismissed reviews
            user_reviews = [
                review for review in reviews
                if review.user and review.user.login == username and review.state != "DISMISSED"
            ]
            
            # Apply date filter if provided
            if since_date:
                since = datetime.fromisoformat(since_date.replace("Z", "+00:00"))
                user_reviews = [
                    review for review in user_reviews
                    if review.submitted_at and review.submitted_at >= since
                ]
            
            # Transform and add to results
            for review in user_reviews:
                all_reviews.append(transform_code_review(review, full_pr))
            
            processed += 1
            if processed % 10 == 0:
                print(f"  Processed {processed} PRs...", end="\r")
        
        print(f"\n  Processed {processed} PRs")
        print(f"  Found {len(all_reviews)} total reviews")
        
        if all_reviews and show_sample:
            import json
            print("\n=== Sample Code Review Object Shape ===")
            print(json.dumps(all_reviews[0], indent=2, default=str))
            print("==================================\n")
        
        return all_reviews
    except Exception as error:
        print(f"Error searching code reviews for {username}: {error}")
        return []

