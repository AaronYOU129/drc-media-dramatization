"""
Purpose:
This script cleans and subsets a merged Reuters dataset to produce a
DRC-focused Reuters article file. It (1) fills missing titles by extracting
a readable title from the Reuters URL slug, (2) flags and filters articles
related to the Democratic Republic of the Congo (DRC) using keyword matching,
and (3) adds a `year` variable derived from the article date.

Design choices:
- Use the processed, combined Reuters dataset as input (2018–2024 merged file)
- If `title` is missing/blank, derive `title_clean` from the URL using regex
  (supports common Reuters URL patterns, including slug + “-idXXXX” forms)
- Identify DRC-related content via case-insensitive keyword search on `title_clean`
- Parse `date` with `errors='coerce'` to safely handle malformed timestamps
- Add `year` from the parsed `date` for quick aggregation and checks

Output:
- CSV file containing DRC-related Reuters articles with extra columns:
  `title_clean`, `is_drc`, and `year`
- File saved to: data/processed/reuters_drc_clean.csv
"""


import pandas as pd
import re
import os

# ============================================================
# Load
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')

INPUT_PATH = os.path.join(processed_dir, 'rtr_combined_2018_2024.csv')
OUTPUT_PATH = os.path.join(processed_dir, 'reuters_drc_clean.csv')

reuters = pd.read_csv(INPUT_PATH)
print(f"Loaded: {len(reuters)} rows")

# ============================================================
# Extract titles from URLs
# ============================================================
def extract_title_from_url(url):
    """Extract readable title from Reuters URL slug"""
    if pd.isna(url):
        return ''
    
    # Pattern 1: /article/topic/slug-idXXXX
    match = re.search(r'/([^/]+)-id[A-Z0-9]+', str(url))
    if match:
        slug = match.group(1)
        title = slug.replace('-', ' ')
        title = re.sub(r'\s*id[A-Z0-9]+$', '', title, flags=re.IGNORECASE)
        return title.strip()
    
    # Pattern 2: /article/topic/slug
    match = re.search(r'/article/[^/]+/([^/]+?)(?:\?|$)', str(url))
    if match:
        slug = match.group(1)
        title = slug.replace('-', ' ')
        return title.strip()
    
    return ''

# Use existing title if available, otherwise extract from URL
reuters['title_clean'] = reuters.apply(
    lambda row: row['title'] if pd.notna(row['title']) and str(row['title']).strip()
    else extract_title_from_url(row['url']),
    axis=1
)

# Check extraction success
extracted = (reuters['title_clean'] != '').sum()
print(f"Title available/extracted: {extracted}/{len(reuters)} ({extracted/len(reuters)*100:.1f}%)")

# ============================================================
# Filter DRC-related articles
# ============================================================
drc_keywords = r'congo|drc|kinshasa|goma|kabila|tshisekedi|katanga|kivu|m23|adf|lubumbashi|bukavu'
reuters['is_drc'] = reuters['title_clean'].str.lower().str.contains(drc_keywords, na=False)

reuters_drc = reuters[reuters['is_drc']].copy()
print(f"DRC-related: {len(reuters_drc)} articles")

# ============================================================
# Extract year
# ============================================================
reuters_drc['date'] = pd.to_datetime(reuters_drc['date'], errors='coerce')
reuters_drc['year'] = reuters_drc['date'].dt.year

print(f"\nYear distribution:")
print(reuters_drc['year'].value_counts().sort_index())

# ============================================================
# Save
# ============================================================
reuters_drc.to_csv(OUTPUT_PATH, index=False)
print(f"\n✓ Saved to {OUTPUT_PATH}")