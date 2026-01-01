# Unified Contributions (Unicon)

A Python CLI tool for fetching and importing GitHub contributions to maintain a unified contribution history across multiple accounts and platforms.

## Purpose

Many developers contribute to private/internal GitHub repositories that don't show up on their public profile and/or are unable to showcase their commits in an anonymous way. This tool provides a way to:

- **Preserve contribution history** from private/internal accounts
- **Display accurate activity** on your public GitHub profile heatmap
- **Organize contributions** by project and date

## Features

- ✅ **Automated Fetching** - Fetch commits, pull requests, and code reviews from GitHub API
- ✅ **CSV Export** - Export contributions to CSV for processing
- ✅ **Automated Import** - Import CSV to markdown files automatically
- ✅ **Interactive CLI** - User-friendly command-line interface
- ✅ **Date Filtering** - Filter contributions by date range
- ✅ **Repository Filtering** - Filter by affiliation (owner, collaborator, organization_member)
- ✅ **Git Integration** - Commit contributions with original timestamps
- ✅ **NDA Compliant** - Anonymous markdown files (no repo names or commit messages)

## Installation

### Prerequisites

- Python 3.8 or higher (Python 3.14 recommended)
- Git installed and configured
- GitHub Personal Access Token

### Setup

1. **Clone or download this repository**

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Or install as a package:

   ```bash
   pip install -e .
   ```

3. **Create `.env` file**

   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your GitHub credentials:

   ```env
   GITHUB_TOKEN=your_github_token_here
   GITHUB_USERNAME=your_username_here
   GITHUB_API_URL=https://api.github.com  # Optional, for GitHub Enterprise
   ```

   **Getting a GitHub Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (for private repos) and `read:user`
   - Copy the token to your `.env` file

## Usage

### Interactive Mode

Run the CLI without arguments for an interactive menu:

```bash
python -m cli
```

Or if installed as a package:

```bash
unicon
```

Or run directly:

```bash
python cli.py
```

### Command-Line Mode

You can also run specific operations directly:

#### Fetch Contributions

```bash
# Fetch all commits (interactive prompts)
python -m cli fetch

# Fetch with date filter
python -m cli fetch 2024-01-01T00:00:00Z

# Fetch with affiliation filter
python -m cli fetch 2024-01-01T00:00:00Z owner,collaborator

# Fetch specific types
python -m cli fetch 2024-01-01T00:00:00Z owner,collaborator commits,prs,reviews

# Fetch all types
python -m cli fetch 2024-01-01T00:00:00Z owner,collaborator all
```

**Types:** `commits`, `prs`, `reviews`, `all`, or comma-separated combinations

**Affiliations:** `owner`, `collaborator`, `organization_member`, or comma-separated

#### Import Contributions

```bash
# Import all available CSV files (interactive prompts)
python -m cli import

# Import specific types
python -m cli import commits
python -m cli import commits,prs
python -m cli import all
```

#### Commit to Git

```bash
# Commit all contributions with original timestamps (interactive prompts)
python -m cli commit
```

#### Combined Operations

```bash
# Fetch and import in one go
python -m cli both

# Full workflow: fetch → import → commit
python -m cli full
```

## Workflow

### 1. Fetch Contributions from GitHub

```bash
python -m cli fetch
```

This will:
- Fetch commits, pull requests, and/or code reviews from all accessible repositories
- Export them to CSV files in `exports/` directory
- Support filtering by date and repository affiliation

### 2. Import Contributions to Markdown

```bash
python -m cli import
```

This will:
- Read CSV files from `exports/` directory
- Create markdown files in `contributions/commits/`, `contributions/pull-requests/`, and/or `contributions/code-reviews/`
- Use anonymous format (date, SHA, author only - NDA compliant)
- Delete CSV files after successful import

### 3. Commit with Original Timestamps

```bash
python -m cli commit
```

This will:
- Find all markdown files in the contributions directories
- Commit them to git with their original timestamps
- Maintain accurate contribution dates on your GitHub heatmap

## Project Structure

```
.
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── __init__.py
├── __main__.py
├── cli.py                 # Main CLI entry point
├── api/                   # GitHub API clients
│   ├── github_client.py
│   ├── repositories.py
│   ├── commits.py
│   ├── pull_requests.py
│   └── code_reviews.py
├── services/              # Business logic services
│   ├── fetch_service.py
│   ├── export_service.py
│   ├── import_service.py
│   └── git_commit_service.py
├── cli_components/        # CLI components
│   ├── banner.py
│   ├── prompts.py
│   ├── args.py
│   ├── import_prompts.py
│   └── import_args.py
├── utils/                 # Utility functions
│   ├── validation_utils.py
│   ├── date_utils.py
│   └── csv_utils.py
├── config/                # Configuration
│   └── constants.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── exports/              # CSV export files (gitignored)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with:

- `GITHUB_TOKEN` - Your GitHub Personal Access Token (required)
- `GITHUB_USERNAME` - Your GitHub username (required)
- `GITHUB_API_URL` - GitHub API URL (optional, defaults to public GitHub)

### Date Format

Dates should be in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

Example: `2024-01-01T00:00:00Z`

## Notes

> [!WARNING]  
> At the time of writing this tool, there IS a way to link multiple GitHub accounts (organization and public ones) so that the contributions show up, however for organizational accounts, this feature must be enabled by the organization to work. Additionally, there's also no way to see contributions across different platforms (i.e BitBucket -> GitHub). The aim for this tool is to unify ALL contributions (especially code commits) across all platforms so that we can easily showcase our work activity. This is NOT in any way, shape, or form an attempt to expose/disclose any internal/private information, and is solely for educational and personal showcasing of work activity.

- ⚠️ **Privacy**: Ensure you have permission to export and re-commit work from internal repositories
- ⚠️ **Compliance**: Verify that your company's policies allow this practice
- 📝 **Documentation**: Include enough context in contribution files to understand what was done without violating any NDA/privacy policy.
- 🗓️ **Timestamps**: Use original timestamps when re-committing to maintain accurate contribution dates

## Troubleshooting

### Rate Limiting

If you encounter GitHub API rate limiting:
- The tool includes automatic delays between requests
- For large repositories, consider fetching in smaller date ranges
- GitHub Enterprise instances may have different rate limits

### Missing Contributions

- Ensure your GitHub token has the `repo` scope for private repositories
- Check that the repository affiliation filter includes the correct types
- Verify date filters are not excluding contributions

### Import Errors

- Ensure CSV files exist in the `exports/` directory
- Check that CSV files are not corrupted
- Verify required fields (author_date, short_sha) are present

## License

This repository is for personal use to track and display unified contributions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

