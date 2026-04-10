"""
Purpose:    Validate the dictionary-based dramatization scores against LLM ratings.
            Each Guardian conflict article is scored by DeepSeek on the same four
            dimensions (emotional, personal, narrative, first-person) using a
            structured prompt. Results are compared via correlation and binary
            agreement to assess dictionary method validity.
Inputs:     data/processed/guardian_conflict_analyzed.csv — articles with dictionary scores.
            DEEPSEEK_API_KEY environment variable (via .env file).
Outputs:    output/llm_validation_results.csv — merged dictionary + LLM scores.
Key Steps:  Load analyzed articles -> send each to DeepSeek with scoring prompt ->
            parse structured response -> compute correlations and agreement -> save.
How to Run: python code/analysis/llm_validation.py
"""

import pandas as pd
from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
import time
import re
import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')
output_dir = os.path.join(project_root, 'output')

load_dotenv(os.path.join(project_root, '.env'))

INPUT_PATH = os.path.join(processed_dir, 'guardian_conflict_analyzed.csv')
OUTPUT_PATH = os.path.join(output_dir, 'llm_validation_results.csv')
SAMPLE_SIZE = None  # None = process all articles; set a number to sample

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found. Please set it in .env file.")

# ---------------------------------------------------------------------------
# Scoring prompt
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """You are a media analyst evaluating news dramatization.

Rate this article on 4 dimensions (each 0-3):

1. EMOTIONAL INTENSITY (0-3)
   0 = No emotional words
   1 = Few (1-2) emotional words (e.g., "tragic", "horrific")
   2 = Several (3-5) emotional words
   3 = Many (6+) emotional words throughout

2. PERSONALIZATION (0-3)
   0 = No individual victims/families mentioned
   1 = Brief mention of victims/families
   2 = Multiple references to specific individuals
   3 = Extensive focus on personal stories

3. NARRATIVE FRAMING (0-3)
   0 = No quotes or testimony
   1 = 1-2 brief quotes
   2 = Several quotes with "told", "recalled"
   3 = Heavy use of first-hand accounts

4. FIRST-PERSON VOICE (0-3)
   0 = No first-person (I, me, my, we, our)
   1 = Minimal first-person
   2 = Moderate first-person
   3 = Extensive first-person narrative

Article:
{article_text}

Respond in this exact format ONLY (no explanation):
EMOTIONAL: [0-3]
PERSONAL: [0-3]
NARRATIVE: [0-3]
FIRSTPERSON: [0-3]
"""

DIMENSIONS = ['emotional', 'personal', 'narrative', 'firstperson']


def score_with_deepseek(text, client):
    """Send article text to DeepSeek and return the raw response string."""
    # Truncate to ~2000 words to stay within token limits
    truncated = ' '.join(text.split()[:2000])

    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(article_text=truncated),
        }],
    )
    return response.choices[0].message.content


def parse_response(response):
    """Extract dimension scores from the structured LLM response."""
    scores = {}
    patterns = {
        'emotional': r'EMOTIONAL:\s*(\d)',
        'personal': r'PERSONAL:\s*(\d)',
        'narrative': r'NARRATIVE:\s*(\d)',
        'firstperson': r'FIRSTPERSON:\s*(\d)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, response, re.IGNORECASE)
        scores[f'llm_{key}'] = int(match.group(1)) if match else None

    valid = [v for v in scores.values() if v is not None]
    scores['llm_total'] = sum(valid) if len(valid) == 4 else None
    return scores


def print_validation_results(sample):
    """Print correlation and agreement statistics."""
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    corr_total = sample['llm_total'].corr(sample['drama_binary'])
    print(f"\nOverall correlation (LLM vs Dictionary): {corr_total:.3f}")

    print("\nPer-dimension correlations:")
    for dim in DIMENSIONS:
        llm_col = f'llm_{dim}'
        dict_col = f'has_{dim}'
        if llm_col in sample.columns and dict_col in sample.columns:
            corr = sample[llm_col].corr(sample[dict_col])
            print(f"  {dim}: {corr:.3f}")

    sample['llm_high'] = (sample['llm_total'] >= 6).astype(int)
    sample['dict_high'] = (sample['drama_binary'] >= 2).astype(int)
    agreement = (sample['llm_high'] == sample['dict_high']).mean()
    print(f"\nBinary agreement rate: {agreement:.1%}")

    if corr_total > 0.7:
        print("\nStrong correlation — dictionary method validated")
    elif corr_total > 0.5:
        print("\nModerate correlation — dictionary method reasonably validated")
    else:
        print("\nWeak correlation — review methodology")


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df)} articles")

    if SAMPLE_SIZE is None:
        sample = df.copy()
        print(f"Processing all {len(sample)} articles")
    else:
        sample = df.sample(n=SAMPLE_SIZE, random_state=42).copy()
        print(f"Sampled {len(sample)} articles for validation")

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    results = []
    total = len(sample)
    for i, (idx, row) in enumerate(sample.iterrows()):
        try:
            response = score_with_deepseek(row['full_text'], client)
            scores = parse_response(response)
            scores['idx'] = idx
            results.append(scores)
            print(f"  [{i + 1}/{total}] Scored")
            time.sleep(0.3)
        except Exception as e:
            print(f"  [{i + 1}/{total}] Error: {e}")
            continue

    results_df = pd.DataFrame(results).set_index('idx')
    sample = sample.join(results_df)

    print_validation_results(sample)

    os.makedirs(output_dir, exist_ok=True)
    sample.to_csv(OUTPUT_PATH, index=False)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
