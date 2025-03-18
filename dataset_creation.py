from pydriller import Repository
import pydriller
import csv
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
from thefuzz import fuzz
import time
import requests
from dotenv import load_dotenv
import ast

# ------------------------
# Utility Functions
# ------------------------

def standardize_author_names(df, threshold=70):
    canonical_names = group_similar_names(df, threshold)
    df["Author"] = df["Author"].map(canonical_names)
    return df

def group_similar_names(df, threshold):
    unique_names = df["Author"].unique()
    name_groups = {}
    canonical_names = {}

    for name in unique_names:
        found_group = False
        for group_key, group_members in name_groups.items():
            for member in group_members:
                if fuzz.ratio(name, member) >= threshold:
                    name_groups[group_key].add(name)
                    found_group = True
                    break
            if found_group:
                break
        if not found_group:
            name_groups[name] = {name}

    for group_members in name_groups.values():
        canonical_name = max(group_members, key=len)
        for member in group_members:
            canonical_names[member] = canonical_name

    return canonical_names

# ------------------------
# GitHub API Utilities
# ------------------------

# Load environment variables from .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("❌ GitHub Token not found! Ensure you have set it in the .env file.")

# GitHub API Headers
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Optionally, you can also store the repo list as a Python list string in the .env file.
# For example, in your .env file:
# GITHUB_REPOS=["https://github.com/activist-org/activist", "https://github.com/ansible/ansible", ...]
repo_list_str = os.getenv("GITHUB_REPOS")
if repo_list_str:
    try:
        repo_paths = ast.literal_eval(repo_list_str)
        if not isinstance(repo_paths, list):
            raise ValueError("Parsed repository list is not a valid Python list!")
    except (SyntaxError, ValueError) as e:
        raise ValueError(f"Error parsing repository list from .env: {e}")
    print(f"✅ Loaded {len(repo_paths)} repositories from .env")
