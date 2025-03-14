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
#Change format of date to only include date, not time
df['Commit_DateTime'] = pd.to_datetime(df['Commit_Date']) #Copy Date and Time into new column
df['Commit_Date'] = pd.to_datetime(df['Commit_Date'].transform(lambda x: x.split(' ')[0]))


#Collect average daily commits and average daily churn
df['Previous_Commit_Date'] = df.groupby('Author')['Commit_DateTime'].shift()
df['Time_Between_Commits'] = df['Commit_DateTime'] - df['Previous_Commit_Date']
df['Time_Between_Commits'] = df['Time_Between_Commits'].apply(lambda x: (x.days * 24) + (x.seconds // 3600))




for author in df['Author'].unique():
    author_df = df[df['Author'] == author]

    if author_df.shape[0] <= 4 or author_df.shape[0] >= 500: #Dev must have 5 or more commits but fewer than 150
       continue

    #idk how to do this yet but this is throwing all kinds of warnings
    #author_df['Previous_Commit_Date'] = author_df.groupby('Author')['Commit_DateTime'].shift()
    #author_df['Time_Between_Commits'] = author_df['Commit_DateTime'] - author_df['Previous_Commit_Date']
    #author_df['Time_Between_Commits'] = author_df['Time_Between_Commits'].apply(lambda x: x.days)
    #auth_mean_commit_time = author_df['Time_Between_Commits'].mean()
    mean_commit_time = author_df['Time_Between_Commits'].mean()
    #
    for date in author_df['Commit_Date']:
        date_df = author_df.loc[author_df['Commit_Date'] == date]

        code_churn = date_df['Code_Churn'].sum()
        num_commits = date_df.shape[0] #number of commits this day
        
        data_temp = [
            date_df['Project_Name'].iloc[0],
            author,
            date,
            mean_commit_time,
            code_churn,
            num_commits
        ]
        if data_temp not in data:
            data.append(data_temp)


#Measure dead time and average time between commits?

    
df_new = pd.DataFrame(data, columns=["Project_Name","Author","Date","Mean_Commit_Time","Daily_Code_Churn","Num_Commits"])

#df_new = df_new[df_new["Num_Commits"] > 1]

#df_new = df_new.groupby('Author').filter(lambda x: x['Daily_Code_Churn'].mean() & x['Num_Commits'].mean())

df_new = df_new.groupby('Author').agg({'Mean_Commit_Time': ['mean'],'Daily_Code_Churn': ['mean'], 'Num_Commits': ['mean', 'sum']}).reset_index()
    
df_new.columns = ['Author','Mean_Commit_Time','Average_Daily_Code_Churn','Average_Daily_Num_Commits','Total_Commits']

if os.path.exists(output_csv):
    df_new.to_csv(output_csv, mode='a', header=False, index=False, encoding='utf-8')
else:
    df_new.to_csv(output_csv, index=False, encoding='utf-8')
    #code_churn_avg = author_df['Code_Churn'].mean()
