# ============================================================
# llm_validation_deepseek.py
# Validate dictionary-based dramatization with DeepSeek
# ============================================================

import pandas as pd
from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
import time
import re
import os
from dotenv import load_dotenv

# ============================================================
# Config
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')
output_dir = os.path.join(project_root, 'output')

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, '.env'))

INPUT_PATH = os.path.join(processed_dir, 'guardian_conflict_analyzed.csv')
OUTPUT_PATH = os.path.join(output_dir, 'llm_validation_results.csv')
SAMPLE_SIZE = None  # Set to None to process all articles, or a number to sample

# DeepSeek API - load from environment variable
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found. Please set it in .env file.")

# ============================================================
# Prompt
# ============================================================
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

# ============================================================
# DeepSeek Scoring Function
# ============================================================
def score_with_deepseek(text, client):
    """Score article using DeepSeek"""
    # Truncate to ~2000 words to save tokens
    words = text.split()[:2000]
    truncated = ' '.join(words)
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(article_text=truncated)
        }]
    )
    return response.choices[0].message.content

# ============================================================
# Parse LLM Response
# ============================================================
def parse_response(response):
    """Extract scores from LLM response"""
    scores = {}
    patterns = {
        'emotional': r'EMOTIONAL:\s*(\d)',
        'personal': r'PERSONAL:\s*(\d)',
        'narrative': r'NARRATIVE:\s*(\d)',
        'firstperson': r'FIRSTPERSON:\s*(\d)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, response, re.IGNORECASE)
        scores[f'llm_{key}'] = int(match.group(1)) if match else None
    
    # Total
    valid = [v for v in scores.values() if v is not None]
    scores['llm_total'] = sum(valid) if len(valid) == 4 else None
    
    return scores

# ============================================================
# Main
# ============================================================
def main():
    # Load data
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df)} articles")

    # Sample or use all
    if SAMPLE_SIZE is None:
        sample = df.copy()
        print(f"Processing all {len(sample)} articles")
    else:
        sample = df.sample(n=SAMPLE_SIZE, random_state=42).copy()
        print(f"Sampled {len(sample)} articles for validation")

    total = len(sample)

    # Initialize DeepSeek client
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )

    # Score each article
    results = []
    for i, (idx, row) in enumerate(sample.iterrows()):
        try:
            response = score_with_deepseek(row['full_text'], client)
            scores = parse_response(response)
            scores['idx'] = idx
            results.append(scores)
            print(f"  [{i+1}/{total}] Scored")
            time.sleep(0.3)  # Rate limiting
        except Exception as e:
            print(f"  [{i+1}/{total}] Error: {e}")
            continue
    
    # Merge results
    results_df = pd.DataFrame(results).set_index('idx')
    sample = sample.join(results_df)
    
    # ============================================================
    # Validation: Compare LLM vs Dictionary
    # ============================================================
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    
    # Correlation
    corr_total = sample['llm_total'].corr(sample['drama_binary'])
    print(f"\nOverall correlation (LLM vs Dictionary): {corr_total:.3f}")
    
    # Per-dimension correlation
    dims = ['emotional', 'personal', 'narrative', 'firstperson']
    print("\nPer-dimension correlations:")
    for dim in dims:
        llm_col = f'llm_{dim}'
        dict_col = f'has_{dim}'
        if llm_col in sample.columns and dict_col in sample.columns:
            corr = sample[llm_col].corr(sample[dict_col])
            print(f"  {dim}: {corr:.3f}")
    
    # Agreement rate
    sample['llm_high'] = (sample['llm_total'] >= 6).astype(int)
    sample['dict_high'] = (sample['drama_binary'] >= 2).astype(int)
    agreement = (sample['llm_high'] == sample['dict_high']).mean()
    print(f"\nBinary agreement rate: {agreement:.1%}")
    
    # Save
    sample.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✓ Results saved to {OUTPUT_PATH}")
    
    # Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    if corr_total > 0.7:
        print("✓ Strong correlation - dictionary method validated")
    elif corr_total > 0.5:
        print("○ Moderate correlation - dictionary method reasonably validated")
    else:
        print("✗ Weak correlation - review methodology")

if __name__ == '__main__':
    main()