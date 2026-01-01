"""Configuration constants"""

# CSV column headers for commit data
COMMIT_CSV_HEADERS = [
    "type",
    "sha",
    "short_sha",
    "message",
    "message_first_line",
    "author_name",
    "author_email",
    "author_date",
    "committer_name",
    "committer_email",
    "committer_date",
    "repo",
    "repo_owner",
    "repo_name",
    "url",
    "api_url",
    "node_id",
    "parents",
    "stats_additions",
    "stats_deletions",
    "stats_total",
    "files_changed",
    "verification_verified",
    "verification_reason",
]

# CSV column headers for pull request data
# Note: body field is excluded to avoid multi-line CSV parsing issues
PULL_REQUEST_CSV_HEADERS = [
    "type",
    "number",
    "sha",
    "short_sha",
    "title",
    "state",
    "created_at",
    "merged_at",
    "closed_at",
    "author_name",
    "author_date",
    "repo",
    "repo_owner",
    "repo_name",
    "url",
    "api_url",
    "node_id",
    "merged",
    "draft",
    "head_sha",
    "merge_commit_sha",
]

# CSV column headers for code review data
# Note: review_body field is sanitized to single line to avoid multi-line CSV parsing issues
CODE_REVIEW_CSV_HEADERS = [
    "type",
    "review_id",
    "state",
    "submitted_at",
    "pr_number",
    "pr_title",
    "repo",
    "repo_owner",
    "repo_name",
    "reviewer_name",
    "review_body",
    "pr_url",
    "review_url",
    "commit_id",
]

# Default repository affiliation filter
DEFAULT_AFFILIATION = "owner,collaborator,organization_member"

