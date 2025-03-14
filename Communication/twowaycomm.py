import pandas as pd
from pydriller import Repository
import os

# Repository URL
REPO_URL = "https://github.com/MunGell/awesome-for-beginners.git"

# Output CSV files
COMMUNICATION_CSV = "communication_events.csv"
COMMITS_DATA_CSV = "commits_data.csv"

def mine_repository():
    """Mine the repository for all commits and export to CSV."""
    print(f"Mining repository: {REPO_URL}")

    # Initialize Repository object without time constraints
    repo = Repository(REPO_URL)

    # Collect commit data
    commits_data = []
    commit_count = 0
    for commit in repo.traverse_commits():
        commit_count += 1
        if commit_count % 1000 == 0:  # Progress update every 1000 commits
            print(f"Processed {commit_count} commits")
        for mod in commit.modified_files:
            file_path = mod.new_path if mod.new_path else mod.old_path
            if file_path:  # Ensure file path exists
                commits_data.append({
                    "author": commit.author.name,
                    "timestamp": commit.committer_date,
                    "file": file_path
                })

    # Create a DataFrame from the collected data
    df = pd.DataFrame(commits_data)
    # Save the raw commits data to CSV
    df.to_csv(COMMITS_DATA_CSV, index=False)
    print(f"Saved {len(commits_data)} commit records to {COMMITS_DATA_CSV}")

    # Calculate total authors and top contributors
    author_stats = df['author'].value_counts()
    total_authors = len(author_stats)
    top_10_contributors = author_stats.head(10)

    # Print author statistics
    print(f"\nTotal number of unique authors: {total_authors}")
    print("\nTop 10 contributors by commit count:")
    print("----------------------------------------")
    for author, count in top_10_contributors.items():
        print(f"{author}: {count} commits")
    print("----------------------------------------")

    # Step 5: Identify Communication Blocks
    # Sort by file and timestamp
    df = df.sort_values(["file", "timestamp"])

    # Add shifted columns to compare with previous commit per file
    df["prev_timestamp"] = df.groupby("file")["timestamp"].shift(1)
    df["prev_author"] = df.groupby("file")["author"].shift(1)

    # Define the time window (e.g., 24 hours)
    time_window = pd.Timedelta(hours=24)

    # Filter for communication events
    comm_events = df[
        (df["timestamp"] - df["prev_timestamp"] <= time_window) &
        (df["author"] != df["prev_author"]) &
        df["prev_timestamp"].notna()
    ]

    # Prepare the communication events DataFrame
    comm_events = comm_events[["file", "prev_author", "author", "prev_timestamp", "timestamp"]].rename(columns={
        "prev_author": "author1",
        "author": "author2",
        "prev_timestamp": "time1",
        "timestamp": "time2"
    })

    # Save to CSV
    comm_events.to_csv(COMMUNICATION_CSV, index=False)

    # Output summary
    print(f"Found {len(comm_events)} communication events.")
    print(f"Data saved to {COMMUNICATION_CSV}")
    if not comm_events.empty:
        print("\nSample of communication events:")
        print(comm_events.head())

    # Custom summary: Number of communication events per author pair
    print("\nTop 10 author pairs by communication events:")
    print("----------------------------------------")
    author_pairs = comm_events.groupby(['author1', 'author2']).size().sort_values(ascending=False).head(10)
    for (author1, author2), count in author_pairs.items():
        print(f"{author1} -> {author2}: {count} events")
    print("----------------------------------------")

if __name__ == "__main__":
    try:
        mine_repository()
    except Exception as e:
        print(f"Error occurred: {e}")
