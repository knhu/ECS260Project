import pandas as pd
from pydriller import Repository
from collections import defaultdict
import os
import csv
from datetime import timedelta

# List of repository URLs to process
REPO_URLS = [
    "https://github.com/activist-org/activist.git",
    "https://github.com/ansible/ansible.git",
    "https://github.com/arviz-devs/arviz.git",
    "https://github.com/bokeh/bokeh.git",
    "https://github.com/borgbackup/borg.git",
    "https://github.com/CiviWiki/OpenCiviWiki.git",
    "https://github.com/hpcaitech/ColossalAI.git",
    "https://github.com/cookiecutter/cookiecutter-django.git",
    "https://github.com/mem0ai/mem0.git",
    "https://github.com/fastapi/fastapi.git",
    "https://github.com/h2oai/wave.git",
    "https://github.com/h2oai/wave-apps.git",
    "https://github.com/harmonydata/harmony.git",
    "https://github.com/sukeesh/Jarvis.git",
    "https://github.com/jupyter/notebook.git",
    "https://github.com/Kinto/kinto.git",
    "https://github.com/matplotlib/matplotlib.git",
    "https://github.com/mindsdb/mindsdb.git",
    "https://github.com/mitmproxy/mitmproxy.git",
    "https://github.com/gpodder/mygpo.git",
    "https://github.com/Deep-Agent/R1-V.git",
    "https://github.com/SamuelSchmidgall/AgentLaboratory.git",
    "https://github.com/multimodal-art-projection/YuE.git",
    "https://github.com/unionlabs/union.git",
    "https://github.com/Tencent/Hunyuan3D-2.git",
    "https://github.com/simplescaling/s1.git",
    "https://github.com/Zyphra/Zonos.git",
    "https://github.com/dzhng/deep-research.git",
    "https://github.com/openai/SWELancer-Benchmark.git",
    "https://github.com/jubnzv/mdeval.nvim.git",
    "https://github.com/kmkzt/react-hooks-svgdrawing.git",
    "https://github.com/danbernier/WordCram.git",
    "https://github.com/cs-util-com/cscore.git",
    "https://github.com/mikitex70/plantuml-markdown.git",
    "https://github.com/clitic/kdam.git",
    "https://github.com/alexhillc/AXPhotoViewer.git",
    "https://github.com/VictoriaMetrics/fastcache.git",
    "https://github.com/sebastianbergmann/version.git",
    "https://github.com/schollz/howmanypeoplearearound.git",
    "https://github.com/exyte/ActivityIndicatorView.git",
    "https://github.com/obsproject/obs-studio.git",
    "https://github.com/google/guava.git",
    "https://github.com/scrapy/scrapy.git",
    "https://github.com/FreeTubeApp/FreeTube.git",
    "https://github.com/nasa/openmct.git",
    "https://github.com/ocaml/ocaml.git",
    "https://github.com/coralproject/talk.git",
    "https://github.com/pengwynn/flint.git",
    "https://github.com/validator/validator.git",
    "https://github.com/simbody/simbody.git",
    "https://github.com/astropy/astropy.git",
    "https://github.com/overleaf/overleaf.git",
    "https://github.com/SeleniumHQ/selenium.git",
    "https://github.com/lowRISC/ibex.git",
    "https://github.com/gem5/gem5.git",
    "https://github.com/karpathy/nanoGPT.git",
    "https://github.com/mingrammer/diagrams.git",
    "https://github.com/RVC-Boss/GPT-SoVITS.git",
    "https://github.com/jesseduffield/lazydocker.git",
    "https://github.com/skylot/jadx.git",
    "https://github.com/lllyasviel/Fooocus.git",
    "https://github.com/FuelLabs/fuels-ts.git",
    "https://github.com/FuelLabs/fuels-rs.git",
    "https://github.com/browser-use/browser-use.git",
    "https://github.com/hiyouga/LLaMA-Factory.git",
    "https://github.com/hacksider/Deep-Live-Cam.git",
    "https://github.com/agalwood/Motrix.git",
    "https://github.com/Z4nzu/hackingtool.git",
    "https://github.com/geekan/MetaGPT.git",
    "https://github.com/FiloSottile/mkcert.git",
    "https://github.com/AntonOsika/gpt-engineer.git",
    "https://github.com/CorentinJ/Real-Time-Voice-Cloning.git",
    "https://github.com/ageitgey/face_recognition.git",
    "https://github.com/FuelLabs/fuel-core.git",
    "https://github.com/meta-llama/llama.git",
    "https://github.com/shadowsocks/shadowsocks-windows.git",
    "https://github.com/OpenInterpreter/open-interpreter.git",
    "https://github.com/localsend/localsend.git",
    "https://github.com/adam-p/markdown-here.git",
    "https://github.com/apache/echarts.git",
    "https://github.com/FuelLabs/sway.git",
    "https://github.com/tesseract-ocr/tesseract.git",
    "https://github.com/base/node.git",
    "https://github.com/hoppscotch/hoppscotch.git",
    "https://github.com/CompVis/stable-diffusion.git",
    "https://github.com/comfyanonymous/ComfyUI.git",
    "https://github.com/nomic-ai/gpt4all.git",
    "https://github.com/typicode/json-server.git",
    "https://github.com/3b1b/manim.git",
    "https://github.com/2dust/v2rayN.git",
    "https://github.com/animate-css/animate.css.git",
    "https://github.com/fatedier/frp.git",
    "https://github.com/Genymobile/scrcpy.git",
    "https://github.com/ytdl-org/youtube-dl.git",
    "https://github.com/iina/iina.git",
    "https://github.com/shadcn-ui/ui.git",
    "https://github.com/termux/termux-app.git",
    "https://github.com/evanw/esbuild.git",
    "https://github.com/KRTirtho/spotube.git",
    "https://github.com/suno-ai/bark.git"
]

