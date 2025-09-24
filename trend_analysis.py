# trend_analysis.py
import os
import json
import logging
import pandas as pd
from janome.tokenizer import Tokenizer
from collections import Counter
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

JANOME = Tokenizer()

def load_skills(skills_path="skills_dict.json"):
    with open(skills_path, encoding="utf-8") as f:
        return json.load(f)

def extract_skills(text, skills_db):
    text_lower = text.lower()
    # Japanese tokenization
    tokens = [t.surface for t in JANOME.tokenize(text)]
    found = []
    for category, skills in skills_db.items():
        for skill in skills:
            if skill.lower() in text_lower or skill in tokens:
                found.append(skill)
    return found

def analyze_youtube_trends(meta_csv, skills_db, save_fig="yt_trends.png"):
    df = pd.read_csv(meta_csv)
    df['upload_date'] = pd.to_datetime(df['upload_date'], errors="coerce")
    trend_data = {}

    for _, row in df.iterrows():
        month = row['upload_date'].strftime('%Y-%m') if not pd.isna(row['upload_date']) else "unknown"
        text = " ".join([str(row.get("title", "")), str(row.get("description", "")), str(row.get("transcript", ""))])
        found = extract_skills(text, skills_db)
        trend_data.setdefault(month, []).extend(found)
    
    # Count by month
    trend_by_month = {month: Counter(skills) for month, skills in trend_data.items()}
    # For top skills, plot Line Chart
    top_skills = Counter([s for l in trend_data.values() for s in l]).most_common(10)
    top_skill_names = [k for k, _ in top_skills]
    months = sorted(trend_by_month.keys())
    plt.figure(figsize=(12,6))
    for skill in top_skill_names:
        freqs = [trend_by_month[m][skill] if skill in trend_by_month[m] else 0 for m in months]
        plt.plot(months, freqs, label=skill)
    plt.title("YouTube Skill Trend (JP/EN)")
    plt.xlabel("Month")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_fig)
    logging.info(f"Saved YouTube trend plot as {save_fig}")

if __name__ == "__main__":
    # -- Example Run --
    skills_db = load_skills("skills_dict.json")
    yt_csv = "data/yt/all_metadata.csv"
    analyze_youtube_trends(yt_csv, skills_db)