else:
    # Otherwise, use the hard-coded list below.
    repo_urls = [
        "https://github.com/activist-org/activist",
        "https://github.com/ansible/ansible",
        "https://github.com/arviz-devs/arviz",
        "https://github.com/bokeh/bokeh",
        "https://github.com/borgbackup/borg",
        "https://github.com/hpcaitech/ColossalAI",
        "https://github.com/cookiecutter/cookiecutter-django",
        "https://github.com/mem0ai/mem0",
        "https://github.com/fastapi/fastapi",
        "https://github.com/h2oai/wave",
        "https://github.com/h2oai/wave-apps",
        "https://github.com/harmonydata/harmony",
        "https://github.com/sukeesh/Jarvis",
        "https://github.com/jupyter/notebook",
        "https://github.com/Kinto/kinto",
        "https://github.com/matplotlib/matplotlib",
        "https://github.com/gpodder/mygpo",
        "https://github.com/SamuelSchmidgall/AgentLaboratory",
        "https://github.com/multimodal-art-projection/YuE",
        "https://github.com/unionlabs/union",
        "https://github.com/Tencent/Hunyuan3D-2",
        "https://github.com/simplescaling/s1",
        "https://github.com/Zyphra/Zonos",
        "https://github.com/dzhng/deep-research",
        "https://github.com/jubnzv/mdeval.nvim",
        "https://github.com/kmkzt/react-hooks-svgdrawing",
        "https://github.com/mikitex70/plantuml-markdown",
        "https://github.com/clitic/kdam",
        "https://github.com/alexhillc/AXPhotoViewer",
        "https://github.com/VictoriaMetrics/fastcache",
        "https://github.com/sebastianbergmann/version",
        "https://github.com/schollz/howmanypeoplearearound",
        "https://github.com/exyte/ActivityIndicatorView",
        "https://github.com/google/guava",
        "https://github.com/FreeTubeApp/FreeTube",
        "https://github.com/coralproject/talk",
        "https://github.com/pengwynn/flint",
        "https://github.com/simbody/simbody",
        "https://github.com/gem5/gem5",
        "https://github.com/karpathy/nanoGPT",
        "https://github.com/mingrammer/diagrams",
        "https://github.com/RVC-Boss/GPT-SoVITS",
        "https://github.com/jesseduffield/lazydocker",
        "https://github.com/skylot/jadx",
        "https://github.com/browser-use/browser-use",
        "https://github.com/hiyouga/LLaMA-Factory",
        "https://github.com/agalwood/Motrix",
        "https://github.com/Z4nzu/hackingtool",
        "https://github.com/FiloSottile/mkcert",
        "https://github.com/CorentinJ/Real-Time-Voice-Cloning",
        "https://github.com/ageitgey/face_recognition",
        "https://github.com/meta-llama/llama",
        "https://github.com/shadowsocks/shadowsocks-windows",
        "https://github.com/localsend/localsend",
        "https://github.com/adam-p/markdown-here",
        "https://github.com/base/node",
        "https://github.com/typicode/json-server",
        "https://github.com/3b1b/manim",
        "https://github.com/2dust/v2rayN",
        "https://github.com/animate-css/animate.css",
        "https://github.com/Genymobile/scrcpy",
        "https://github.com/termux/termux-app",
        "https://github.com/suno-ai/bark",
        "https://github.com/huggingface/open-r1",
        "https://github.com/mannaandpoem/OpenManus",
        "https://github.com/camel-ai/owl",
        "https://github.com/lynx-family/lynx",
        "https://github.com/Jiayi-Pan/TinyZero",
        "https://github.com/browser-use/web-ui",
        "https://github.com/Wan-Video/Wan2.1",
        "https://github.com/deepseek-ai/DeepEP",
        "https://github.com/deepseek-ai/DeepGEMM",
        "https://github.com/OpenHealthForAll/open-health",
        "https://github.com/NovaSky-AI/SkyThought",
        "https://github.com/bytedance/UI-TARS-desktop",
        "https://github.com/eastlondoner/cursor-tools",
        "https://github.com/David-patrick-chuks/Instagram-AI-Agent",
        "https://github.com/coleam00/Archon",
        "https://github.com/rag-web-ui/rag-web-ui",
        "https://github.com/trycua/computer",
        "https://github.com/santinic/audiblez",
        "https://github.com/SkyworkAI/SkyReels-V1",
        "https://github.com/GLips/Figma-Context-MCP",
        "https://github.com/AgentDeskAI/browser-tools-mcp",
        "https://github.com/open-thoughts/open-thoughts",
        "https://github.com/superglue-ai/superglue",
        "https://github.com/antfu/node-modules-inspector",
        "https://github.com/kijai/ComfyUI-WanVideoWrapper",
        "https://github.com/browserbase/open-operator",
        "https://github.com/LearningCircuit/local-deep-research",
        "https://github.com/sunsmarterjie/yolov12",
        "https://github.com/IsaacGemal/wikitok",
        "https://github.com/ASLP-lab/DiffRhythm",
        "https://github.com/cloudflare/agents",
        "https://github.com/SaiAkhil066/DeepSeek-RAG-Chatbot",
        "https://github.com/rmurai0610/MASt3R-SLAM",
        "https://github.com/openai/openai-agents-python",
        "https://github.com/facebookresearch/large_concept_model",
        "https://github.com/thewh1teagle/kokoro-onnx",
        "https://github.com/bytedance/LatentSync"
    ]


# ------------------------
# GitHub API Request with Retry Logic
# ------------------------
MAX_RETRIES = 5
def github_api_request(url):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            # Handle rate limits
            if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                wait_time = reset_time - int(time.time())
                print(f"Rate limit exceeded. Sleeping for {wait_time} seconds...")
                time.sleep(wait_time + 1)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            retries += 1
            wait_time = min(2 ** retries, 30)
            print(f"⚠️ API request failed (attempt {retries}/{MAX_RETRIES}): {e}")
            time.sleep(wait_time)
    print(f"❌ API request failed after {MAX_RETRIES} retries: {url}")
    return None

