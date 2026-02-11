# ============================================================
# 04_dramatization_index.py
# Calculate dramatization index using dictionary method
# ============================================================

import pandas as pd
import numpy as np
import re
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Get paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')

# ============================================================
# Dictionary Definition (4 Dimensions)
# ============================================================

DICTIONARY = {
    'emotional': [
        'horrific', 'devastating', 'tragic', 'brutal', 'terrible', 'shocking',
        'heartbreaking', 'desperate', 'dire', 'grim', 'deadly', 'fatal',
        'massacre', 'slaughter', 'atrocity', 'horror', 'terror', 'suffering',
        'feared', 'afraid', 'terrified', 'haunted', 'traumatized', 'scarred',
        'crying', 'screaming', 'sobbing', 'weeping', 'trembling',
        'heartbroken', 'shattered', 'devastated', 'horrified', 'terrifying',
        'agonizing', 'unbearable', 'unimaginable', 'unspeakable', 'harrowing',
        'nightmare', 'nightmarish', 'hellish'
    ],
    'personal': [
        'victim', 'victims', 'survivor', 'survivors', 'witness', 'witnesses',
        'orphan', 'orphans', 'widow', 'widows',
        'mother', 'father', 'child', 'children', 'baby', 'babies', 'infant',
        'daughter', 'son', 'family', 'families', 'parents',
        'villager', 'villagers', 'civilian', 'civilians', 'resident', 'residents',
        'woman', 'women', 'girl', 'boy'
    ],
    'narrative': [
        'told', 'says', 'recalled', 'remembers', 'describes', 'recounts',
        'story', 'stories', 'account', 'testimony', 'voice', 'voices',
        'lived', 'experienced', 'witnessed', 'survived', 'escaped', 'fled'
    ],
    'firstperson': ['i ', ' me ', ' my ', ' we ', ' our ']
}

# ============================================================
# Count Function
# ============================================================

def count_words(text, word_list):
    """Count occurrences of words in text using word boundaries"""
    text_lower = ' ' + str(text).lower() + ' '
    total = 0
    for word in word_list:
        pattern = r'\b' + word.strip() + r'\b'
        total += len(re.findall(pattern, text_lower))
    return total

# ============================================================
# Apply to Guardian (Full Text)
# ============================================================

def analyze_guardian(input_path, output_path):
    """Analyze Guardian articles with full text"""
    
    guardian = pd.read_csv(input_path)
    
    # Filter conflict articles only
    guardian_conflict = guardian[guardian['topic'] == 'Conflict'].copy()
    print(f"Guardian conflict articles: {len(guardian_conflict)}")
    
    # Count raw occurrences
    for dim, words in DICTIONARY.items():
        guardian_conflict[f'{dim}_raw'] = guardian_conflict['full_text'].apply(
            lambda x: count_words(x, words))
    
    # Normalize per 1000 words
    for dim in DICTIONARY.keys():
        guardian_conflict[dim] = guardian_conflict[f'{dim}_raw'] / guardian_conflict['wordcount'] * 1000
    
    # PCA
    dims = list(DICTIONARY.keys())
    X = guardian_conflict[dims].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    
    guardian_conflict['drama_pca'] = X_pca[:, 0]
    
    # Report
    print(f"\nPCA Results:")
    print(f"  PC1 variance explained: {pca.explained_variance_ratio_[0]*100:.1f}%")
    print(f"  Loadings:")
    for dim, loading in zip(dims, pca.components_[0]):
        print(f"    {dim}: {loading:.3f}")
    
    # Binary features (for comparison with Reuters)
    for dim in dims:
        guardian_conflict[f'has_{dim}'] = (guardian_conflict[dim] > 0).astype(int)
    guardian_conflict['drama_binary'] = sum(guardian_conflict[f'has_{dim}'] for dim in dims)
    
    # Save
    guardian_conflict.to_csv(output_path, index=False)
    print(f"\n✓ Saved to {output_path}")
    
    return guardian_conflict, pca

# ============================================================
# Apply to Reuters (Headlines Only)
# ============================================================

def analyze_reuters(input_path, output_path):
    """Analyze Reuters headlines"""
    
    reuters = pd.read_csv(input_path)
    
    # Filter conflict articles
    conflict_kw = r'kill|killed|attack|rebel|militia|m23|war|violence|soldier|troops|fight|clash|battle|dead|death|massacre|flee|refugee|displaced|humanitarian'
    reuters['is_conflict'] = reuters['title_clean'].str.lower().str.contains(conflict_kw, na=False)
    reuters_conflict = reuters[reuters['is_conflict']].copy()
    print(f"Reuters conflict articles: {len(reuters_conflict)}")
    
    # Binary features (headline too short for counts)
    dims = list(DICTIONARY.keys())
    for dim, words in DICTIONARY.items():
        if dim == 'firstperson':
            # For headlines, check quote opening instead
            reuters_conflict[f'has_{dim}'] = reuters_conflict['title_clean'].apply(
                lambda x: 1 if re.match(r"^['\"\']", str(x)) else 0)
        else:
            reuters_conflict[f'has_{dim}'] = reuters_conflict['title_clean'].apply(
                lambda x: 1 if count_words(x, words) > 0 else 0)
    
    reuters_conflict['drama_binary'] = sum(reuters_conflict[f'has_{dim}'] for dim in dims)
    
    # Save
    reuters_conflict.to_csv(output_path, index=False)
    print(f"\n✓ Saved to {output_path}")
    
    return reuters_conflict

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':

    print("="*60)
    print("Analyzing Guardian")
    print("="*60)
    guardian, pca = analyze_guardian(
        os.path.join(processed_dir, 'guardian_drc_clean.csv'),
        os.path.join(processed_dir, 'guardian_conflict_analyzed.csv')
    )

    print("\n" + "="*60)
    print("Analyzing Reuters")
    print("="*60)
    reuters = analyze_reuters(
        os.path.join(processed_dir, 'reuters_drc_clean.csv'),
        os.path.join(processed_dir, 'reuters_conflict_analyzed.csv')
    )