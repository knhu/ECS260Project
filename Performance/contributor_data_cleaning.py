import pandas as pd
import re
from fuzzywuzzy import fuzz

def clean_contributor_performance(
    input_file="contributor_performance.csv",
    output_file="cleaned_contributor_performance.csv",
    fuzzy_threshold=85
):
    """
    Cleans contributor_performance.csv by:
    1. Removing bot contributors.
    2. De-aliasing contributor names via fuzzy matching (no hard-coded map).
    3. Dropping duplicates so each (contributor, repo) is unique.

    Expects columns:
    [ 'contributor', 'repo', 'total_commits', 'total_prs',
      'avg_pr_merge_time', 'code_churn', 'bug_fix_commits' ]
    """

    # Load dataset
    df = pd.read_csv(input_file)

    # Verify columns
    expected_cols = [
        "contributor", "repo", "total_commits", "total_prs",
        "avg_pr_merge_time", "code_churn", "bug_fix_commits"
    ]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataset.")

    # Convert contributor column to string, replacing NaN with empty string
    df["contributor"] = df["contributor"].fillna("").astype(str)

    # 1. Remove bot contributors
    bot_keywords = ["bot", "ci", "github-actions", "dependabot", "renovate", "auto"]
    def is_bot(name):
        return any(re.search(pattern, name, re.IGNORECASE) for pattern in bot_keywords)
    df = df[~df["contributor"].apply(is_bot)].copy()

    # 2. Fuzzy de-aliasing
    # Collect unique contributor names (strings)
    unique_names = df["contributor"].unique().tolist()
    name_groups = []

    for name in unique_names:
        # Safely strip whitespace
        name = name.strip()
        if not name:
            continue  # skip empty names
        found_group = None
        for group in name_groups:
            score = fuzz.ratio(name.lower(), group["canonical"].lower())
            if score >= fuzzy_threshold:
                found_group = group
                break
        if found_group:
            found_group["names"].add(name)
        else:
            name_groups.append({"canonical": name, "names": {name}})

    # Build alias->canonical map
    alias_to_canonical = {}
    for group in name_groups:
        canon = group["canonical"]
        for alias in group["names"]:
            alias_to_canonical[alias] = canon

    # Replace all contributor names with canonical
    df["contributor"] = df["contributor"].apply(lambda x: alias_to_canonical.get(x.strip(), x.strip()))

    # 3. Drop duplicates for (contributor, repo)
    df = df.drop_duplicates(subset=["contributor", "repo"], keep="first")

    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Cleaned contributor performance data saved to {output_file}")

if __name__ == "__main__":
    clean_contributor_performance()
