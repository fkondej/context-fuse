#!/usr/bin/env python3
"""
Context Fuse: Aggregates repo files into a unified context file for enhanced AI prompting.
"""

import argparse
import datetime
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import justext
from scrapy import Spider, signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Context Fuse: Aggregates repo files into a unified context file "
            "for enhanced AI prompting."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--git", help="Git repository URL to scrape")
    group.add_argument("--web", help="Website URL to scrape")
    return parser.parse_args()


def get_repo_name(repo_url: str) -> str:
    """Extract a safe name from a Git repository URL."""
    parts = repo_url.rstrip("/").replace(":", "/").split("/")
    return f"{parts[-2].lower()}_{parts[-1].replace('.git', '').lower()}"


def get_site_name(site_url: str) -> str:
    """Extract a safe name from a website URL."""
    netloc = urlparse(site_url).netloc
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc.replace(".", "_").lower()


def scrape_repo(repo_url: str, output_file_path: Path) -> None:
    """Clone and scrape a Git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = Path(temp_dir) / output_file_path.stem
        try:
            print(f"Cloning repository {repo_url} into temporary directory...")
            subprocess.run(
                ["git", "clone", repo_url, str(clone_dir)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return

        print("Scraping repository files...")

        with open(output_file_path, "w", encoding="utf-8") as outfile:
            # Write header information.
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            outfile.write("===========================================\n")
            outfile.write(f"Repository URL: {repo_url}\n")
            outfile.write(f"Scraped at: {timestamp}\n\n")

            for file in clone_dir.rglob("*"):
                if not file.is_file() or ".git" in file.parts:
                    continue
                rel_path = file.relative_to(clone_dir)
                outfile.write(f"----- FILE: '{rel_path}' (in {repo_url}) -----\n")
                try:
                    outfile.write(
                        file.read_text(encoding="utf-8", errors="ignore") + "\n\n"
                    )
                except (OSError, UnicodeDecodeError) as e:
                    outfile.write(f"[Error reading file: {e}]\n\n")

    print(f"Scraping complete. Result file saved to: {output_file_path}")


class WebsiteSpider(Spider):
    """Spider to crawl and scrape a website."""

    name = "website_spider"

    def __init__(self, url):
        self.start_urls = [url]
        self.allowed_domains = [urlparse(url).netloc]
        super().__init__()

    def parse(self, response):
        """Parse the response and extract core text."""
        print(f"Parsing URL: {response.url}")
        paragraphs = justext.justext(response.body, justext.get_stoplist("English"))
        core_text = "\n".join(p.text for p in paragraphs if not p.is_boilerplate)
        yield {"url": response.url, "content": core_text}

        # Follow internal links to other pages
        for link in response.css("a::attr(href)").getall():
            if link.startswith("/"):
                yield response.follow(link, self.parse)
            elif (
                link.startswith("http")
                and urlparse(link).netloc in self.allowed_domains
            ):
                yield response.follow(link, self.parse)


def scrape_website(url: str, output_file_path: Path) -> None:
    """Crawl and scrape a website."""
    process = CrawlerProcess(settings={"LOG_LEVEL": "ERROR"})

    with open(output_file_path, "w", encoding="utf-8") as outfile:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        outfile.write(f"Website URL: {url}\n")
        outfile.write(f"Scraped at: {timestamp}\n\n")

        def crawler_item_scraped(item, response, spider):
            outfile.write(f"----- URL: {item['url']} -----\n")
            outfile.write(item["content"] + "\n\n")
            outfile.flush()  # Ensure content is written to disk immediately

        dispatcher.connect(crawler_item_scraped, signal=signals.item_scraped)
        process.crawl(WebsiteSpider, url=url)
        process.start()  # Blocks until crawling is finished.


def main():
    """Main entry point of the script."""
    args = parse_args()
    if args.git:
        mode = "git"
        input_url = args.git
        identifier = get_repo_name(input_url)
    else:
        mode = "web"
        input_url = args.web
        identifier = get_site_name(input_url)

    # Create a "results" directory next to the script.
    script_dir = Path(__file__).resolve().parent
    results_dir = script_dir / "results"
    results_dir.mkdir(exist_ok=True)

    # Construct the output file name with repo name and timestamp.
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = results_dir / f"{mode}_{identifier}_{timestamp_str}.txt"

    if mode == "git":
        scrape_repo(input_url, output_file_path)
    else:
        scrape_website(input_url, output_file_path)

    # Cleanup: Delete previous result files for the same repo.
    for old_file in results_dir.glob(f"{mode}_{identifier}_*.txt"):
        if old_file != output_file_path:
            old_file.unlink()


if __name__ == "__main__":
    main()
