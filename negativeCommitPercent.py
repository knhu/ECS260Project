from pydriller import Repository
import pydriller
import pydriller
import csv
import pandas as pd
from datetime import datetime

def checkNegativeCommitPercentage(csvFile):
    df = pd.read_csv(csvFile)

    negative_commit_percentage = df.groupby('Author')['Sentiment'].apply(lambda x: (x == 'negative').sum() / len(x) * 100).reset_index(name='Negative Commit Percentage')

    df = pd.merge(df, negative_commit_percentage, on='Author', how='left')

    df.to_csv("commit_data_with_negative_percentage.csv", index=False)  # Save to a new CSV


if __name__ == "__main__":
    checkNegativeCommitPercentage("updated_test.csv")