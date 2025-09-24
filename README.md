# JP Skill Trends: Japanese Tech Blog Skill Trend Analyzer

Analyze and visualize trending tech skills from top Japanese tech blogs, in both Japanese and English!

## Features

- **Fetch latest articles** from popular Japanese tech blogs (Qiita, Zenn, Japan Dev Blog, Hatena, TechCrunch Japan, and more).
- **Extract and visualize trending skills** (Python, Java, React, AWS, etc.) using Japanese and English keywords.
- **Analyze a single blog post** by URL.
- **Interactive bar charts** for top skills using Plotly.
- **Easy-to-use Streamlit UI** with sidebar controls and tabs.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hritik1804/jp_skill_trends.git
cd jp_skill_trends
```

### 2. Install dependencies

It’s recommended to use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

Open your browser at [http://localhost:8501](http://localhost:8501).

## Usage

- **Sidebar:** Select a blog and number of articles, or enter a single blog post URL.
- **Top Blogs Trend Tab:** Fetch and analyze the latest articles from the selected blog.
- **Single Blog Analysis Tab:** Analyze a single blog post by URL.
- **Skill Trend Chart:** See which tech skills are trending in the selected articles.
- **Top Blog Titles:** Clickable links to the fetched articles.

## Supported Blogs

- Qiita
- Zenn
- Japan Dev Blog
- Hatena Developer Blog
- TechCrunch Japan
- CodeIQ Magazine
- ITmedia News
- Publickey
- Findy Engineer Lab
- LIG Blog
- Mercari Engineering Blog
- LINE Engineering Blog
- CyberAgent Developers Blog
- Yahoo! JAPAN Tech Blog

## Customization

- **Add more skills:** Edit `skills_dict.json` to include new keywords.
- **Add more blogs:** Update `JP_TECH_BLOGS` in `app.py` and add selectors in `fetch_latest_articles`.

## File Structure

```
jp_skill_trends/
├── app.py                # Main Streamlit app
├── blog_scrape.py        # Blog scraping logic
├── skills_dict.json      # Skill keywords (JP/EN)
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

## Notes

- Some blogs may change their HTML structure, which can affect scraping. If you see "No articles found", try another blog or update the selectors.
- For Japanese tokenization, Janome is used. You can add more advanced tokenizers if needed.

## Author

[Hritik Ranjan Sharma](https://github.com/hritik1804)

---

Feel free to open issues or pull requests for improvements!
