import os
import csv
import re
import time
import hashlib
from datetime import datetime
from pydriller import Repository

REPOS = [
    'https://github.com/activist-org/activist',
    'https://github.com/ansible/ansible',
    'https://github.com/arviz-devs/arviz',
    'https://github.com/bokeh/bokeh',
    'https://github.com/borgbackup/borg',
    'https://github.com/CiviWiki/OpenCiviWiki',
    'https://github.com/hpcaitech/ColossalAI',
    'https://github.com/cookiecutter/cookiecutter-django',
    'https://github.com/mem0ai/mem0',
    'https://github.com/fastapi/fastapi'
]

OUTPUT_CSV = 'performance_metrics.csv'

def local_repo_path(repo_url: str) -> str:
    repo_hash = hashlib.md5(repo_url.encode('utf-8')).hexdigest()
    return os.path.join('repos', repo_hash)

def is_bug_fix_commit(message: str) -> bool:
    bug_keywords = re.compile(r'\b(fix(e[ds])?|bugs?|issue\s?#\d+)\b', re.IGNORECASE)
    return bool(bug_keywords.search(message))

def is_revert_commit(message: str) -> bool:
    revert_keywords = re.compile(r'\brevert\b', re.IGNORECASE)
    return bool(revert_keywords.search(message))

def mine_repo_commits(repo_url: str):
    """
    Generator that yields commit data from the given repo_url.
    This function does the actual PyDriller call.
    """
    repo_local_path = local_repo_path(repo_url)
    os.makedirs(repo_local_path, exist_ok=True)

    # Example: no 'since' date => full commit history
    for commit in Repository(repo_url, clone_repo_to=repo_local_path, since=datetime(2024, 1, 1)).traverse_commits():
        code_churn = commit.insertions + commit.deletions
        commit_message = commit.msg.lower() if commit.msg else ""

        yield {
            'repo_url': repo_url,
            'commit_hash': commit.hash,
            'author': commit.author.name,
            'date': commit.committer_date.isoformat(),
            'code_churn': code_churn,
            'is_bug_fix': 1 if is_bug_fix_commit(commit_message) else 0,
            'is_revert': 1 if is_revert_commit(commit_message) else 0
        }

def process_repo_with_retries(repo_url: str, max_attempts=3, wait_seconds=5):
    """
    Tries up to 'max_attempts' times to mine the repo.
    If it still fails, we'll skip it (or you can handle differently).
    """
    for attempt in range(1, max_attempts+1):
        try:
            # If the mining succeeds, we yield all commits and return
            for commit_data in mine_repo_commits(repo_url):
                yield commit_data
            return  # success => exit the function
        except Exception as e:
            print(f"Attempt {attempt} failed for {repo_url} with error:\n{e}")
            if attempt < max_attempts:
                print(f"Retrying in {wait_seconds} seconds...\n")
                time.sleep(wait_seconds)
            else:
                print(f"All {max_attempts} attempts failed for {repo_url}. Skipping.\n")
                return  # or raise if you prefer

def main():
    os.makedirs('repos', exist_ok=True)

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'repo_url',
            'commit_hash',
            'author',
            'date',
            'code_churn',
            'is_bug_fix',
            'is_revert'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for repo_url in REPOS:
            print(f"Processing: {repo_url}")
            for commit_info in process_repo_with_retries(repo_url):
                writer.writerow(commit_info)

    print(f"\nDone! Results saved in {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
