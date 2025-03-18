import pandas as pd
import numpy as np

def clean_repo_performance(input_file="repo_performance.csv", output_file="cleaned_repo_performance.csv"):
    """
    Cleans repo_performance.csv by:
    1. Ensuring numeric columns are correct and handling missing values.
    2. Removing outliers (using IQR).
    3. Saving cleaned data.

    Expects columns:
    ['repo_name', 'total_commits', 'total_prs', 'avg_pr_merge_time',
     'total_issues', 'issue_reopening_rate', 'ci_cd_success_rate']
    """

    # Step 1: Load dataset
    df = pd.read_csv(input_file)

    # Ensure column existence
    expected_cols = [
        "repo_name",
        "total_commits",
        "total_prs",
        "avg_pr_merge_time",
        "total_issues",
        "issue_reopening_rate",
        "ci_cd_success_rate",
    ]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataset. Please verify CSV structure.")

    # Step 2: Ensure numeric columns, fill missing with median
    numeric_cols = [
        "total_commits",
        "total_prs",
        "avg_pr_merge_time",
        "total_issues",
        "issue_reopening_rate",
        "ci_cd_success_rate",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].fillna(df[col].median(), inplace=True)

    # Step 3: Remove outliers using IQR on selected columns
    outlier_cols = ["avg_pr_merge_time", "issue_reopening_rate", "ci_cd_success_rate"]

    def remove_outliers_iqr(data, col):
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]

    for col in outlier_cols:
        df = remove_outliers_iqr(df, col)

    # Step 4: Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Cleaned repo performance data saved to: {output_file}")


if __name__ == "__main__":
    clean_repo_performance(
        input_file="repo_performance.csv",
        output_file="cleaned_repo_performance.csv"
    )
