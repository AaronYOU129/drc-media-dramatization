"""
Purpose:
This script cleans Guardian API article data and classifies articles into
broad topical categories, with a focus on identifying conflict-related
coverage relevant to the Democratic Republic of the Congo (DRC). It prepares
a processed Guardian dataset for downstream text analysis.

Design choices:
- Use the raw Guardian API dataset (2018–2024) as input
- Parse publication dates to extract a `year` variable
- Construct a `full_text` field by combining title and article text
- Classify articles into topic categories using rule-based keyword matching
  on titles, truncated article text, and section metadata
- Prioritize conflict-related keywords commonly used in reporting on violence,
  displacement, and humanitarian crises

Output:
- CSV file containing cleaned Guardian articles with added variables:
  `year`, `full_text`, and `topic`
- File saved to: data/processed/guardian_drc_clean.csv
- Coverage: 2018–2024
"""


import pandas as pd
import re
import os

# ============================================================
# Load
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
raw_dir = os.path.join(project_root, 'data', 'raw')
processed_dir = os.path.join(project_root, 'data', 'processed')

INPUT_PATH = os.path.join(raw_dir, 'gdn_api_2018_2024.csv')
OUTPUT_PATH = os.path.join(processed_dir, 'guardian_drc_clean.csv')

guardian = pd.read_csv(INPUT_PATH)
print(f"Loaded: {len(guardian)} articles")
print(f"Average word count: {guardian['wordcount'].mean():.0f}")

# ============================================================
# Basic cleaning
# ============================================================
guardian['year'] = pd.to_datetime(guardian['date']).dt.year
guardian['text'] = guardian['text'].fillna('').astype(str)
guardian['title'] = guardian['title'].fillna('').astype(str)
guardian['full_text'] = guardian['title'] + ' ' + guardian['text']

# ============================================================
# Classify topics
# ============================================================
def classify_topic(row):
    """Classify article into topic categories"""
    title = str(row['title']).lower()
    text = str(row['text']).lower()[:500]
    section = str(row.get('section', '')).lower()
    
    # Sports
    if section == 'football' or 'football' in title or 'fifa' in title:
        return 'Sports'
    
    # Conflict
    conflict_kw = r'war|conflict|rebel|m23|militia|attack|kill|violence|fighting|troops|soldier|massacre|refugee|displaced|humanitarian|crisis'
    if re.search(conflict_kw, title) or re.search(conflict_kw, text):
        return 'Conflict'
    
    # Health
    health_kw = r'ebola|mpox|covid|health|disease|outbreak|vaccine|hospital'
    if re.search(health_kw, title) or re.search(health_kw, text):
        return 'Health'
    
    # Environment
    if section == 'environment' or 'climate' in title or 'forest' in title:
        return 'Environment'
    
    # Economy
    econ_kw = r'econom|business|trade|investment|mining|cobalt|copper'
    if section == 'business' or re.search(econ_kw, title):
        return 'Economy'
    
    # Politics
    if 'election' in title or 'president' in title or 'government' in title:
        return 'Politics'
    
    return 'Other'

guardian['topic'] = guardian.apply(classify_topic, axis=1)

print(f"\nTopic distribution:")
print(guardian['topic'].value_counts())

# ============================================================
# Year distribution
# ============================================================
print(f"\nYear distribution:")
print(guardian['year'].value_counts().sort_index())

# ============================================================
# Save
# ============================================================
guardian.to_csv(OUTPUT_PATH, index=False)
print(f"\n✓ Saved to {OUTPUT_PATH}")