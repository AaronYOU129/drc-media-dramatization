"""
Purpose:    Collect all Guardian articles mentioning the DRC (2018-2024) via the
            Guardian Open Platform API. Uses boolean keyword query to maximize recall
            while excluding false positives (e.g., "Washington DC"). Paginates through
            all results with rate-limit throttling.
Inputs:     GUARDIAN_API_KEY environment variable (via .env file).
Outputs:    data/raw/gdn_api_2018_2024.csv — columns: title, url, date, section,
            text, byline, wordcount. Encoded as UTF-8-sig for Excel compatibility.
Key Steps:  Query API page by page -> parse JSON responses -> collect into DataFrame
            -> deduplicate and save.
How to Run: python code/scraping/gdn_api_2018_2024.py
"""



import requests
import pandas as pd
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# ==========================================
# settings
# ==========================================
API_KEY = os.getenv("GUARDIAN_API_KEY")
BASE_URL = "https://content.guardianapis.com/search"

# ==========================================
# functions
# ==========================================
def search_guardian(query, from_date, to_date, page=1, page_size=50):
    """Send a single paginated request to the Guardian API."""
    params = {
        'q': query,
        'from-date': from_date,
        'to-date': to_date,
        'page': page,
        'page-size': page_size,
        'show-fields': 'headline,bodyText,byline,wordcount',
        'api-key': API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()

    print(f"Error {response.status_code}: {response.text}")
    return None

def parse_results(data):
    """Extract article records from a Guardian API JSON response."""
    if not data or 'response' not in data:
        return []

    articles = []
    for item in data['response']['results']:
        fields = item.get('fields', {})
        articles.append({
            'title': item.get('webTitle', ''),
            'url': item.get('webUrl', ''),
            'date': item.get('webPublicationDate', ''),
            'section': item.get('sectionName', ''),
            'text': fields.get('bodyText', ''),
            'byline': fields.get('byline', ''),
            'wordcount': fields.get('wordcount', 0),
        })

    return articles

def scrape_all_pages(query, from_date, to_date):
    """Paginate through the Guardian API and collect all matching articles."""
    first_data = search_guardian(query, from_date, to_date, page=1)
    if not first_data:
        print("Failed to connect to Guardian API. Check your API key and connection.")
        return []

    total_articles = first_data['response']['total']
    total_pages = first_data['response']['pages']
    print(f"Found {total_articles} articles across {total_pages} pages")

    all_articles = parse_results(first_data)
    failed_pages = []

    for page in range(2, total_pages + 1):
        print(f"Page {page}/{total_pages}...", end=" ", flush=True)
        try:
            data = search_guardian(query, from_date, to_date, page=page)
            if data:
                articles = parse_results(data)
                all_articles.extend(articles)
                print(f"Got {len(articles)} articles | Total: {len(all_articles)}")
            else:
                print("Failed")
                failed_pages.append(page)
            # Respect API rate limit (max 12 requests/second)
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            failed_pages.append(page)
            time.sleep(2)

    if failed_pages:
        print(f"Failed pages: {failed_pages}")

    return all_articles


def save_results(all_articles):
    """Save collected articles to CSV and print a summary."""
    df = pd.DataFrame(all_articles)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'gdn_api_2018_2024.csv')
    # UTF-8-sig encoding to avoid garbled text when opening in Excel
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    file_size_mb = os.path.getsize(csv_path) / (1024 * 1024)
    print(f"Saved {len(df)} articles to {csv_path} ({file_size_mb:.2f} MB)")

    print_summary(df)
    return df


def print_summary(df):
    """Print descriptive statistics about the collected dataset."""
    print("-" * 60)
    print(f"Total articles: {len(df)}")
    print(f"Date range: {df['date'].min()[:10]} to {df['date'].max()[:10]}")

    df['wordcount'] = pd.to_numeric(df['wordcount'], errors='coerce').fillna(0).astype(int)
    print(f"Average word count: {df['wordcount'].mean():.0f}")
    print(f"Total words: {df['wordcount'].sum():,}")

    print("\nTop 5 sections:")
    for section, count in df['section'].value_counts().head(5).items():
        print(f"  {section}: {count}")

    texts_with_content = df['text'].str.len() > 100
    print(f"\nArticles with text (>100 chars): {texts_with_content.sum()}")
    print(f"Articles missing text: {(~texts_with_content).sum()}")
    print("-" * 60)


def main():
    query = '("Democratic Republic of Congo" OR "DRC" OR "DR Congo") AND NOT "Washington DC"'
    from_date = '2018-01-01'
    to_date = '2024-12-31'

    print("Starting Guardian DRC Article Scraper")
    print(f"Date range: {from_date} to {to_date}")

    all_articles = scrape_all_pages(query, from_date, to_date)
    if all_articles:
        save_results(all_articles)


if __name__ == "__main__":
    main()
