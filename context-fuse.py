#!/usr/bin/env python3
import argparse
import subprocess
import tempfile
import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Context Fuse: Aggregates repo files into a unified context file "
            "for enhanced AI prompting."
        )
    )
    parser.add_argument("repo_url", help="HTTPS or SSH URL of the repository")
    return parser.parse_args()


def get_repo_name(repo_url: str) -> str:
    parts = repo_url.rstrip("/").replace(":", "/").split("/")
    return f"{parts[-2].lower()}_{parts[-1].replace('.git', '').lower()}"


def scrape_repo(repo_dir: Path, repo_url: str, output_file_path: Path) -> None:
    with open(output_file_path, "w", encoding="utf-8") as outfile:
        # Write header information.
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        outfile.write("===========================================\n")
        outfile.write(f"Repository URL: {repo_url}\n")
        outfile.write(f"Scraped at: {timestamp}\n\n")

        for file in repo_dir.rglob("*"):
            if not file.is_file() or ".git" in file.parts:
                continue
            rel_path = file.relative_to(repo_dir)
            outfile.write(f"----- FILE: '{rel_path}' (in {repo_url}) -----\n")
            try:
                outfile.write(
                    file.read_text(encoding="utf-8", errors="ignore") + "\n\n"
                )
            except Exception as e:
                outfile.write(f"[Error reading file: {e}]\n\n")


def main():
    args = parse_args()
    repo_url = args.repo_url
    repo_name = get_repo_name(repo_url)

    # Create a "results" directory next to the script.
    script_dir = Path(__file__).resolve().parent
    results_dir = script_dir / "results"
    results_dir.mkdir(exist_ok=True)

    # Construct the output file name with repo name and timestamp.
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = results_dir / f"{repo_name}_{timestamp_str}.txt"

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = Path(temp_dir) / repo_name
        try:
            print(f"Cloning repository {repo_url} into temporary directory...")
            subprocess.run(
                ["git", "clone", repo_url, str(clone_dir)],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return

        print("Scraping repository files...")
        scrape_repo(clone_dir, repo_url, str(output_file_path))

    print(f"Scraping complete. Result file saved to: {output_file_path}")

    # Cleanup: Delete previous result files for the same repo.
    for old_file in results_dir.glob(f"{repo_name}_*.txt"):
        if old_file != output_file_path:
            old_file.unlink()


if __name__ == "__main__":
    main()
