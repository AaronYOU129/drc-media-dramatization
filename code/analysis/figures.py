# ============================================================
# 06_figures.py
# Generate figures for paper
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import stats

# ============================================================
# Load data
# ============================================================

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
processed_dir = os.path.join(project_root, 'data', 'processed')
figures_dir = os.path.join(project_root, 'output', 'figures')

guardian = pd.read_csv(os.path.join(processed_dir, 'guardian_conflict_analyzed.csv'))
reuters = pd.read_csv(os.path.join(processed_dir, 'reuters_conflict_analyzed.csv'))

# ============================================================
# Figure 1: Guardian vs Reuters Trend
# ============================================================

def fig1_trend():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    years = range(2018, 2025)
    g_yearly = [guardian[guardian['year']==y]['drama_binary'].mean() for y in years]
    r_yearly = [reuters[reuters['year']==y]['drama_binary'].mean() for y in years]
    
    ax.plot(years, g_yearly, 'o-', color='#27ae60', linewidth=2.5, markersize=10, 
            label='Guardian (full text)')
    ax.plot(years, r_yearly, 's-', color='#3498db', linewidth=2.5, markersize=10, 
            label='Reuters (headline)')
    ax.axvline(x=2021.5, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax.fill_between(years, g_yearly, r_yearly, alpha=0.15, color='#27ae60')
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Dramatization Score\n(dimensions present, 0-4)', fontsize=11)
    ax.set_title('Guardian vs Reuters: Dramatization Over Time', fontsize=13, fontweight='bold')
    ax.legend(loc='center right', fontsize=10)
    ax.set_xticks(years)
    ax.set_ylim(0, 4)
    ax.grid(True, alpha=0.3)
    ax.text(2021.7, 3.7, 'M23\nResurgence', fontsize=9, color='red', ha='left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig1_guardian_vs_reuters_trend.pdf'), bbox_inches='tight')
    plt.close()
    print("✓ Figure 1 saved")

# ============================================================
# Figure 2: Feature Coverage
# ============================================================

def fig2_coverage():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    features = ['Emotional', 'Personal', 'Narrative', 'First-person']
    g_vals = [
        guardian['has_emotional'].mean() * 100,
        guardian['has_personal'].mean() * 100,
        guardian['has_narrative'].mean() * 100,
        guardian['has_firstperson'].mean() * 100
    ]
    r_vals = [
        reuters['has_emotional'].mean() * 100,
        reuters['has_personal'].mean() * 100,
        reuters['has_narrative'].mean() * 100,
        reuters['has_firstperson'].mean() * 100
    ]
    
    x = np.arange(len(features))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, g_vals, width, label='Guardian', color='#27ae60', alpha=0.85)
    bars2 = ax.bar(x + width/2, r_vals, width, label='Reuters', color='#3498db', alpha=0.85)
    
    ax.set_ylabel('% of articles with feature', fontsize=11)
    ax.set_title('Feature Coverage: Guardian vs Reuters', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(features, fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars1, g_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar, val in zip(bars2, r_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{val:.0f}%', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig2_feature_coverage.pdf'), bbox_inches='tight')
    plt.close()
    print("✓ Figure 2 saved")

# ============================================================
# Figure 3: Guardian PCA Trend
# ============================================================

def fig3_pca_trend():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    years = range(2018, 2025)
    yearly_stats = guardian.groupby('year')['drama_pca'].agg(['mean', 'std', 'count'])
    means = [yearly_stats.loc[y, 'mean'] for y in years]
    se = [yearly_stats.loc[y, 'std'] / np.sqrt(yearly_stats.loc[y, 'count']) for y in years]
    
    ax.plot(years, means, 'o-', color='#c0392b', linewidth=2.5, markersize=10)
    ax.fill_between(years, 
                    [m - 1.96*s for m, s in zip(means, se)],
                    [m + 1.96*s for m, s in zip(means, se)],
                    alpha=0.2, color='#c0392b')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=2021.5, color='red', linestyle='--', alpha=0.7, linewidth=2)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Dramatization Index (PC1)', fontsize=11)
    ax.set_title('Guardian Conflict Coverage: Dramatization Over Time', fontsize=13, fontweight='bold')
    ax.set_xticks(years)
    ax.grid(True, alpha=0.3)
    ax.text(2021.7, 0.4, 'M23\nResurgence', fontsize=9, color='red', ha='left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig3_guardian_pca_trend.pdf'), bbox_inches='tight')
    plt.close()
    print("✓ Figure 3 saved")

# ============================================================
# Figure 4: Pre vs Post M23
# ============================================================

def fig4_m23_comparison():
    fig, ax = plt.subplots(figsize=(7, 5))
    
    pre_m23 = guardian[guardian['year'] <= 2021]['drama_pca']
    post_m23 = guardian[guardian['year'] >= 2022]['drama_pca']
    
    bp = ax.boxplot([pre_m23, post_m23], positions=[1, 2], widths=0.5, patch_artist=True)
    bp['boxes'][0].set_facecolor('#3498db')
    bp['boxes'][0].set_alpha(0.7)
    bp['boxes'][1].set_facecolor('#e74c3c')
    bp['boxes'][1].set_alpha(0.7)
    
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xticks([1, 2])
    ax.set_xticklabels([f'Pre-M23\n(2018-2021)\n$N$={len(pre_m23)}', 
                        f'Post-M23\n(2022-2024)\n$N$={len(post_m23)}'], fontsize=11)
    ax.set_ylabel('Dramatization Index (PC1)', fontsize=11)
    ax.set_title('Guardian: Pre vs Post M23 Comparison', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Statistics
    t_stat, p_val = stats.ttest_ind(pre_m23, post_m23)
    cohens_d = (post_m23.mean() - pre_m23.mean()) / np.sqrt(
        (pre_m23.std()**2 + post_m23.std()**2) / 2
    )
    
    ax.text(1.5, ax.get_ylim()[1]*0.9,
            f'$\\Delta$ = {post_m23.mean()-pre_m23.mean():.3f}\n$t$ = {abs(t_stat):.2f}, $p$ = {p_val:.3f}\nCohen\'s $d$ = {cohens_d:.2f}',
            ha='center', va='top', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'fig4_pre_post_m23.pdf'), bbox_inches='tight')
    plt.close()
    print("✓ Figure 4 saved")

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    os.makedirs(figures_dir, exist_ok=True)

    fig1_trend()
    fig2_coverage()
    fig3_pca_trend()
    fig4_m23_comparison()

    print(f"\n✓ All figures saved to {figures_dir}")