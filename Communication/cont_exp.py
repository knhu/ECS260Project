from pydriller import Repository
from collections import defaultdict
import os
import csv

# Repository URL
REPO_URL = "https://github.com/zsh-users/zsh.git"

# Output CSV files
TIMEZONE_CSV = "committer_timezones.csv"
CONTRIBUTORS_EXPERIENCE_CSV = "contributors_experience.csv"
SUMMARY_CSV = "summary.csv"  # New summary file

# Data storage
committer_timezones = defaultdict(int)  # Timezone frequency
file_contributors = defaultdict(lambda: defaultdict(int))  # File -> Author -> Lines

def calculate_contributors_experience(file_contributors):
    """Calculate Contributors Experience metric: % of lines by top contributor per file."""
    contributors_experience = {}
    for file, authors in file_contributors.items():
        total_lines = sum(authors.values())
        if total_lines > 0:
            top_contributor_lines = max(authors.values())
            contributors_experience[file] = (top_contributor_lines / total_lines) * 100
    return contributors_experience

def save_to_csv(data, filename, headers):
    """Save data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)
    print(f"Data saved to {filename}")

def format_offset(tzinfo):
    """Convert tzoffset object to a readable UTC offset string (e.g., +00:00)."""
    if tzinfo is None:
        return "Unknown"
    offset_seconds = tzinfo._offset.total_seconds()
    hours = int(offset_seconds // 3600)
    minutes = int((offset_seconds % 3600) // 60)
    sign = "+" if hours >= 0 else "-"
    return f"{sign}{abs(hours):02d}:{abs(minutes):02d}"

def mine_repository():
    """Mine the repository for Committer Timezones and Contributors Experience metrics."""
    print(f"Mining repository: {REPO_URL}")

    # Initialize Repository object without time constraints
    repo = Repository(REPO_URL)

    for commit in repo.traverse_commits():
        # Extract and format timezone
        commit_date = commit.committer_date
        timezone = commit_date.tzinfo
        tz_name = format_offset(timezone)
        committer_timezones[tz_name] += 1

        # Process modified files for Contributors Experience
        for mod in commit.modified_files:
            file_path = mod.new_path if mod.new_path else mod.old_path
            if file_path:
                author = commit.author.name
                lines_added = mod.added_lines
                file_contributors[file_path][author] += lines_added

    # Calculate Contributors Experience
    contributors_experience = calculate_contributors_experience(file_contributors)

    # Prepare data for CSV export
    timezone_data = [(tz, count) for tz, count in committer_timezones.items()]
    save_to_csv(timezone_data, TIMEZONE_CSV, ["Timezone", "Commit Count"])

    contributors_data = [(file, percentage) for file, percentage in contributors_experience.items()]
    save_to_csv(contributors_data, CONTRIBUTORS_EXPERIENCE_CSV, ["File", "Top Contributor Share (%)"])

    # Prepare summary data for CSV instead of printing
    summary_data = []

    # Committer Timezone Distribution
    summary_data.append(["Committer Timezone Distribution", ""])
    summary_data.append(["Timezone", "Commits"])
    for tz, count in sorted(committer_timezones.items()):
        summary_data.append([tz, count])

    # Contributors Experience
    summary_data.append(["", ""])  # Empty row for separation
    summary_data.append([f"Contributors Experience (All {len(contributors_experience)} files)", ""])
    summary_data.append(["File", "Top Contributor Share (%)"])
    for file in sorted(contributors_experience.keys()):
        percentage = contributors_experience[file]
        summary_data.append([file, f"{percentage:.2f}"])

    # Summary statistics
    avg_contributors_experience = sum(contributors_experience.values()) / len(contributors_experience) if contributors_experience else 0
    summary_data.append(["", ""])  # Empty row for separation
    summary_data.append(["Average Contributors Experience across files", f"{avg_contributors_experience:.2f}%"])
    summary_data.append(["Total unique timezones", len(committer_timezones)])

    # Save summary to CSV
    save_to_csv(summary_data, SUMMARY_CSV, ["Field", "Value"])

if __name__ == "__main__":
    try:
        mine_repository()
    except Exception as e:
        print(f"Error occurred: {e}")
