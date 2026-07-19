"""
Section 4 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_04_insightful_plots.py
Or via runner:   from section_04_insightful_plots import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import df, save_plot, _section, COLORS, OUTPUT_DIR

def run():
    _section("SECTION 4: Additional Insightful Plots (5-12)")
    
    # --- 4.5 Box Plot: Rating spread per company (Top 15 by review count) ---
    top_companies = df.groupby('Company')['#Reviews'].sum().nlargest(15).index
    df_top = df[df['Company'].isin(top_companies)]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.boxplot(data=df_top, x='Company', y='Rating', hue='Company',
                palette='viridis', legend=False, ax=ax)
    ax.set_title('Rating Distribution per Company (Top 15 by Total Reviews)', fontsize=14)
    ax.set_xticks(range(len(top_companies)))
    ax.set_xticklabels(top_companies, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Rating', fontsize=12)
    save_plot(plt, "05_rating_boxplot_per_company.png")
    
    # --- 4.6 Bar Chart: Total Number of Reviews per Company (Top 15) ---
    review_counts = df.groupby('Company')['#Reviews'].sum().nlargest(15)
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(review_counts.index, review_counts.values, color=COLORS[2])
    ax.set_title('Total Number of Reviews per Company (Top 15)', fontsize=14)
    ax.set_ylabel('Total Reviews', fontsize=12)
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 50, str(height), ha='center', va='bottom', fontsize=9)
    save_plot(plt, "06_review_count_per_company.png")
    
    # --- 4.7 Scatter: Average Rating vs Industry Deviation ---
    avg_stats = df.groupby('Company').agg(
        avg_rating=('Rating', 'mean'),
        avg_deviation=('Industry level insights (%: -100 (below industry\'s average) to 100)', 'mean'),
        total_reviews=('#Reviews', 'sum')
    ).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(avg_stats['avg_rating'], avg_stats['avg_deviation'],
                         s=avg_stats['total_reviews']/10, alpha=0.6, c='#8e44ad', edgecolors='w')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(avg_stats['avg_rating'].mean(), color='red', linestyle='--', alpha=0.5)
    ax.set_title('Average Rating vs Industry Deviation (bubble size = total reviews)', fontsize=14)
    ax.set_xlabel('Average Rating', fontsize=12)
    ax.set_ylabel('Average Industry Deviation (%)', fontsize=12)
    ax.grid(True)
    # Annotate a few outliers
    for i, row in avg_stats.iterrows():
        if abs(row['avg_deviation']) > 15 or row['avg_rating'] < 2.5 or row['avg_rating'] > 4.5:
            ax.annotate(row['Company'], (row['avg_rating'], row['avg_deviation']),
                        textcoords="offset points", xytext=(5,5), ha='left', fontsize=8)
    save_plot(plt, "07_rating_vs_deviation_scatter.png")
    
    # --- 4.8 Pie Chart: Review Distribution among Top 8 Companies ---
    top8_reviews = review_counts.nlargest(8)
    others = review_counts.sum() - top8_reviews.sum()
    pie_data = top8_reviews.copy()
    pie_data['Others'] = others
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%',
                                      startangle=90, colors=sns.color_palette('Set3', len(pie_data)))
    ax.set_title('Review Distribution Among Top Companies', fontsize=14)
    save_plot(plt, "08_review_distribution_pie.png")
    
    # --- 4.9 Time Series: Monthly Average Rating ---
    monthly_avg = df.groupby('YearMonth')['Rating'].mean().reset_index()
    monthly_avg['YearMonth'] = monthly_avg['YearMonth'].astype(str)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly_avg['YearMonth'], monthly_avg['Rating'], marker='o', color='#2c3e50', linewidth=2)
    ax.set_title('Monthly Average Rating Over Time', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Average Rating', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)
    # Add trend line
    mask = monthly_avg['Rating'].notna()
    if mask.sum() > 2:
        x = np.arange(len(monthly_avg))
        z = np.polyfit(x[mask], monthly_avg.loc[mask, 'Rating'], 1)
        p = np.poly1d(z)
        ax.plot(monthly_avg['YearMonth'], p(x), "r--", label='Trend')
    ax.legend()
    save_plot(plt, "09_monthly_avg_rating_line.png")
    
    # --- 4.10 Correlation Heatmap ---
    corr_df = df[['Rating', '#Reviews', 'Industry level insights (%: -100 (below industry\'s average) to 100)']].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0, square=True, ax=ax)
    ax.set_title('Correlation Matrix of Numeric Features', fontsize=14)
    save_plot(plt, "10_correlation_heatmap.png")
    
    # --- 4.11 Violin Plot: Rating distribution by Review Count Bracket ---
    # Categorize number of reviews into brackets
    bins = [0, 10, 50, 200, 1000, np.inf]
    labels = ['0-10', '11-50', '51-200', '201-1000', '1000+']
    df['Review_bracket'] = pd.cut(df['#Reviews'], bins=bins, labels=labels, right=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=df, x='Review_bracket', y='Rating', hue='Review_bracket',
                   palette='muted', legend=False, ax=ax)
    ax.set_title('Rating Distribution by Number of Reviews', fontsize=14)
    ax.set_xlabel('Review Count Bracket', fontsize=12)
    ax.set_ylabel('Rating', fontsize=12)
    save_plot(plt, "11_rating_violin_by_review_bracket.png")
    
    # --- 4.12 Stacked Bar: Companies Above/Below Industry Average ---
    df['above_industry'] = df['Industry level insights (%: -100 (below industry\'s average) to 100)'] >= 0
    counts = df.groupby(['Company', 'above_industry']).size().unstack(fill_value=0)
    counts.columns = ['Below Industry Avg', 'Above Industry Avg']
    # Sort by total count of above, take top 15
    counts['Total'] = counts.sum(axis=1)
    counts = counts.sort_values('Total', ascending=False).head(15).drop('Total', axis=1)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    counts.plot(kind='bar', stacked=True, ax=ax, color=['#e74c3c', '#2ecc71'])
    ax.set_title('Companies: Above/Below Industry Average (Top 15 by Total Reviews)', fontsize=14)
    ax.set_ylabel('Number of Data Points', fontsize=12)
    ax.set_xlabel('Company', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title='')
    save_plot(plt, "12_above_below_industry_stacked_bar.png")
    
    print(f"\n  ✓ Section 4 complete — 8 plots saved.")

if __name__ == "__main__":
    run()
