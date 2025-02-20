from pydriller import Repository
import pydriller
import pydriller
import csv
import pandas as pd
from datetime import datetime

def get_commits_and_save_to_csv(repo_path, csv_file_path):
    """Retrieves commits, calculates project age (first to last), and saves to CSV."""

    try:
        commits_data = []

        for commit in pydriller.Repository(repo_path).traverse_commits():
            commits_data.append([
                commit.hash,
                commit.author.name,
                commit.committer_date,
                commit.msg,
            ])

        df = pd.DataFrame(commits_data, columns=["Commit Hash", "Author", "Date", "Message"])

        # 1. Calculate Project Age (First to Last Commit)
        df['Date'] = pd.to_datetime(df['Date'], utc = True)
        first_commit_date = df['Date'].min()
        last_commit_date = df['Date'].max()

        project_age_days = (last_commit_date - first_commit_date).days
        project_age_years = project_age_days / 365.25  # Approximate years

        # 2. Calculate Commits per Author
        commits_per_author = df.groupby('Author').size().reset_index(name='Total Commits')

        df['Project Age (Years)'] = project_age_years
        df = pd.merge(df, commits_per_author, on='Author', how='left')

        df.to_csv(csv_file_path, index=False, encoding='utf-8')

        print(f"Commit data, project age ({project_age_years:.2f} years), and commit counts saved to {csv_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")



def checkNegativeCommitPercentage(csvFile):
    df = pd.read_csv(csvFile)

    negative_commit_percentage = df.groupby('Author')['Sentiment'].apply(lambda x: (x == 'negative').sum() / len(x) * 100).reset_index(name='Negative Commit Percentage')

    df = pd.merge(df, negative_commit_percentage, on='Author', how='left')

    df.to_csv("commit_data_with_negative_percentage.csv", index=False)  # Save to a new CSV




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
    repo_path = "https://github.com/aj-avendano/Melody-Project"
    #get_committer_timezone_info(repo_path)
    get_commits_and_save_to_csv(repo_path, "test.csv")
    checkNegativeCommitPercentage("updated_test.csv")
