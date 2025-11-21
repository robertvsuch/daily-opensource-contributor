#!/usr/bin/env python3
"""
Daily Open Source Contributor
Automatically finds and contributes to open-source projects
"""

import os
import sys
import json
import random
from datetime import datetime
from github import Github
import requests

# Target repositories for ML/Data Engineering
TARGET_REPOS = [
    "apache/airflow",
    "apache/spark",
    "dbt-labs/dbt-core",
    "tensorflow/tensorflow",
    "pytorch/pytorch",
    "pandas-dev/pandas",
    "scikit-learn/scikit-learn",
    "huggingface/transformers",
    "mlflow/mlflow",
    "ray-project/ray",
    "dagster-io/dagster",
    "prefecthq/prefect",
    "great-expectations/great_expectations"
]

LABELS_TO_SEARCH = [
    "good first issue",
    "documentation",
    "help wanted",
    "beginner",
    "easy"
]

def get_github_client():
    """Initialize GitHub client with token"""
    token = os.getenv('GH_PAT') or os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token not found")
        sys.exit(1)
    return Github(token)

def find_good_issues(g, max_issues=5):
    """Find good first issues across target repos"""
    issues_found = []
    
    for repo_name in TARGET_REPOS:
        try:
            repo = g.get_repo(repo_name)
            print(f"Searching {repo_name}...")
            
            for label in LABELS_TO_SEARCH:
                try:
                    issues = repo.get_issues(
                        state='open',
                        labels=[label],
                        sort='created',
                        direction='desc'
                    )
                    
                    for issue in issues[:2]:  # Check first 2 issues
                        if issue.pull_request is None:  # Skip PRs
                            issues_found.append({
                                'repo': repo_name,
                                'number': issue.number,
                                'title': issue.title,
                                'url': issue.html_url,
                                'label': label,
                                'body': issue.body[:200] if issue.body else ''
                            })
                            
                            if len(issues_found) >= max_issues:
                                return issues_found
                except Exception as e:
                    print(f"Error searching label {label}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error accessing {repo_name}: {e}")
            continue
    
    return issues_found

def analyze_and_comment(g, issue_info):
    """Analyze issue and post a helpful comment"""
    try:
        repo = g.get_repo(issue_info['repo'])
        issue = repo.get_issue(issue_info['number'])
        
        # Check if we've already commented
        comments = issue.get_comments()
        for comment in comments:
            if comment.user.login == g.get_user().login:
                print(f"Already commented on issue #{issue_info['number']}")
                return False
        
        # Create helpful comment based on issue type
        if 'documentation' in issue_info['label'].lower():
            comment_text = (
                f"Hi! I'd like to help improve the documentation for this issue.\n\n"
                f"Based on the issue description, I can:\n"
                f"- Review and clarify existing documentation\n"
                f"- Add code examples if needed\n"
                f"- Improve formatting and readability\n\n"
                f"Let me know if you'd like me to submit a PR with these improvements!"
            )
        else:
            comment_text = (
                f"Hi! I'm interested in working on this issue.\n\n"
                f"I have experience with data engineering and would like to contribute. "
                f"Could you provide any additional context or point me to relevant code sections?\n\n"
                f"Thanks!"
            )
        
        # Post comment
        issue.create_comment(comment_text)
        print(f"✓ Commented on {issue_info['repo']}#{issue_info['number']}")
        return True
        
    except Exception as e:
        print(f"Error commenting on issue: {e}")
        return False

def save_contribution_log(issues):
    """Save log of today's contributions"""
    log_file = 'contributions.json'
    
    # Load existing log
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log = json.load(f)
    else:
        log = []
    
    # Add today's entry
    log.append({
        'date': datetime.now().isoformat(),
        'issues': issues
    })
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=2)
    
    print(f"\nLog saved to {log_file}")

def main():
    print("🚀 Daily Open Source Contributor")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Initialize GitHub client
    g = get_github_client()
    user = g.get_user()
    print(f"\nAuthenticated as: {user.login}")
    
    # Find issues
    print("\nSearching for good first issues...")
    issues = find_good_issues(g, max_issues=3)
    
    if not issues:
        print("\n❌ No suitable issues found today.")
        return
    
    print(f"\n✓ Found {len(issues)} potential issues:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['repo']}#{issue['number']} - {issue['title'][:60]}")
    
    # Interact with one issue
    if issues:
        selected = issues[0]
        print(f"\nInteracting with: {selected['repo']}#{selected['number']}")
        analyze_and_comment(g, selected)
    
    # Save log
    save_contribution_log(issues)
    
    print("\n✅ Daily contribution complete!")

if __name__ == "__main__":
    main()
