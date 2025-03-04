from pydriller import Repository
import pydriller
import pydriller
from pydriller.metrics.process.code_churn import CodeChurn
import csv
import pandas as pd
from datetime import datetime
import os

def calculate_commit_code_churn(commits):
    """Loops over commits and calculates the code churn of the entire
    list of commits.

    Args:
        commits: a list of commits for which to calculate the total code churn

    Returns:
        code_churn: A single integer value representing the code churn for all commits
    """
    code_churn = 0
    for commit in commits:
        try:
            code_churn = code_churn + commit.insertions - commit.deletions
        except Exception as e:
            print(f"Error processing commit {commit}: {e}")
    
    return code_churn

def get_code_churn_and_save_to_csv(repo_paths, csv_file_path):

    code_churn_data = []
    for repo_path in repo_paths:

        print(f"------------------- Currently parsing through {repo_path} -------------------")
        authors_to_churn = {}
        for commit in pydriller.Repository(repo_path).traverse_commits():
            if commit.author.name not in authors_to_churn.keys():
                authors_to_churn[commit.author.name] = [commit.project_name, commit.insertions - commit.deletions, repo_path]
            else:
                val = authors_to_churn[commit.author.name][1]
                authors_to_churn[commit.author.name][1] = val + commit.insertions - commit.deletions


        for auth in authors_to_churn.keys():
            code_churn_data.append([authors_to_churn[auth][0],auth,authors_to_churn[auth][1],authors_to_churn[auth][2]])

        
        #except Exception as e:
        #    print(f"Error processing repository {repo_path}: {e}")

    df = pd.DataFrame(code_churn_data, columns=["Project Name", "Author", "Code Churn", "Repo Path"])

    # Save to CSV (append if the file exists)
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

    print(f"Commit data saved to {csv_file_path}")

def get_commits_and_save_to_csv(repo_paths, csv_file_path):
    """Retrieves commits from multiple repositories, calculates project age,
    and saves to a single CSV.

    Args:
        repo_paths: A list of repository paths (strings).
        csv_file_path: The path to the output CSV file.
    """

    all_commits_data = []

    for repo_path in repo_paths:
        print(f"------------------- Currently parsing through {repo_path} -------------------")
        try:
            for commit in pydriller.Repository(repo_path).traverse_commits():
                all_commits_data.append([
                    commit.project_name,  # Include project name
                    commit.author.name,
                    commit.committer_date,
                    commit.msg,
                    repo_path # Add repo path for clarity
                ])
        except Exception as e:
            print(f"Error processing repository {repo_path}: {e}")

    df = pd.DataFrame(all_commits_data, columns=["Project Name", "Author", "Date", "Message", "Repo Path"])

    if df.empty:
        print("No commit data found in the provided repositories.")
        return

    df['Date'] = pd.to_datetime(df['Date'], utc=True)

    # Calculate Project Age (per project and overall)
    for project_name in df['Project Name'].unique():
        project_df = df[df['Project Name'] == project_name]
        first_commit_date = project_df['Date'].min()
        last_commit_date = project_df['Date'].max()
        project_age_days = (last_commit_date - first_commit_date).days
        project_age_years = project_age_days / 365.25
        df.loc[df['Project Name'] == project_name, 'Project Age (Years)'] = project_age_years




    # Calculate Total Commits per Author within each project
    project_author_commits = df.groupby(['Project Name', 'Author']).size().reset_index(name='Total Commits')
    df = pd.merge(df, project_author_commits, on=['Project Name', 'Author'], how='left')


    # Save to CSV (append if the file exists)
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

    print(f"Commit data saved to {csv_file_path}")


def get_committer_timezone_info(repo_path):
    """
    Analyzes a Git repository and prints committer timezone information.

    Args:
        repo_path: The path to the Git repository.
    """
    commit_regular = 0
    commit_late = 0
    for commit in Repository(repo_path).traverse_commits():
        # Get committer date (timezone-aware, in UTC)

        committer_date_utc = commit.committer_date

        # Get committer timezone offset in seconds
        committer_timezone_offset = commit.committer_timezone

        # Create a timezone object representing the committer's timezone
        committer_timezone = datetime.timezone(datetime.timedelta(seconds=committer_timezone_offset))

        # Convert the committer date to the committer's timezone
        committer_date_local = committer_date_utc.astimezone(committer_timezone)

        print(f"Commit: {commit.hash}")
        print(f"  Committer: {commit.committer.name} <{commit.committer.email}>")
        print(f"  Committer Date (UTC): {committer_date_utc}")
        print(f"  Committer Timezone Offset: {committer_timezone_offset} seconds")
        print(f"  Committer Timezone: {committer_timezone}")
        print(f"  Committer Date (Local): {committer_date_local}")  # In their local timezone
        print("-" * 40)
        commit_regular += 1
        if 1 <= committer_date_local.hour <= 4:
            commit_late += 1
    print(f"Regular Commits: {commit_regular}\nLate Commits: {commit_late}")





if __name__ == "__main__":

    repo_path = [
"https://github.com/activist-org/activist",
#"https://github.com/ansible/ansible",
#"https://github.com/arviz-devs/arviz",
#"https://github.com/bokeh/bokeh",
#"https://github.com/borgbackup/borg",
#"https://github.com/CiviWiki/OpenCiviWiki",
#"https://github.com/hpcaitech/ColossalAI",
#"https://github.com/cookiecutter/cookiecutter-django",
#"https://github.com/mem0ai/mem0",
#"https://github.com/fastapi/fastapi",
#"https://github.com/h2oai/wave",
#"https://github.com/h2oai/wave-apps",
#"https://github.com/harmonydata/harmony",
#"https://github.com/sukeesh/Jarvis",
#"https://github.com/jupyter/notebook",
#"https://github.com/Kinto/kinto",
#"https://github.com/matplotlib/matplotlib",
#"https://github.com/mindsdb/mindsdb",
#"https://github.com/mitmproxy/mitmproxy",
#"https://github.com/gpodder/mygpo"
]

    #repo_path = ["https://github.com/Eissayou/CatDetector", "https://github.com/aj-avendano/Melody-Project"]
    #get_committer_timezone_info(repo_path)
    get_code_churn_and_save_to_csv(repo_path, "CodeChurn.csv")
