# blog_scrape.py
import os
import json
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def fetch_blog(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        # Try to extract main content
        if "qiita.com" in url:
            content = soup.find("div", class_="it-MdContent").get_text(" ", strip=True)
        elif "zenn.dev" in url:
            content = soup.find("article").get_text(" ", strip=True)
        else:
            # fallback, extract all paragraphs
            content = " ".join(p.get_text() for p in soup.find_all("p"))
        title = soup.title.text.strip() if soup.title else url
        logging.info(f"Fetched: {title[:40]}")
        return {"url": url, "title": title, "content": content}
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {e}")
        return None

def scrape_blogs(blog_urls, save_path='data/blogs/'):
    os.makedirs(save_path, exist_ok=True)
    results = []
    for url in blog_urls:
        entry = fetch_blog(url)
        if entry:
            results.append(entry)
            with open(os.path.join(save_path, f"{hash(url)}.json"), "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(save_path, "all_blogs.csv"), index=False)
    logging.info(f"Scraped and saved {len(results)} blogs.")

if __name__ == "__main__":
    # Place blog URLs to data/blogs/blog_list.txt
    blog_list_path = "data/blogs/blog_list.txt"
    with open(blog_list_path, encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    scrape_blogs(urls)
