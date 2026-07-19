"""
Section 3 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_03_mandatory_plots.py
Or via runner:   from section_03_mandatory_plots import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import df, save_plot, _section, COLORS, OUTPUT_DIR

def run():
    _section("SECTION 3: Mandatory Plots (1-4)")
    
    # --- 3.1 Bar Chart: Company Ratings (Top 20 by rating) ---
    top_rated = df.groupby('Company')['Rating'].mean().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(top_rated.index, top_rated.values, color=COLORS[0])
    ax.set_title('Top 20 Companies by Average Rating', fontsize=14, pad=15)
    ax.set_xlabel('Company', fontsize=12)
    ax.set_ylabel('Rating (out of 5)', fontsize=12)
    ax.set_ylim(0, 5.5)
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 2), ha='center', va='bottom', fontsize=8)
    save_plot(plt, "01_company_ratings_bar.png")
    
    # --- 3.2 Bar Chart: Industry Level Insights (Top/Bottom 10 deviation) ---
    # Aggregate mean deviation per company
    deviation = df.groupby('Company')['Industry level insights (%: -100 (below industry\'s average) to 100)'].mean().sort_values()
    worst10 = deviation.head(10)
    best10 = deviation.tail(10)
    combined = pd.concat([worst10, best10])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#d9534f' if x < 0 else '#5cb85c' for x in combined.values]
    bars = ax.barh(combined.index, combined.values, color=colors)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_title('Companies with Most Extreme Industry Deviation (%)', fontsize=14)
    ax.set_xlabel('Deviation from Industry Average (%)', fontsize=12)
    for i, (bar, val) in enumerate(zip(bars, combined.values)):
        if pd.notna(val):
            ax.text(val + (2 if val >=0 else -5), bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=9)
    save_plot(plt, "02_industry_insights_bar.png")
    
    # --- 3.3 Distribution Plot: Rating Distribution ---
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df['Rating'], bins=20, kde=True, color='#3498db', ax=ax)
    ax.set_title('Distribution of Company Ratings', fontsize=14)
    ax.set_xlabel('Rating (0-5)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.axvline(df['Rating'].mean(), color='red', linestyle='dashed', linewidth=2, label=f'Mean: {df["Rating"].mean():.2f}')
    ax.legend()
    save_plot(plt, "03_rating_distribution.png")
    
    # --- 3.4 Scatter Plot: Rating vs Number of Reviews (log scale) ---
    fig, ax = plt.subplots(figsize=(10, 6))
    # Slight jitter to avoid overlapping points (optional)
    scatter = ax.scatter(df['Rating'], df['#Reviews'], alpha=0.6, c='#e67e22', edgecolors='w', s=30)
    ax.set_yscale('log')
    ax.set_title('Rating vs Number of Reviews (Log Scale)', fontsize=14)
    ax.set_xlabel('Rating', fontsize=12)
    ax.set_ylabel('Number of Reviews (log scale)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    # Add a trend line (optional)
    mask = df['Rating'].notna() & df['#Reviews'].notna()
    if mask.sum() > 2:
        z = np.polyfit(df.loc[mask, 'Rating'],
                       np.log10(df.loc[mask, '#Reviews'] + 1), 1)
        p = np.poly1d(z)
        ax.plot(df['Rating'].sort_values(), 10**p(df['Rating'].sort_values()), "r--", alpha=0.7)
    save_plot(plt, "04_rating_vs_reviews_scatter.png")
    
    print(f"\n  ✓ Section 3 complete — 4 plots saved.")

if __name__ == "__main__":
    run()
