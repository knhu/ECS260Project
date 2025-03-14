from pydriller import Repository
import pydriller
import pydriller
from pydriller.metrics.process.code_churn import CodeChurn
import csv
import pandas as pd
from datetime import datetime
import os


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
