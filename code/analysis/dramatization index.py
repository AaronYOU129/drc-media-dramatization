"""
Purpose:    Compute dramatization scores for Guardian and Reuters conflict articles
            using a dictionary-based method across four dimensions (emotional, personal,
            narrative, first-person). Guardian articles use full text with PCA to create
            a continuous index; Reuters uses headlines only with binary indicators
            because headline text is too short for reliable word counts.
Inputs:     data/processed/guardian_drc_clean.csv — cleaned Guardian articles.
            data/processed/reuters_drc_clean.csv — cleaned Reuters articles.
Outputs:    data/processed/guardian_conflict_analyzed.csv — Guardian with dramatization scores.
            data/processed/reuters_conflict_analyzed.csv — Reuters with binary indicators.
Key Steps:  Define four-dimension dictionary -> count word occurrences per article ->
            normalize per 1000 words (Guardian) or use binary presence (Reuters) ->
            run PCA on Guardian dimensions -> save.
How to Run: python "code/analysis/dramatization index.py"
"""

import pandas as pd
import numpy as np
import re
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')

# ---------------------------------------------------------------------------
# Dramatization Dictionary (4 dimensions)
# ---------------------------------------------------------------------------
DRAMATIZATION_DICT = {
    'emotional': [
        'horrific', 'devastating', 'tragic', 'brutal', 'terrible', 'shocking',
        'heartbreaking', 'desperate', 'dire', 'grim', 'deadly', 'fatal',
        'massacre', 'slaughter', 'atrocity', 'horror', 'terror', 'suffering',
        'feared', 'afraid', 'terrified', 'haunted', 'traumatized', 'scarred',
        'crying', 'screaming', 'sobbing', 'weeping', 'trembling',
        'heartbroken', 'shattered', 'devastated', 'horrified', 'terrifying',
        'agonizing', 'unbearable', 'unimaginable', 'unspeakable', 'harrowing',
        'nightmare', 'nightmarish', 'hellish',
    ],
    'personal': [
        'victim', 'victims', 'survivor', 'survivors', 'witness', 'witnesses',
        'orphan', 'orphans', 'widow', 'widows',
        'mother', 'father', 'child', 'children', 'baby', 'babies', 'infant',
        'daughter', 'son', 'family', 'families', 'parents',
        'villager', 'villagers', 'civilian', 'civilians', 'resident', 'residents',
        'woman', 'women', 'girl', 'boy',
    ],
    'narrative': [
        'told', 'says', 'recalled', 'remembers', 'describes', 'recounts',
        'story', 'stories', 'account', 'testimony', 'voice', 'voices',
        'lived', 'experienced', 'witnessed', 'survived', 'escaped', 'fled',
    ],
    'firstperson': ['i ', ' me ', ' my ', ' we ', ' our '],
}

DIMENSIONS = list(DRAMATIZATION_DICT.keys())

# Reuters conflict keyword filter (broader than the dramatization dictionary)
REUTERS_CONFLICT_KW = (
    r'kill|killed|attack|rebel|militia|m23|war|violence|soldier|troops|'
    r'fight|clash|battle|dead|death|massacre|flee|refugee|displaced|humanitarian'
)


def count_words(text, word_list):
    """Count occurrences of dictionary words in text using word boundaries."""
    text_lower = ' ' + str(text).lower() + ' '
    total = 0
    for word in word_list:
        pattern = r'\b' + word.strip() + r'\b'
        total += len(re.findall(pattern, text_lower))
    return total


# ---------------------------------------------------------------------------
# Guardian analysis (full text -> PCA)
# ---------------------------------------------------------------------------
def analyze_guardian(input_path, output_path):
    """Score Guardian full-text articles and compute a PCA-based dramatization index."""
    guardian = pd.read_csv(input_path)
    guardian_conflict = guardian[guardian['topic'] == 'Conflict'].copy()
    print(f"Guardian conflict articles: {len(guardian_conflict)}")

    # Raw word counts per dimension
    for dim, words in DRAMATIZATION_DICT.items():
        guardian_conflict[f'{dim}_raw'] = guardian_conflict['full_text'].apply(
            lambda x, w=words: count_words(x, w))

    # Normalize per 1000 words
    for dim in DIMENSIONS:
        guardian_conflict[dim] = (
            guardian_conflict[f'{dim}_raw'] / guardian_conflict['wordcount'] * 1000
        )

    # PCA on the four normalized dimensions
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(guardian_conflict[DIMENSIONS].values)

    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    guardian_conflict['drama_pca'] = X_pca[:, 0]

    print(f"\nPCA — PC1 variance explained: {pca.explained_variance_ratio_[0] * 100:.1f}%")
    print("Loadings:")
    for dim, loading in zip(DIMENSIONS, pca.components_[0]):
        print(f"  {dim}: {loading:.3f}")

    # Binary indicators (for cross-source comparison with Reuters)
    for dim in DIMENSIONS:
        guardian_conflict[f'has_{dim}'] = (guardian_conflict[dim] > 0).astype(int)
    guardian_conflict['drama_binary'] = sum(
        guardian_conflict[f'has_{dim}'] for dim in DIMENSIONS
    )

    guardian_conflict.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return guardian_conflict, pca


# ---------------------------------------------------------------------------
# Reuters analysis (headlines -> binary)
# ---------------------------------------------------------------------------
def analyze_reuters(input_path, output_path):
    """Score Reuters headlines using binary presence of dictionary dimensions."""
    reuters = pd.read_csv(input_path)

    reuters['is_conflict'] = reuters['title_clean'].str.lower().str.contains(
        REUTERS_CONFLICT_KW, na=False
    )
    reuters_conflict = reuters[reuters['is_conflict']].copy()
    print(f"Reuters conflict articles: {len(reuters_conflict)}")

    # Binary features — headlines are too short for reliable word counts
    for dim, words in DRAMATIZATION_DICT.items():
        if dim == 'firstperson':
            # For headlines, detect quote-opening as a proxy for first-person voice
            reuters_conflict[f'has_{dim}'] = reuters_conflict['title_clean'].apply(
                lambda x: 1 if re.match(r"^['\"\']", str(x)) else 0
            )
        else:
            reuters_conflict[f'has_{dim}'] = reuters_conflict['title_clean'].apply(
                lambda x, w=words: 1 if count_words(x, w) > 0 else 0
            )

    reuters_conflict['drama_binary'] = sum(
        reuters_conflict[f'has_{dim}'] for dim in DIMENSIONS
    )

    reuters_conflict.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return reuters_conflict


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Analyzing Guardian")
    print("=" * 60)
    analyze_guardian(
        os.path.join(processed_dir, 'guardian_drc_clean.csv'),
        os.path.join(processed_dir, 'guardian_conflict_analyzed.csv'),
    )

    print("\n" + "=" * 60)
    print("Analyzing Reuters")
    print("=" * 60)
    analyze_reuters(
        os.path.join(processed_dir, 'reuters_drc_clean.csv'),
        os.path.join(processed_dir, 'reuters_conflict_analyzed.csv'),
    )


if __name__ == '__main__':
    main()
