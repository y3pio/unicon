"""Main CLI entry point"""
import sys
import time
import questionary
from .api.github_client import create_github_client, get_github_username
from .utils.validation_utils import validate_environment
from cli_components.banner import display_banner
from cli_components.prompts import prompt_user
from cli_components.args import parse_args
from cli_components.import_prompts import prompt_import_options
from cli_components.import_args import parse_import_args
from .services.fetch_service import process_repositories
from .services.export_service import export_to_csv
from .services.import_service import import_contributions
from .services.git_commit_service import commit_contributions


def display_fetch_config(username, since_date, affiliation, fetch_commits, fetch_pull_requests, fetch_code_reviews):
    """Display configuration summary for fetch"""
    print("\n" + "─" * 60)
    print("📋 Configuration:")
    print(f"   User: {username}")
    fetch_types = []
    if fetch_commits:
        fetch_types.append("Commits")
    if fetch_pull_requests:
        fetch_types.append("Pull Requests")
    if fetch_code_reviews:
        fetch_types.append("Code Reviews")
    print(f"   Fetching: {', '.join(fetch_types)}")
    if since_date:
        print(f"   Date filter: {since_date}")
    print(f"   Repository affiliation: {affiliation}")
    print("─" * 60 + "\n")


def display_fetch_summary(stats, affiliation, since_date, fetch_commits, fetch_pull_requests, fetch_code_reviews):
    """Display summary statistics for fetch"""
    print(f"\n{'═' * 60}")
    print("📊 Summary:")
    print(f"   Repositories processed: {stats['totalReposProcessed']}")
    if fetch_commits:
        print(f"   Repositories with commits: {stats['reposWithCommits']}")
        print(f"   Total commits found: {len(stats['commits'])}")
    if fetch_pull_requests:
        print(f"   Repositories with PRs: {stats['reposWithPRs']}")
        print(f"   Total pull requests found: {len(stats['pullRequests'])}")
    if fetch_code_reviews:
        print(f"   Repositories with reviews: {stats['reposWithReviews']}")
        print(f"   Total code reviews found: {len(stats['codeReviews'])}")
    print(f"   Affiliation filter: {affiliation}")
    if since_date:
        print(f"   Filtered since: {since_date}")


def display_fetch_completion(total_time, output_paths):
    """Display completion message for fetch"""
    print(f"\n{'═' * 60}")
    print("✅ Fetch Complete!")
    print(f"   Total time: {total_time}s")
    if output_paths:
        print("   CSV files saved:")
        for path in output_paths:
            print(f"     - {path}")
    else:
        print("   No data to export")
    print(f"{'═' * 60}\n")


def display_import_config(import_commits, import_pull_requests, import_code_reviews):
    """Display configuration summary for import"""
    print("\n" + "─" * 60)
    print("📋 Configuration:")
    import_types = []
    if import_commits:
        import_types.append("Commits")
    if import_pull_requests:
        import_types.append("Pull Requests")
    if import_code_reviews:
        import_types.append("Code Reviews")
    print(f"   Importing: {', '.join(import_types)}")
    print("─" * 60 + "\n")


def display_import_summary(results):
    """Display import summary"""
    print(f"{'═' * 60}")
    print("✅ Import Complete!")
    print(f"{'═' * 60}")
    
    if results.get("commits"):
        print("\n📝 Commits:")
        print(f"   Imported: {results['commits']['imported']}")
        print(f"   Skipped: {results['commits']['skipped']}")
        if results["commits"]["discarded"] > 0:
            print(f"   Discarded: {results['commits']['discarded']}")
    
    if results.get("pullRequests"):
        print("\n📝 Pull Requests:")
        print(f"   Imported: {results['pullRequests']['imported']}")
        print(f"   Skipped: {results['pullRequests']['skipped']}")
        if results["pullRequests"]["discarded"] > 0:
            print(f"   Discarded: {results['pullRequests']['discarded']}")
    
    if results.get("codeReviews"):
        print("\n📝 Code Reviews:")
        print(f"   Imported: {results['codeReviews']['imported']}")
        print(f"   Skipped: {results['codeReviews']['skipped']}")
        if results["codeReviews"]["discarded"] > 0:
            print(f"   Discarded: {results['codeReviews']['discarded']}")
    
    if not results.get("commits") and not results.get("pullRequests") and not results.get("codeReviews"):
        print("\n⚠️  No contributions were imported")
    
    print()


