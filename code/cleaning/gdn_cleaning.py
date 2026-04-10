"""
Purpose:    Clean Guardian API data and classify articles into topic categories.
            Topic classification uses rule-based keyword matching with a priority
            order (Sports > Conflict > Health > Environment > Economy > Politics)
            to assign each article a single dominant topic. Conflict-related
            coverage is the primary focus for downstream dramatization analysis.
Inputs:     data/raw/gdn_api_2018_2024.csv — raw Guardian API output.
Outputs:    data/processed/guardian_drc_clean.csv — cleaned articles with added
            columns: year, full_text, topic.
Key Steps:  Load raw data -> extract year -> combine title+text into full_text ->
            classify topics via keyword matching -> save.
How to Run: python code/cleaning/gdn_cleaning.py
"""

import pandas as pd
import re
import os


def classify_topic(row):
    """Assign a single topic category based on keyword priority.

    Priority order matters: Sports is checked first to avoid misclassifying
    sports violence as Conflict. Only the first 500 chars of article text
    are checked to keep classification fast on large datasets.
    """
    title = str(row['title']).lower()
    text = str(row['text']).lower()[:500]
    section = str(row.get('section', '')).lower()

    if section == 'football' or 'football' in title or 'fifa' in title:
        return 'Sports'

    conflict_kw = r'war|conflict|rebel|m23|militia|attack|kill|violence|fighting|troops|soldier|massacre|refugee|displaced|humanitarian|crisis'
    if re.search(conflict_kw, title) or re.search(conflict_kw, text):
        return 'Conflict'

    health_kw = r'ebola|mpox|covid|health|disease|outbreak|vaccine|hospital'
    if re.search(health_kw, title) or re.search(health_kw, text):
        return 'Health'

    if section == 'environment' or 'climate' in title or 'forest' in title:
        return 'Environment'

    econ_kw = r'econom|business|trade|investment|mining|cobalt|copper'
    if section == 'business' or re.search(econ_kw, title):
        return 'Economy'

    if 'election' in title or 'president' in title or 'government' in title:
        return 'Politics'

    return 'Other'


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    raw_dir = os.path.join(project_root, 'data', 'raw')
    processed_dir = os.path.join(project_root, 'data', 'processed')

    input_path = os.path.join(raw_dir, 'gdn_api_2018_2024.csv')
    output_path = os.path.join(processed_dir, 'guardian_drc_clean.csv')

    guardian = pd.read_csv(input_path)
    print(f"Loaded: {len(guardian)} articles")
    print(f"Average word count: {guardian['wordcount'].mean():.0f}")

    guardian['year'] = pd.to_datetime(guardian['date']).dt.year
    guardian['text'] = guardian['text'].fillna('').astype(str)
    guardian['title'] = guardian['title'].fillna('').astype(str)
    guardian['full_text'] = guardian['title'] + ' ' + guardian['text']

    guardian['topic'] = guardian.apply(classify_topic, axis=1)

    print(f"\nTopic distribution:")
    print(guardian['topic'].value_counts())
    print(f"\nYear distribution:")
    print(guardian['year'].value_counts().sort_index())

    guardian.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
