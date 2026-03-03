import requests
from datetime import datetime, timedelta

def fetch_commits(github_username):
    """
    Fetch public commits for the given GitHub username.
    Returns a list of dicts with 'date' (ISO datetime) and 'message'.
    Tries multiple approaches to get commit data.
    """
    # First try: use events API
    commits = _fetch_from_events(github_username)
    if commits:
        return commits
    
    # Second try: use repos API to get commits
    commits = _fetch_from_repos(github_username)
    if commits:
        return commits
    
    raise ValueError("No public commits found for this user.")

def _fetch_from_events(github_username):
    """Fetch commits from public events API"""
    url = f"https://api.github.com/users/{github_username}/events/public"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            raise ValueError("GitHub user not found.")
        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise ValueError("GitHub API rate limit exceeded. Please try again later.")
        response.raise_for_status()
        events = response.json()
    except requests.exceptions.RequestException as e:
        return []

    commits = []
    for event in events:
        if event.get("type") == "PushEvent":
            payload = event.get("payload", {})
            # PushEvent might have commits or just a ref
            if "commits" in payload:
                for commit in payload["commits"]:
                    commits.append({
                        "date": event.get("created_at", ""),
                        "message": commit.get("message", "")
                    })
    return commits

def _fetch_from_repos(github_username):
    """Fallback: fetch user's repos and get commits from each"""
    try:
        # Get user's public repositories
        repos_url = f"https://api.github.com/users/{github_username}/repos?type=public&sort=updated&per_page=5"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(repos_url, headers=headers, timeout=10)
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            return []
        
        commits = []
        # Get commits from the most recently updated repos
        for repo in repos[:3]:
            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits?author={github_username}&per_page=10"
            commits_response = requests.get(commits_url, headers=headers, timeout=10)
            if commits_response.status_code == 200:
                repo_commits = commits_response.json()
                for commit in repo_commits:
                    commits.append({
                        "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                        "message": commit.get("commit", {}).get("message", "")
                    })
        
        return commits
    except Exception:
        return []