def handle_fetch():
    """Handle fetch operation"""
    try:
        validate_environment()
    except ValueError as error:
        print(f"❌ Error: {error}")
        return False
    
    username = get_github_username()
    github_client = create_github_client()
    
    # Parse arguments or prompt user
    args = parse_args()
    since_date = args["sinceDate"]
    affiliation = args["affiliation"]
    fetch_commits = args["fetchCommits"]
    fetch_pull_requests = args["fetchPullRequests"]
    fetch_code_reviews = args["fetchCodeReviews"]
    
    if not args["hasArgs"]:
        # Interactive mode: prompt user
        try:
            user_input = prompt_user()
            since_date = user_input["sinceDate"]
            affiliation = user_input["affiliation"]
            fetch_commits = user_input["fetchCommits"]
            fetch_pull_requests = user_input["fetchPullRequests"]
            fetch_code_reviews = user_input["fetchCodeReviews"]
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return False
        except Exception as error:
            print(f"❌ Error: {error}")
            return False
    
    # Display configuration
    display_fetch_config(username, since_date, affiliation, fetch_commits, fetch_pull_requests, fetch_code_reviews)
    
    # Process repositories and collect commits/PRs/reviews
    result = process_repositories(
        github_client,
        username,
        affiliation,
        since_date,
        fetch_commits,
        fetch_pull_requests,
        fetch_code_reviews,
    )
    
    commits = result["commits"]
    pull_requests = result["pullRequests"]
    code_reviews = result["codeReviews"]
    stats = result["stats"]
    
    # Display summary
    display_fetch_summary(
        {
            **stats,
            "commits": commits,
            "pullRequests": pull_requests,
            "codeReviews": code_reviews,
        },
        affiliation,
        since_date,
        fetch_commits,
        fetch_pull_requests,
        fetch_code_reviews,
    )
    
    # Export to CSV
    output_paths = export_to_csv(commits, pull_requests, code_reviews)
    
    # Display completion
    total_time = f"{(time.time() - stats['startTime']):.2f}"
    display_fetch_completion(total_time, output_paths)
    
    return True


def handle_import():
    """Handle import operation"""
    # Parse arguments or prompt user
    try:
        args = parse_import_args()
    except SystemExit:
        return False
    
    import_commits = args["importCommits"]
    import_pull_requests = args["importPullRequests"]
    import_code_reviews = args["importCodeReviews"]
    
    if not args["hasArgs"]:
        # Interactive mode: prompt user
        try:
            user_input = prompt_import_options()
            import_commits = user_input["importCommits"]
            import_pull_requests = user_input["importPullRequests"]
            import_code_reviews = user_input["importCodeReviews"]
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return False
        except Exception as error:
            print(f"❌ Error: {error}")
            return False
    
    # Display configuration
    display_import_config(import_commits, import_pull_requests, import_code_reviews)
    
    # Import contributions
    try:
        results = import_contributions(import_commits, import_pull_requests, import_code_reviews)
        display_import_summary(results)
        return True
    except Exception as error:
        print(f"❌ Error: {error}")
        return False


def handle_commit():
    """Handle git commit operation"""
    try:
        commit_types = questionary.checkbox(
            "Which contributions would you like to commit?",
            choices=[
                {"name": "Commits", "value": "commits", "checked": True},
                {"name": "Pull Requests", "value": "pullRequests", "checked": True},
                {"name": "Code Reviews", "value": "codeReviews", "checked": True},
            ],
            validate=lambda x: len(x) > 0 or "Please select at least one option",
        ).ask()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return False
    
    commit_types_dict = {
        "commits": "commits" in commit_types,
        "pullRequests": "pullRequests" in commit_types,
        "codeReviews": "codeReviews" in commit_types,
    }
    
    try:
        commit_contributions(commit_types_dict)
        return True
    except Exception as error:
        print(f"❌ Error: {error}")
        return False


def prompt_operation():
    """Prompt user for operation selection"""
    operation = questionary.select(
        "What would you like to do?",
        choices=[
            {"name": "Fetch contributions from GitHub", "value": "fetch"},
            {"name": "Import contributions from CSV", "value": "import"},
            {"name": "Commit contributions to git", "value": "commit"},
            {"name": "Fetch and then import", "value": "both"},
            {"name": "Full workflow (fetch → import → commit)", "value": "full"},
        ],
    ).ask()
    
    return operation


def main():
    """Main function"""
    operation_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    operation = operation_arg
    
    if not operation:
        # Interactive mode: show banner and prompt user
        display_banner()
        try:
            operation = prompt_operation()
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            sys.exit(1)
        except Exception as error:
            print(f"❌ Error: {error}")
            print("Usage: python -m cli [fetch|import|commit|both|full]")
            sys.exit(1)
    else:
        # Validate operation
        valid_operations = ["fetch", "import", "commit", "both", "full"]
        if operation.lower() not in valid_operations:
            print(f"❌ Error: Invalid operation \"{operation}\"")
            print("Usage: python -m cli [fetch|import|commit|both|full]")
            print("Valid operations: fetch, import, commit, both, full")
            sys.exit(1)
        operation = operation.lower()
    
    success = True
    
    if operation == "fetch" or operation == "both":
        success = handle_fetch()
        if not success:
            sys.exit(1)
    
    if operation == "import" or operation == "both" or operation == "full":
        if operation == "both" or operation == "full":
            print("\n" + "=" * 60)
            print("Proceeding to import...")
            print("=" * 60 + "\n")
        success = handle_import()
        if not success:
            sys.exit(1)
    
    if operation == "commit" or operation == "full":
        if operation == "full":
            print("\n" + "=" * 60)
            print("Proceeding to commit...")
            print("=" * 60 + "\n")
        success = handle_commit()
        if not success:
            sys.exit(1)
    
    if (operation == "both" or operation == "full") and success:
        print(f"{'═' * 60}")
        print("✅ All operations complete!")
        print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()

