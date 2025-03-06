from pydriller import Repository
import pydriller
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

def analyze_repositories(repo_paths, csv_file_path):
    all_data = []

    for repo_path in repo_paths:
        print(f"------------------- Currently parsing through {repo_path} -------------------")
        authors_to_churn = {}
        commit_regular, commit_late = 0, 0

        try:
            for commit in Repository(repo_path).traverse_commits():
                project_name = commit.project_name
                author_name = commit.author.name
                commit_date = commit.committer_date
                commit_message = commit.msg
                churn = commit.insertions - commit.deletions
                timezone_offset = commit.committer_timezone
                local_timezone = timezone(timedelta(seconds=timezone_offset))
                local_commit_time = commit_date.astimezone(local_timezone)

                # Calculate average cyclomatic complexity per commit
                total_complexity = 0
                modified_files = 0
                for mod in commit.modified_files:
                    if mod.complexity is not None:
                        total_complexity += mod.complexity
                        modified_files += 1
                avg_complexity = total_complexity / modified_files if modified_files > 0 else 0

                # Track code churn per author
                if author_name not in authors_to_churn:
                    authors_to_churn[author_name] = churn
                else:
                    authors_to_churn[author_name] += churn

                # Collect commit data
                all_data.append([
                    project_name, author_name, commit_date, commit_message,
                    repo_path, churn, local_commit_time, avg_complexity
                ])
        except Exception as e:
            print(f"Error processing repository {repo_path}: {e}")

    # Create DataFrame
    df = pd.DataFrame(all_data, columns=[
        "Project_Name", "Author", "Commit_Date", "Message", "Repo_Path",
        "Code_Churn", "Local_Commit_Time", "Avg_Complexity"
    ])

    if df.empty:
        print("No commit data found in the provided repositories.")
        return

    df['Commit_Date'] = pd.to_datetime(df['Commit_Date'], utc=True)

    # Calculate Project Age (in years)
    for project_name in df['Project_Name'].unique():
        project_df = df[df['Project_Name'] == project_name]
        first_commit = project_df['Commit_Date'].min()
        last_commit = project_df['Commit_Date'].max()
        project_age = (last_commit - first_commit).days / 365.25
        df.loc[df['Project_Name'] == project_name, 'Project_Age_(Years)'] = project_age

    # Calculate Total Commits per Author within each project
    project_author_commits = df.groupby(['Project_Name', 'Author']).size().reset_index(name='Total_Commits')
    df = pd.merge(df, project_author_commits, on=['Project_Name', 'Author'], how='left')

    # Save to CSV (append if exists)
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

    print(f"Data saved to {csv_file_path}")


if __name__ == "__main__":
    repo_paths = [
        "https://github.com/activist-org/activist",

    ]
    analyze_repositories(repo_paths, "repos_mined.csv")