def format_offset(tzinfo):
    """Convert tzoffset object to a readable UTC offset string (e.g., +00:00)."""
    if tzinfo is None:
        return "Unknown"
    offset_seconds = tzinfo._offset.total_seconds()
    hours = int(offset_seconds // 3600)
    minutes = int((offset_seconds % 3600) // 60)
    sign = "+" if hours >= 0 else "-"
    return f"{sign}{abs(hours):02d}:{abs(minutes):02d}"

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

def mine_repository(repo_url, repo_index, total_repos):
    """Mine a single repository for all metrics and export to CSV files."""
    # Create folder name from repo URL (replace invalid chars and use repo name)
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    output_dir = f"repo_metrics_{repo_name}"
    os.makedirs(output_dir, exist_ok=True)

    # Define output CSV files with directory
    COMMUNICATION_CSV = os.path.join(output_dir, "communication_events.csv")
    COMMITS_DATA_CSV = os.path.join(output_dir, "commits_data.csv")
    TIMEZONE_CSV = os.path.join(output_dir, "committer_timezones.csv")
    CONTRIBUTORS_EXPERIENCE_CSV = os.path.join(output_dir, "contributors_experience.csv")
    SUMMARY_CSV = os.path.join(output_dir, "summary.csv")

    # Data storage
    committer_timezones = defaultdict(int)
    file_contributors = defaultdict(lambda: defaultdict(int))

    print(f"\n[{repo_index}/{total_repos}] Mining repository: {repo_url}")
    repo = Repository(repo_url)

    # Collect commit data
    commits_data = []
    commit_count = 0
    for commit in repo.traverse_commits():
        commit_count += 1
        if commit_count % 1000 == 0:
            print(f"[{repo_index}/{total_repos}] Processed {commit_count} commits in {repo_name}")

        # Timezone data
        tz_name = format_offset(commit.committer_date.tzinfo)
        committer_timezones[tz_name] += 1

        # Process commits and contributors experience
        for mod in commit.modified_files:
            file_path = mod.new_path if mod.new_path else mod.old_path
            if file_path:
                commits_data.append({
                    "author": commit.author.name,
                    "timestamp": commit.committer_date,
                    "file": file_path
                })
                file_contributors[file_path][commit.author.name] += mod.added_lines

    # Create commits DataFrame and save
    commits_df = pd.DataFrame(commits_data)
    commits_df.to_csv(COMMITS_DATA_CSV, index=False)

    # Author stats
    author_stats = commits_df['author'].value_counts()
    total_authors = len(author_stats)
    top_10_contributors = author_stats.head(10)

    # Communication events
    commits_df = commits_df.sort_values(["file", "timestamp"])
    commits_df["prev_timestamp"] = commits_df.groupby("file")["timestamp"].shift(1)
    commits_df["prev_author"] = commits_df.groupby("file")["author"].shift(1)
    time_window = pd.Timedelta(hours=24)
    comm_events = commits_df[
        (commits_df["timestamp"] - commits_df["prev_timestamp"] <= time_window) &
        (commits_df["author"] != commits_df["prev_author"]) &
        commits_df["prev_timestamp"].notna()
    ]
    comm_events = comm_events[["file", "prev_author", "author", "prev_timestamp", "timestamp"]].rename(columns={
        "prev_author": "author1",
        "author": "author2",
        "prev_timestamp": "time1",
        "timestamp": "time2"
    })
    comm_events.to_csv(COMMUNICATION_CSV, index=False)

    # Contributors experience
    contributors_experience = calculate_contributors_experience(file_contributors)
    contributors_data = [(file, f"{percentage:.2f}") for file, percentage in contributors_experience.items()]
    save_to_csv(contributors_data, CONTRIBUTORS_EXPERIENCE_CSV, ["File", "Top Contributor Share (%)"])

    # Timezone data
    timezone_data = [(tz, count) for tz, count in committer_timezones.items()]
    save_to_csv(timezone_data, TIMEZONE_CSV, ["Timezone", "Commit Count"])

    # Comprehensive summary
    summary_data = []
    summary_data.append(["Commits Overview", ""])
    summary_data.append(["Total Commits", commit_count])
    summary_data.append(["Total Unique Authors", total_authors])
    summary_data.append(["", ""])

    summary_data.append(["Top 10 Contributors", ""])
    summary_data.append(["Author", "Commits"])
    for author, count in top_10_contributors.items():
        summary_data.append([author, count])
    summary_data.append(["", ""])

    author_pairs = comm_events.groupby(['author1', 'author2']).size().sort_values(ascending=False)
    summary_data.append(["Communication Events", f"Total: {len(comm_events)}"])
    summary_data.append(["Author1,Author2", "Events"])
    for (author1, author2), count in author_pairs.items():
        summary_data.append([f"{author1},{author2}", count])
    summary_data.append(["", ""])

    summary_data.append(["Committer Timezone Distribution", f"Unique Timezones: {len(committer_timezones)}"])
    summary_data.append(["Timezone", "Commits"])
    for tz, count in sorted(committer_timezones.items()):
        summary_data.append([tz, count])
    summary_data.append(["", ""])

    avg_contributors_experience = sum(contributors_experience.values()) / len(contributors_experience) if contributors_experience else 0
    summary_data.append(["Contributors Experience", f"Average across {len(contributors_experience)} files: {avg_contributors_experience:.2f}%"])
    summary_data.append(["File", "Top Contributor Share (%)"])
    for file, percentage in sorted(contributors_experience.items(), key=lambda x: x[1], reverse=True)[:10]:
        summary_data.append([file, f"{percentage:.2f}"])

    save_to_csv(summary_data, SUMMARY_CSV, ["Field", "Value"])

    # Final output for this repo
    print(f"[{repo_index}/{total_repos}] Saved {len(commits_data)} commit records to {COMMITS_DATA_CSV}")
    print(f"[{repo_index}/{total_repos}] Found {len(comm_events)} communication events. Data saved to {COMMUNICATION_CSV}")
    print(f"[{repo_index}/{total_repos}] Processed {len(contributors_experience)} files for contributors experience. Data saved to {CONTRIBUTORS_EXPERIENCE_CSV}")
    print(f"[{repo_index}/{total_repos}] Found {len(committer_timezones)} unique timezones. Data saved to {TIMEZONE_CSV}")
    print(f"[{repo_index}/{total_repos}] Comprehensive summary saved to {SUMMARY_CSV}")

def process_repositories():
    """Process all repositories sequentially."""
    total_repos = len(REPO_URLS)
    for i, repo_url in enumerate(REPO_URLS, 1):
        try:
            mine_repository(repo_url, i, total_repos)
        except Exception as e:
            print(f"[{i}/{total_repos}] Error processing {repo_url}: {e}")
    print(f"\nCompleted processing all {total_repos} repositories.")

if __name__ == "__main__":
    process_repositories()
