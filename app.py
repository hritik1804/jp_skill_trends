# app.py
import streamlit as st
import pandas as pd
import json
from collections import Counter
import matplotlib.pyplot as plt
from janome.tokenizer import Tokenizer
from blog_scrape import fetch_blog
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# List of top Japanese tech blogs (add more as needed)
JP_TECH_BLOGS = {
    "Qiita": "https://qiita.com/",
    "Zenn": "https://zenn.dev/",
    "Japan Dev Blog": "https://japan-dev.com/blog",
    "Hatena Developer Blog": "https://developer.hatenastaff.com/",
    "TechCrunch Japan": "https://jp.techcrunch.com/",
    "CodeIQ Magazine": "https://codeiq.jp/magazine/",
    "ITmedia News": "https://www.itmedia.co.jp/news/",
    "Publickey": "https://www.publickey1.jp/",
    "Findy Engineer Lab": "https://findy-code.io/engineer-lab",
    "LIG Blog": "https://liginc.co.jp/blog/",
    "Mercari Engineering Blog": "https://engineering.mercari.com/blog/",
    "LINE Engineering Blog": "https://engineering.linecorp.com/ja/blog/",
    "CyberAgent Developers Blog": "https://developers.cyberagent.co.jp/blog/",
    "Yahoo! JAPAN Tech Blog": "https://techblog.yahoo.co.jp/",
}

# --- Helper functions ---
def load_skills_db(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def extract_skills(text, skills_db):
    tokens = [t.surface for t in JANOME.tokenize(str(text))]
    found = []
    for _, skills in skills_db.items():
        for skill in skills:
            if skill in text or skill in tokens:
                found.append(skill)
    return found

def analyze_trends(df, text_cols, date_col, skills_db, period="M"):
    trends = {}
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
        df['period'] = df[date_col].dt.to_period(period)
        for _, row in df.iterrows():
            text = " ".join(str(row[col]) for col in text_cols if col in row)
            skills = extract_skills(text, skills_db)
            trends.setdefault(str(row['period']), []).extend(skills)
        skill_counts = {period: Counter(skills) for period, skills in trends.items()}
    else:
        # No date column, just count overall
        all_text = " ".join(df[col].astype(str).sum() for col in text_cols if col in df.columns)
        skill_hits = extract_skills(all_text, skills_db)
        skill_counts = {"all": Counter(skill_hits)}
    return skill_counts

def plot_trends(skill_counts, top_n=10):
    # Flatten all skill counts
    all_skills = Counter([s for skills in skill_counts.values() for s in skills])
    top_skills = all_skills.most_common(top_n)
    if not top_skills:
        st.info("No skills found in the selected articles.")
        return
    skill_names, skill_freqs = zip(*top_skills)
    fig = px.bar(
        x=skill_names,
        y=skill_freqs,
        labels={'x': 'Skill', 'y': 'Mentions'},
        title="Top Skills in Selected Blogs",
        color=skill_names,
        text=skill_freqs
    )
    fig.update_layout(xaxis_title="Skill", yaxis_title="Mentions", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def fetch_latest_articles(blog_url, max_articles=5):
    articles = []
    try:
        r = requests.get(blog_url, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        # Qiita
        if "qiita.com" in blog_url:
            links = soup.select("a[href^='/']")  # all internal links
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/") and "/items/" in a.get("href", "")]
            for url in article_links[:max_articles]:
                full_url = "https://qiita.com" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # Zenn
        elif "zenn.dev" in blog_url:
            links = soup.select("a[href^='/articles/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/articles/")]
            for url in article_links[:max_articles]:
                full_url = "https://zenn.dev" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # Japan Dev Blog
        elif "japan-dev.com" in blog_url:
            links = soup.select("a[href^='/blog/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/blog/") and len(a.get("href", "")) > 6]
            for url in article_links[:max_articles]:
                full_url = "https://japan-dev.com" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # Hatena Developer Blog
        elif "hatenastaff.com" in blog_url:
            links = soup.select("h2.entry-title a")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("https://developer.hatenastaff.com/entry/")]
            for url in article_links[:max_articles]:
                entry = fetch_blog(url)
                if entry: articles.append(entry)
        # TechCrunch Japan
        elif "techcrunch.com" in blog_url:
            links = soup.select("a.post-block__title__link")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("https://jp.techcrunch.com/20")]
            for url in article_links[:max_articles]:
                entry = fetch_blog(url)
                if entry: articles.append(entry)
        # CodeIQ Magazine
        elif "codeiq.jp" in blog_url:
            links = soup.select("h3.entry-title a")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("https://codeiq.jp/magazine/")]
            for url in article_links[:max_articles]:
                entry = fetch_blog(url)
                if entry: articles.append(entry)
        # ITmedia News
        elif "itmedia.co.jp" in blog_url:
            links = soup.select("a[href^='https://www.itmedia.co.jp/news/articles/']")
            article_links = [a.get("href") for a in links if "/news/articles/" in a.get("href", "")]
            for url in article_links[:max_articles]:
                entry = fetch_blog(url)
                if entry: articles.append(entry)
        # Publickey
        elif "publickey1.jp" in blog_url:
            links = soup.select("h2.entry-title a")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("https://www.publickey1.jp/blog/")]
            for url in article_links[:max_articles]:
                entry = fetch_blog(url)
                if entry: articles.append(entry)
        # Findy Engineer Lab
        elif "findy-code.io" in blog_url:
            links = soup.select("a[href^='/engineer-lab/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/engineer-lab/") and len(a.get("href", "")) > 15]
            for url in article_links[:max_articles]:
                full_url = "https://findy-code.io" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # LIG Blog
        elif "liginc.co.jp" in blog_url:
            links = soup.select("a[href^='/blog/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/blog/") and len(a.get("href", "")) > 6]
            for url in article_links[:max_articles]:
                full_url = "https://liginc.co.jp" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # Mercari Engineering Blog
        elif "engineering.mercari.com" in blog_url:
            links = soup.select("a[href^='/blog/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/blog/") and len(a.get("href", "")) > 6]
            for url in article_links[:max_articles]:
                full_url = "https://engineering.mercari.com" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # LINE Engineering Blog
        elif "engineering.linecorp.com" in blog_url:
            links = soup.select("a[href^='/ja/blog/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/ja/blog/") and len(a.get("href", "")) > 9]
            for url in article_links[:max_articles]:
                full_url = "https://engineering.linecorp.com" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # CyberAgent Developers Blog
        elif "developers.cyberagent.co.jp" in blog_url:
            links = soup.select("a[href^='/blog/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/blog/") and len(a.get("href", "")) > 6]
            for url in article_links[:max_articles]:
                full_url = "https://developers.cyberagent.co.jp" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
        # Yahoo! JAPAN Tech Blog
        elif "techblog.yahoo.co.jp" in blog_url:
            links = soup.select("a[href^='/entry/']")
            article_links = [a.get("href") for a in links if a.get("href", "").startswith("/entry/")]
            for url in article_links[:max_articles]:
                full_url = "https://techblog.yahoo.co.jp" + url
                entry = fetch_blog(full_url)
                if entry: articles.append(entry)
    except Exception as e:
        st.warning(f"Failed to fetch articles from {blog_url}: {e}")
    if not articles:
        st.info("No articles found. The blog's structure may have changed or there are no recent posts.")
    return articles