# ------------------------
# Main Function: Mining Commits and GitHub API Metrics
# ------------------------
def get_commits_and_save_to_csv(repo_paths, csv_file_path):
    """
    Retrieves commits from multiple repositories using PyDriller,
    calculates project age and other commit metrics,
    and also mines additional SPACE framework metrics using GitHub's API.
    Saves the combined dataset to a CSV file.
    """
    all_commits_data = []
    repo_api_data = {}  # Dictionary to store GitHub API metrics per repository

    for repo_path in repo_paths:
        print(f"------------------- Currently parsing through {repo_path} -------------------")
        authors_to_churn = {}
        try:
            for commit in Repository(repo_path).traverse_commits():
                churn = commit.insertions-commit.deletions

                local_timezone = timezone(timedelta(seconds=commit.committer_timezone))
                local_commit_time = commit.committer_date.astimezone(local_timezone)
                
                # Calculate average cyclomatic complexity per commit
                total_complexity = 0
                modified_files = 0
                for mod in commit.modified_files:
                    if mod.complexity is not None:
                        total_complexity += mod.complexity
                        modified_files += 1
                avg_complexity = total_complexity / modified_files if modified_files > 0 else 0

                # Track code churn per author
                if commit.author.name not in authors_to_churn:
                    authors_to_churn[commit.author.name] = churn
                else:
                    authors_to_churn[commit.author.name] += churn
                all_commits_data.append([
                    commit.project_name,     # Project Name
                    commit.author.name,      # Author
                    commit.committer_date,   # Date
                    commit.msg,              # Message
                    repo_path,                # Repo Path for clarity
                    churn,
                    local_commit_time,
                    avg_complexity
                ])
        except Exception as e:
            print(f"Error processing repository {repo_path}: {e}")

        # Now, mine additional metrics using GitHub's API for this repository.
        repo_name = repo_path.replace("https://github.com/", "")
        
        # 1. Pull Request Metrics
        pr_api_url = f"https://api.github.com/repos/{repo_name}/pulls?state=all"
        prs = github_api_request(pr_api_url) or []
        total_prs = len(prs)
        pr_merge_times = []
        for pr in prs:
            if pr.get("merged_at"):
                created_at = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                merged_at = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ")
                pr_merge_times.append((merged_at - created_at).total_seconds() / 3600)
        avg_pr_merge_time = sum(pr_merge_times) / len(pr_merge_times) if pr_merge_times else None

        # 2. Issue Metrics
        issues_api_url = f"https://api.github.com/repos/{repo_name}/issues?state=all"
        issues = github_api_request(issues_api_url) or []
        total_issues = len(issues)
        issue_resolution_times = []
        for issue in issues:
            if issue.get("closed_at"):
                created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                closed_at = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
                issue_resolution_times.append((closed_at - created_at).total_seconds() / 3600)
        avg_issue_resolution_time = sum(issue_resolution_times) / len(issue_resolution_times) if issue_resolution_times else None

        # 3. Code Review Metrics
        review_api_url = f"https://api.github.com/repos/{repo_name}/pulls/comments"
        reviews = github_api_request(review_api_url) or []
        total_reviews = len(reviews)

        # 4. CI/CD Metrics
        ci_api_url = f"https://api.github.com/repos/{repo_name}/actions/runs"
        ci_data = github_api_request(ci_api_url) or {"workflow_runs": []}
        total_ci_runs = len(ci_data.get("workflow_runs", []))
        ci_failures = sum(1 for run in ci_data.get("workflow_runs", []) if run.get("conclusion") == "failure")
        ci_success_rate = (total_ci_runs - ci_failures) / total_ci_runs if total_ci_runs else None

        # 5. Deployment Metrics
        deployments_api_url = f"https://api.github.com/repos/{repo_name}/deployments"
        deployments = github_api_request(deployments_api_url) or []
        total_deployments = len(deployments)

        # 6. Contributor Metrics
        contributors_api_url = f"https://api.github.com/repos/{repo_name}/contributors"
        contributors = github_api_request(contributors_api_url) or []
        total_contributors = len(contributors)

        # 7. Bug Fix Metrics: Count commits (from our commit data) with keywords indicating bug fixes.
        bug_fix_count = sum(
            1 for row in all_commits_data
            if row[4] == repo_path and any(kw in row[3].lower() for kw in ["fix", "bug", "error"])
        )

        # Save the repository-level API metrics
        repo_api_data[repo_name] = {
            "Total PRs": total_prs,
            "Avg PR Merge Time (hours)": avg_pr_merge_time,
            "Total Issues": total_issues,
            "Avg Issue Resolution Time (hours)": avg_issue_resolution_time,
            "Total Code Reviews": total_reviews,
            "Total CI/CD Runs": total_ci_runs,
            "CI/CD Success Rate": ci_success_rate,
            "Total Deployments": total_deployments,
            "Total Contributors": total_contributors,
            "Bug Fix Commit Count": bug_fix_count
        }

    # ------------------------
    # Process Commit DataFrame
    # ------------------------
    df = pd.DataFrame(all_commits_data, columns=["Project Name", "Author", "Date", "Message", "Repo Path", "Code Churn", "Local Commit Time", "Avg Complexity"])

    if df.empty:
        print("No commit data found in the provided repositories.")
        return

    df['Date'] = pd.to_datetime(df['Date'], utc=True)

    # Remove Bots and Automated Messages
    df = df[~df["Author"].str.contains("bot", case=False, na=False)]
    df = df[~df["Message"].str.contains("dependabot", case=False, na=False)]
    df = df[~df["Message"].str.contains("Merge pull request", case=False, na=False)]

    # Standardize Author Names using Fuzzy Matching
    df = standardize_author_names(df)

    # Calculate Project Age for each project
    for project_name in df['Project Name'].unique():
        project_df = df[df['Project Name'] == project_name]
        first_commit_date = project_df['Date'].min()
        last_commit_date = project_df['Date'].max()
        project_age_days = (last_commit_date - first_commit_date).days
        project_age_years = project_age_days / 365.25
        df.loc[df['Project Name'] == project_name, 'Project Age (Years)'] = project_age_years

    # Calculate Total Commits per Author within each project
    project_author_commits = df.groupby(['Project Name', 'Author']).size().reset_index(name='Total Commits')
    df = pd.merge(df, project_author_commits, on=['Project Name', 'Author'], how='left')

    # ------------------------
    # Merge Repository-level API Metrics into the DataFrame
    # ------------------------
    def get_repo_metric(row, metric):
        repo = row["Repo Path"].replace("https://github.com/", "")
        return repo_api_data.get(repo, {}).get(metric, None)

    metrics_to_add = [
        "Total PRs", "Avg PR Merge Time (hours)", "Total Issues",
        "Avg Issue Resolution Time (hours)", "Total Code Reviews",
        "Total CI/CD Runs", "CI/CD Success Rate", "Total Deployments",
        "Total Contributors", "Bug Fix Commit Count"
    ]
    for metric in metrics_to_add:
        df[metric] = df.apply(lambda row: get_repo_metric(row, metric), axis=1)

    # ------------------------
    # Save DataFrame to CSV (append if file exists)
    # ------------------------
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

    print(f"Commit data with GitHub API metrics saved to {csv_file_path}")

