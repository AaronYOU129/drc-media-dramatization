"""
Pipeline step 1: Guardian DRC news ingestion

Purpose:
- Collect all Guardian news articles mentioning the Democratic Republic of Congo (DRC)
- Retrieve full article text and metadata for downstream text analysis

Design choices:
- Use the Guardian Open Platform API for structured and reliable access to news content
- Query articles using a boolean keyword expression to maximize recall while excluding irrelevant results (e.g., Washington DC)
- Paginate through all available results to ensure full temporal coverage
- Respect API rate limits via explicit request throttling

Coverage:
- Articles published between 2018-01-01 and 2024-12-31
- Includes all pages returned by the Guardian API for the specified query

Output:
- CSV file containing Guardian article metadata and full text with columns:
  title, url, date, section, text, byline, wordcount
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
    """search Guardian articles"""
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
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

def parse_results(data):
    """parse the API response"""
    if not data or 'response' not in data:
        return []
    
    articles = []
    for item in data['response']['results']:
        article = {
            'title': item.get('webTitle', ''),
            'url': item.get('webUrl', ''),
            'date': item.get('webPublicationDate', ''),
            'section': item.get('sectionName', ''),
            'text': item.get('fields', {}).get('bodyText', ''),
            'byline': item.get('fields', {}).get('byline', ''),
            'wordcount': item.get('fields', {}).get('wordcount', 0)
        }
        articles.append(article)
    
    return articles

# ==========================================
# main program: scrape all articles from 2018 to 2024
# ==========================================
print("🚀 Starting Guardian DRC Article Scraper")
print("=" * 80)

# search parameters
query = '("Democratic Republic of Congo" OR "DRC" OR "DR Congo") AND NOT "Washington DC"'
from_date = '2018-01-01'
to_date = '2024-12-31'

# first request: get the total number of pages
print("🔍 Fetching article count...")
first_data = search_guardian(query, from_date, to_date, page=1)

if not first_data:
    print("❌ Failed to connect to Guardian API!")
    print("💡 Please check:")
    print("   1. Your API key is correct")
    print("   2. You have internet connection")
    print("   3. Get API key at: https://open-platform.theguardian.com/access/")
    exit()

total_articles = first_data['response']['total']
total_pages = first_data['response']['pages']

print(f"✅ Found {total_articles} articles across {total_pages} pages")
print(f"⏱️  Estimated time: ~{total_pages * 1.5 / 60:.1f} minutes")
print(f"📅 Date range: {from_date} to {to_date}")
print("=" * 80)

# store all articles
all_articles = []
failed_pages = []

# loop through each page
start_time = time.time()

for page in range(1, total_pages + 1):
    print(f"📄 Page {page}/{total_pages}...", end=" ", flush=True)
    
    try:
        data = search_guardian(query, from_date, to_date, page=page)
        
        if data:
            articles = parse_results(data)
            all_articles.extend(articles)
            print(f"✅ Got {len(articles)} articles | Total: {len(all_articles)}")
        else:
            print(f"❌ Failed")
            failed_pages.append(page)
        
        # avoid exceeding API limits (max 12 requests per second)
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        failed_pages.append(page)
        time.sleep(2)

elapsed_time = time.time() - start_time

print("=" * 80)
print(f"✅ Scraping complete!")
print(f"⏱️  Time elapsed: {elapsed_time / 60:.1f} minutes")
print(f"📊 Total articles collected: {len(all_articles)}/{total_articles}")

if failed_pages:
    print(f"⚠️  Failed pages: {failed_pages}")

# ==========================================
# save data
# ==========================================
print("\n💾 Saving data...")

df = pd.DataFrame(all_articles)

# generate file path relative to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
output_dir = os.path.join(project_root, 'data', 'raw')
os.makedirs(output_dir, exist_ok=True)

csv_filename = os.path.join(output_dir, 'gdn_api_2018_2024.csv')

# save CSV (using utf-8-sig to avoid Excel乱码)
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

# get the full path
full_path = os.path.abspath(csv_filename)
file_size_mb = os.path.getsize(csv_filename) / (1024 * 1024)

print("=" * 80)
print("✅ FILE SAVED SUCCESSFULLY!")
print(f"📁 File name: {csv_filename}")
print(f"📂 Full path: {full_path}")
print(f"📊 File size: {file_size_mb:.2f} MB")
print("=" * 80)

# ==========================================
# data summary
# ==========================================
print("\n📈 DATA SUMMARY:")
print("-" * 80)
print(f"Total articles: {len(df)}")
print(f"Date range: {df['date'].min()[:10]} to {df['date'].max()[:10]}")
print(f"Columns: {list(df.columns)}")

# count words
df['wordcount'] = pd.to_numeric(df['wordcount'], errors='coerce').fillna(0).astype(int)
print(f"Average word count: {df['wordcount'].mean():.0f} words")
print(f"Total words: {df['wordcount'].sum():,} words")
print(f"Longest article: {df['wordcount'].max()} words")
print(f"Shortest article: {df['wordcount'].min()} words")

# count section distribution
print(f"\nTop 5 sections:")
section_counts = df['section'].value_counts().head(5)
for section, count in section_counts.items():
    print(f"  - {section}: {count} articles")

# check text data
texts_with_content = df['text'].str.len() > 100
print(f"\nArticles with text content (>100 chars): {texts_with_content.sum()}")
print(f"Articles missing text: {(~texts_with_content).sum()}")

print("-" * 80)

# ==========================================
# display sample articles
# ==========================================
print("\n📝 SAMPLE ARTICLES (First 3):")
print("=" * 80)

for i, row in df.head(3).iterrows():
    print(f"\n[{i+1}] {row['title']}")
    print(f"    Date: {row['date'][:10]}")
    print(f"    Section: {row['section']}")
    print(f"    Author: {row['byline']}")
    print(f"    Words: {row['wordcount']}")
    print(f"    URL: {row['url']}")
    print(f"    Text preview: {row['text'][:200]}...")

print("\n" + "=" * 80)
print("🎉 ALL DONE!")
print(f"📂 Your data is saved at: {full_path}")
print("=" * 80)
