"""
Purpose:    Clean the combined Reuters dataset and filter to DRC-related articles.
            Many GDELT entries lack titles, so titles are extracted from Reuters URL
            slugs using regex. DRC relevance is determined by keyword matching on
            the cleaned title field.
Inputs:     data/processed/rtr_combined_2018_2024.csv — merged Reuters data.
Outputs:    data/processed/reuters_drc_clean.csv — DRC-filtered articles with
            columns: title, date, url, title_clean, is_drc, year.
Key Steps:  Load combined data -> extract missing titles from URL slugs -> flag
            DRC-related articles via keyword regex -> extract year -> save.
How to Run: python code/cleaning/rtr_clean_filter_drc.py
"""

import pandas as pd
import re
import os


DRC_KEYWORDS = r'congo|drc|kinshasa|goma|kabila|tshisekedi|katanga|kivu|m23|adf|lubumbashi|bukavu'


def extract_title_from_url(url):
    """Extract a readable title from a Reuters URL slug.

    Handles two common URL patterns:
      /article/topic/slug-idXXXX  (older Reuters format)
      /article/topic/slug         (newer format)
    """
    if pd.isna(url):
        return ''

    url_str = str(url)

    # Pattern 1: slug ending with -idXXXX (older Reuters URLs)
    match = re.search(r'/([^/]+)-id[A-Z0-9]+', url_str)
    if match:
        slug = match.group(1)
        title = slug.replace('-', ' ')
        title = re.sub(r'\s*id[A-Z0-9]+$', '', title, flags=re.IGNORECASE)
        return title.strip()

    # Pattern 2: clean slug after /article/topic/
    match = re.search(r'/article/[^/]+/([^/]+?)(?:\?|$)', url_str)
    if match:
        return match.group(1).replace('-', ' ').strip()

    return ''


def fill_missing_titles(df):
    """Use existing title if available; otherwise extract from URL."""
    df['title_clean'] = df.apply(
        lambda row: row['title'] if pd.notna(row['title']) and str(row['title']).strip()
        else extract_title_from_url(row['url']),
        axis=1,
    )
    extracted = (df['title_clean'] != '').sum()
    print(f"Title available/extracted: {extracted}/{len(df)} ({extracted / len(df) * 100:.1f}%)")
    return df


def filter_drc_articles(df):
    """Flag and filter articles whose title matches DRC-related keywords."""
    df['is_drc'] = df['title_clean'].str.lower().str.contains(DRC_KEYWORDS, na=False)
    df_drc = df[df['is_drc']].copy()
    print(f"DRC-related: {len(df_drc)} articles")
    return df_drc


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    processed_dir = os.path.join(project_root, 'data', 'processed')

    input_path = os.path.join(processed_dir, 'rtr_combined_2018_2024.csv')
    output_path = os.path.join(processed_dir, 'reuters_drc_clean.csv')

    reuters = pd.read_csv(input_path)
    print(f"Loaded: {len(reuters)} rows")

    reuters = fill_missing_titles(reuters)
    reuters_drc = filter_drc_articles(reuters)

    reuters_drc['date'] = pd.to_datetime(reuters_drc['date'], errors='coerce')
    reuters_drc['year'] = reuters_drc['date'].dt.year

    print(f"\nYear distribution:")
    print(reuters_drc['year'].value_counts().sort_index())

    reuters_drc.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