# ------------------------
# Additional Function (Existing)
# ------------------------
def get_committer_timezone_info(repo_path):
    """
    Analyzes a Git repository and prints committer timezone information.

    Args:
        repo_path: The path to the Git repository.
    """
    commit_regular = 0
    commit_late = 0
    for commit in Repository(repo_path).traverse_commits():
        committer_date_utc = commit.committer_date
        committer_timezone_offset = commit.committer_timezone
        committer_timezone = datetime.timezone(timedelta(seconds=committer_timezone_offset))
        committer_date_local = committer_date_utc.astimezone(committer_timezone)

        print(f"Commit: {commit.hash}")
        print(f"  Committer: {commit.committer.name} <{commit.committer.email}>")
        print(f"  Committer Date (UTC): {committer_date_utc}")
        print(f"  Committer Timezone Offset: {committer_timezone_offset} seconds")
        print(f"  Committer Timezone: {committer_timezone}")
        print(f"  Committer Date (Local): {committer_date_local}")
        print("-" * 40)
        commit_regular += 1
        if 1 <= committer_date_local.hour <= 4:
            commit_late += 1
    print(f"Regular Commits: {commit_regular}\nLate Commits: {commit_late}")

# ------------------------
# Main Execution
# ------------------------
if __name__ == "__main__":
    repo_path = [
        "https://github.com/activist-org/activist",
        "https://github.com/ansible/ansible",
        "https://github.com/arviz-devs/arviz",
        "https://github.com/bokeh/bokeh",
        "https://github.com/borgbackup/borg",
        "https://github.com/hpcaitech/ColossalAI",
        "https://github.com/cookiecutter/cookiecutter-django",
        "https://github.com/mem0ai/mem0",
        "https://github.com/fastapi/fastapi",
        "https://github.com/h2oai/wave",
        "https://github.com/h2oai/wave-apps",
        "https://github.com/harmonydata/harmony",
        "https://github.com/sukeesh/Jarvis",
        "https://github.com/jupyter/notebook",
        "https://github.com/Kinto/kinto",
        "https://github.com/matplotlib/matplotlib",
        "https://github.com/gpodder/mygpo",
        "https://github.com/SamuelSchmidgall/AgentLaboratory",
        "https://github.com/multimodal-art-projection/YuE",
        "https://github.com/unionlabs/union",
        "https://github.com/Tencent/Hunyuan3D-2",
        "https://github.com/simplescaling/s1",
        "https://github.com/Zyphra/Zonos",
        "https://github.com/dzhng/deep-research",
        "https://github.com/jubnzv/mdeval.nvim",
        "https://github.com/kmkzt/react-hooks-svgdrawing",
        "https://github.com/mikitex70/plantuml-markdown",
        "https://github.com/clitic/kdam",
        "https://github.com/alexhillc/AXPhotoViewer",
        "https://github.com/VictoriaMetrics/fastcache",
        "https://github.com/sebastianbergmann/version",
        "https://github.com/schollz/howmanypeoplearearound",
        "https://github.com/exyte/ActivityIndicatorView",
        "https://github.com/google/guava",
        "https://github.com/FreeTubeApp/FreeTube",
        "https://github.com/coralproject/talk",
        "https://github.com/pengwynn/flint",
        "https://github.com/simbody/simbody",
        "https://github.com/gem5/gem5",
        "https://github.com/karpathy/nanoGPT",
        "https://github.com/mingrammer/diagrams",
        "https://github.com/RVC-Boss/GPT-SoVITS",
        "https://github.com/jesseduffield/lazydocker",
        "https://github.com/skylot/jadx",
        "https://github.com/browser-use/browser-use",
        "https://github.com/hiyouga/LLaMA-Factory",
        "https://github.com/agalwood/Motrix",
        "https://github.com/Z4nzu/hackingtool",
        "https://github.com/FiloSottile/mkcert",
        "https://github.com/CorentinJ/Real-Time-Voice-Cloning",
        "https://github.com/ageitgey/face_recognition",
        "https://github.com/meta-llama/llama",
        "https://github.com/shadowsocks/shadowsocks-windows",
        "https://github.com/localsend/localsend",
        "https://github.com/adam-p/markdown-here",
        "https://github.com/base/node",
        "https://github.com/typicode/json-server",
        "https://github.com/3b1b/manim",
        "https://github.com/2dust/v2rayN",
        "https://github.com/animate-css/animate.css",
        "https://github.com/Genymobile/scrcpy",
        "https://github.com/termux/termux-app",
        "https://github.com/suno-ai/bark",
        "https://github.com/huggingface/open-r1",
        "https://github.com/mannaandpoem/OpenManus",
        "https://github.com/camel-ai/owl",
        "https://github.com/lynx-family/lynx",
        "https://github.com/Jiayi-Pan/TinyZero",
        "https://github.com/browser-use/web-ui",
        "https://github.com/Wan-Video/Wan2.1",
        "https://github.com/deepseek-ai/DeepEP",
        "https://github.com/deepseek-ai/DeepGEMM",
        "https://github.com/OpenHealthForAll/open-health",
        "https://github.com/NovaSky-AI/SkyThought",
        "https://github.com/bytedance/UI-TARS-desktop",
        "https://github.com/eastlondoner/cursor-tools",
        "https://github.com/David-patrick-chuks/Instagram-AI-Agent",
        "https://github.com/coleam00/Archon",
        "https://github.com/rag-web-ui/rag-web-ui",
        "https://github.com/trycua/computer",
        "https://github.com/santinic/audiblez",
        "https://github.com/SkyworkAI/SkyReels-V1",
        "https://github.com/GLips/Figma-Context-MCP",
        "https://github.com/AgentDeskAI/browser-tools-mcp",
        "https://github.com/open-thoughts/open-thoughts",
        "https://github.com/superglue-ai/superglue",
        "https://github.com/antfu/node-modules-inspector",
        "https://github.com/kijai/ComfyUI-WanVideoWrapper",
        "https://github.com/browserbase/open-operator",
        "https://github.com/LearningCircuit/local-deep-research",
        "https://github.com/sunsmarterjie/yolov12",
        "https://github.com/IsaacGemal/wikitok",
        "https://github.com/ASLP-lab/DiffRhythm",
        "https://github.com/cloudflare/agents",
        "https://github.com/SaiAkhil066/DeepSeek-RAG-Chatbot",
        "https://github.com/rmurai0610/MASt3R-SLAM",
        "https://github.com/openai/openai-agents-python",
        "https://github.com/facebookresearch/large_concept_model",
        "https://github.com/thewh1teagle/kokoro-onnx",
        "https://github.com/bytedance/LatentSync"
    ]

    # Uncomment the following line to run the timezone analysis
    # get_committer_timezone_info(repo_path)
    
    get_commits_and_save_to_csv(repo_path, "all_mined_repos.csv")
