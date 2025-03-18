import os
from dotenv import load_dotenv
import requests
import pandas as pd
from pydriller import Repository
from datetime import datetime
from time import sleep
from tqdm import tqdm

# Define the path to the .env file (in parent directory)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

# Load environment variables
load_dotenv(env_path)

# GitHub API Token (optional)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Confirm if the token is loaded (for debugging)
if not GITHUB_TOKEN:
    print("Warning: GITHUB_TOKEN not found. API requests may be limited.")

# Hardcoded list of GitHub repo URLs
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

# Extract repository name
def get_repo_name(repo_url):
    return "/".join(repo_url.split("/")[-2:])

# GitHub API Request Function with Rate Limit Handling
def github_api_request(url):
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_time = max(0, reset_time - int(datetime.now().timestamp()))
            print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
            sleep(wait_time + 1)
        else:
            print(f"GitHub API Error {response.status_code}: {url}")
            return None

# Initialize data storage
repo_data = []
contributor_data = []

# List of keywords for detecting bug-fix commits
BUG_FIX_KEYWORDS = ["fix", "bug", "resolve", "patch", "hotfix", "defect", "issue"]

# Process repositories
for repo_url in tqdm(repo_urls, desc="Processing Repositories"):
    repo_name = get_repo_name(repo_url)
    print(f"Processing: {repo_name}")

    try:
        repo_commit_count = 0
        contributors = {}

        # PyDriller: Extract commit and contributor data
        for commit in Repository(repo_url).traverse_commits():
            author = commit.author.name
            if author not in contributors:
                contributors[author] = {
                    "repo": repo_name,
                    "total_commits": 0,
                    "code_churn": 0,
                    "bug_fixes": 0,
                }
            contributors[author]["total_commits"] += 1
            contributors[author]["code_churn"] += commit.insertions + commit.deletions
            
            # More robust bug-fix detection
            if any(keyword in commit.msg.lower() for keyword in BUG_FIX_KEYWORDS):
                contributors[author]["bug_fixes"] += 1

            repo_commit_count += 1

        # GitHub API: Fetch repository metadata
        repo_api_url = f"https://api.github.com/repos/{repo_name}"
        repo_data_json = github_api_request(repo_api_url)
        if not repo_data_json:
            print(f"Skipping {repo_name} due to missing repo data.")
            continue

        # Pull Requests
        pr_api_url = f"https://api.github.com/repos/{repo_name}/pulls?state=all&per_page=100"
        pr_data = github_api_request(pr_api_url) or []
        total_prs = len(pr_data)
        pr_merge_times = [
            (datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ") -
             datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")).total_seconds() / 3600
            for pr in pr_data if pr.get("merged_at")
        ]
        avg_pr_merge_time = sum(pr_merge_times) / len(pr_merge_times) if pr_merge_times else None

        # Issues
        issue_api_url = f"https://api.github.com/repos/{repo_name}/issues?state=all&per_page=100"
        issue_data = github_api_request(issue_api_url) or []
        total_issues = len(issue_data)
        reopened_issues = sum(1 for issue in issue_data if issue.get("state") == "reopened")
        issue_reopen_rate = reopened_issues / total_issues if total_issues else None

        # CI/CD Data
        workflows_url = f"https://api.github.com/repos/{repo_name}/actions/runs"
        workflow_data = github_api_request(workflows_url) or {}
        ci_cd_runs = len(workflow_data.get("workflow_runs", []))
        successful_ci_cd = sum(1 for run in workflow_data.get("workflow_runs", []) if run.get("conclusion") == "success")
        ci_cd_success_rate = successful_ci_cd / ci_cd_runs if ci_cd_runs else None

        # Store Repository-Level Data
        repo_data.append({
            "repo_name": repo_name,
            "total_commits": repo_commit_count,
            "total_prs": total_prs,
            "avg_pr_merge_time": avg_pr_merge_time,
            "total_issues": total_issues,
            "issue_reopening_rate": issue_reopen_rate,
            "ci_cd_success_rate": ci_cd_success_rate,
        })

        # Store Contributor-Level Data
        for contributor, metrics in contributors.items():
            contributor_data.append({
                "contributor": contributor,
                "repo": metrics["repo"],
                "total_commits": metrics["total_commits"],
                "total_prs": total_prs,
                "avg_pr_merge_time": avg_pr_merge_time,
                "code_churn": metrics["code_churn"],
                "bug_fix_commits": metrics["bug_fixes"],
            })

    except Exception as e:
        print(f"Error processing {repo_name}: {e}")

# Save to CSV
repo_df = pd.DataFrame(repo_data)
repo_df.to_csv("repo_performance.csv", index=False)

contributor_df = pd.DataFrame(contributor_data)
contributor_df.to_csv("contributor_performance.csv", index=False)

print("Data collection completed. Check repo_performance.csv and contributor_performance.csv.")