JANOME = Tokenizer()

# --- Streamlit UI ---
st.set_page_config("JP/EN Skill Trend Analyzer", layout="wide")
st.title("🇯🇵 Japanese Tech Blog Skill Trend Analyzer")

skills_db = load_skills_db("skills_dict.json")

with st.sidebar:
    st.header("Select Blog Source")
    selected_blog = st.selectbox("Choose a tech blog", list(JP_TECH_BLOGS.keys()))
    max_articles = st.slider("Number of articles", 3, 15, 5)
    st.markdown("---")
    st.markdown("Or analyze a single blog post:")
    single_blog_url = st.text_input("Blog URL", value="https://japan-dev.com/blog/vuejs-in-japan")
    analyze_single = st.button("Analyze Single Blog")

tab1, tab2 = st.tabs(["Top Blogs Trend", "Single Blog Analysis"])

with tab1:
    st.subheader(f"Latest Articles from {selected_blog}")
    if st.button("Fetch Latest Articles"):
        blog_url = JP_TECH_BLOGS[selected_blog]
        articles = fetch_latest_articles(blog_url, max_articles=max_articles)
        if articles:
            blog_df = pd.DataFrame(articles)
            st.dataframe(blog_df[["title", "url"]], use_container_width=True)
            st.markdown("### Skill Trend Chart")
            skill_counts = analyze_trends(blog_df, ['title','content'], None, skills_db)
            plot_trends(skill_counts)
            st.markdown("### Top Blog Titles")
            for i, row in blog_df.iterrows():
                st.markdown(f"- [{row['title']}]({row['url']})")
        else:
            st.error("No articles found or failed to fetch. Try another blog or check your connection.")

with tab2:
    st.subheader("Single Blog Post Analysis")
    if analyze_single and single_blog_url:
        entry = fetch_blog(single_blog_url)
        if entry:
            st.markdown(f"#### [{entry['title']}]({entry['url']})")
            st.write(entry['content'][:800] + "..." if len(entry['content']) > 800 else entry['content'])
            blog_df = pd.DataFrame([entry])
            skill_counts = analyze_trends(blog_df, ['title','content'], None, skills_db)
            st.markdown("### Skill Trend Chart")
            plot_trends(skill_counts)
            st.markdown("### Skill Counts")
            st.json({k: dict(v.most_common(10)) for k, v in skill_counts.items()})
        else:
            st.error("Failed to fetch blog content. Please check the URL or try another blog.")
