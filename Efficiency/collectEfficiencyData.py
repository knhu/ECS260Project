import argparse
import pandas as pd
import os
from datetime import datetime
#Collects specific data for Efficiency metrics

parser = argparse.ArgumentParser()

parser.add_argument('input_csv')

parser.add_argument('output_csv')

args = parser.parse_args()

input_csv = args.input_csv
output_csv = args.output_csv

try:
    df = pd.read_csv(input_csv)
except FileNotFoundError:
    print(f"Error: Input CSV file '{input_csv}' not found.")
    exit(0)

data = []
df['Commit_Date'] = pd.to_datetime(df['Commit_Date'].transform(lambda x: x.split(' ')[0]))


#Collect average daily commits and average daily churn

for author in df['Author'].unique():
    author_df = df[df['Author'] == author]

    for date in author_df['Commit_Date']:
        date_df = author_df.loc[author_df['Commit_Date'] == date]

        code_churn = date_df['Code_Churn'].sum()
        num_commits = date_df.shape[0] #number of commits this day
        data_temp = [
            date_df['Project_Name'].iloc[0],
            author,
            date,
            code_churn,
            num_commits
        ]
        if data_temp not in data:
            data.append(data_temp)




    
df_new = pd.DataFrame(data, columns=["Project_Name","Author","Date","Daily_Code_Churn","Num_Commits"])

if os.path.exists(output_csv):
    df_new.to_csv(output_csv, mode='a', header=False, index=False, encoding='utf-8')
else:
    df_new.to_csv(output_csv, index=False, encoding='utf-8')
    #code_churn_avg = author_df['Code_Churn'].mean()
