"""
Section 5 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_05_sub_ratings.py
Or via runner:   from section_05_sub_ratings import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shared_config import df, save_plot, _section, COLORS, SUB_RATINGS, OUTPUT_DIR

def run():
    _section("SECTION 5: Sub-Rating Analysis (13-22)")

    # --- 5.13 Radar Chart: Sub-Rating Profiles of Top 6 Companies ---
    from math import pi
    
    top6_companies = df.groupby('Company')['Rating'].mean().nlargest(6).index
    radar_data = df[df['Company'].isin(top6_companies)].groupby('Company')[SUB_RATINGS].mean()
    
    # Normalize to 0-1 for better visual spread (optional, but ratings are already 0-5)
    N = len(SUB_RATINGS)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # close the circle
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    palette = sns.color_palette("husl", len(radar_data))
    for idx, (company, row) in enumerate(radar_data.iterrows()):
        values = row.values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=company, color=palette[idx])
        ax.fill(angles, values, alpha=0.1, color=palette[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(SUB_RATINGS, fontsize=10)
    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
    ax.set_title('Sub-Rating Profiles: Top 6 Companies by Overall Rating', fontsize=15, pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    save_plot(plt, "13_radar_top6_companies.png")
    
    # --- 5.14 Average Sub-Ratings Across All Companies (Grouped Bar) ---
    avg_sub = df[SUB_RATINGS].mean().sort_values()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_colors = sns.color_palette("RdYlGn", len(SUB_RATINGS))
    bars = ax.barh(range(len(avg_sub)), avg_sub.values, color=bar_colors)
    ax.set_yticks(range(len(avg_sub)))
    ax.set_yticklabels(avg_sub.index, fontsize=11)
    ax.set_xlim(0, 5.5)
    ax.set_title('Average Sub-Rating Across All Companies', fontsize=14)
    ax.set_xlabel('Average Rating (out of 5)', fontsize=12)
    for i, (bar, val) in enumerate(zip(bars, avg_sub.values)):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                va='center', fontsize=10, fontweight='bold')
    save_plot(plt, "14_avg_sub_ratings_bar.png")
    
    # --- 5.15 Full Correlation Heatmap (Overall Rating + Sub-Ratings + Reviews) ---
    corr_cols = ['Rating', '#Reviews'] + SUB_RATINGS
    full_corr = df[corr_cols].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(full_corr, dtype=bool), k=1)
    sns.heatmap(full_corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
                annot_kws={'fontsize': 9})
    ax.set_title('Correlation Matrix: Overall Rating, Reviews & Sub-Ratings', fontsize=14, pad=15)
    save_plot(plt, "15_full_correlation_heatmap.png")
    
    # --- 5.16 Box Plots: Distribution of Each Sub-Rating ---
    df_melted_sub = df[SUB_RATINGS].melt(var_name='Sub-Rating', value_name='Score')
    
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.boxplot(data=df_melted_sub, x='Sub-Rating', y='Score', hue='Sub-Rating',
                palette='Set3', legend=False, ax=ax)
    sns.stripplot(data=df_melted_sub, x='Sub-Rating', y='Score', color='black',
                  alpha=0.15, size=2, ax=ax, jitter=True)
    ax.set_title('Distribution of Sub-Rating Scores', fontsize=14)
    ax.set_ylabel('Score (out of 5)', fontsize=12)
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=30, labelsize=10)
    # Add mean markers
    means = df[SUB_RATINGS].mean()
    for i, (col, mean_val) in enumerate(means.items()):
        ax.plot(i, mean_val, 'D', color='red', markersize=8, zorder=5)
    ax.axhline(y=df[SUB_RATINGS].mean().mean(), color='gray', linestyle='--',
               alpha=0.5, label='Grand Mean')
    ax.legend(['Grand Mean'], fontsize=9)
    save_plot(plt, "16_sub_ratings_boxplot.png")
    
    # --- 5.17 Scatter Facets: Overall Rating vs Each Sub-Rating ---
    fig, axes = plt.subplots(3, 3, figsize=(16, 14))
    axes = axes.flatten()
    
    for i, sub in enumerate(SUB_RATINGS):
        ax = axes[i]
        ax.scatter(df[sub], df['Rating'], alpha=0.2, c='#3498db', edgecolors='none', s=20)
        # Regression line
        mask = df[sub].notna() & df['Rating'].notna()
        if mask.sum() > 2:
            z = np.polyfit(df.loc[mask, sub], df.loc[mask, 'Rating'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(df[sub].min(), df[sub].max(), 100)
            ax.plot(x_line, p(x_line), 'r-', linewidth=1.5, alpha=0.8)
        ax.set_title(f'{sub}', fontsize=11)
        ax.set_xlabel('Score', fontsize=9)
        ax.set_ylabel('Overall Rating', fontsize=9)
        ax.set_xlim(-0.2, 5.2)
        ax.set_ylim(-0.2, 5.2)
        ax.grid(True, linestyle='--', alpha=0.4)
        # Annotate correlation
        corr_val = df[sub].corr(df['Rating'])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=10, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Hide extra subplots if any
    for j in range(len(SUB_RATINGS), len(axes)):
        axes[j].set_visible(False)
    
    fig.suptitle('Overall Rating vs Each Sub-Rating (with Regression Line)', fontsize=16, y=1.01)
    plt.tight_layout()
    save_plot(plt, "17_rating_vs_sub_ratings_facets.png")
    
    # --- 5.18 Monthly Trend of Sub-Ratings ---
    monthly_sub = df.groupby('YearMonth')[SUB_RATINGS].mean()
    monthly_sub.index = monthly_sub.index.astype(str)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    palette = sns.color_palette("tab10", len(SUB_RATINGS))
    for i, sub in enumerate(SUB_RATINGS):
        ax.plot(monthly_sub.index, monthly_sub[sub], marker='o', linewidth=2,
                label=sub, color=palette[i], markersize=5)
    
    ax.set_title('Monthly Average Sub-Ratings Over Time', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Average Score', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_ylim(0, 5.5)
    save_plot(plt, "18_monthly_sub_ratings_line.png")
    
    # --- 5.19 Heatmap: Companies × Sub-Ratings (Top 20 by total reviews) ---
    top20_by_reviews = df.groupby('Company')['#Reviews'].sum().nlargest(20).index
    heatmap_data = df[df['Company'].isin(top20_by_reviews)].groupby('Company')[SUB_RATINGS].mean()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
                linewidths=0.5, vmin=0, vmax=5, annot_kws={'fontsize': 8})
    ax.set_title('Sub-Rating Heatmap: Top 20 Companies by Total Reviews', fontsize=14, pad=12)
    ax.set_xlabel('Sub-Rating Category', fontsize=12)
    ax.set_ylabel('Company', fontsize=12)
    ax.tick_params(axis='y', labelsize=9)
    save_plot(plt, "19_companies_sub_ratings_heatmap.png")
    
    # --- 5.20 Grouped Bar: Sub-Ratings of Top 10 Companies ---
    top10_overall = df.groupby('Company')['Rating'].mean().nlargest(10).index
    grouped_bar_data = df[df['Company'].isin(top10_overall)].groupby('Company')[SUB_RATINGS].mean()
    
    x = np.arange(len(SUB_RATINGS))
    width = 0.08
    n_companies = len(grouped_bar_data)
    
    fig, ax = plt.subplots(figsize=(18, 8))
    palette = sns.color_palette("tab10", n_companies)
    for i, (company, row) in enumerate(grouped_bar_data.iterrows()):
        offset = (i - n_companies/2 + 0.5) * width
        ax.bar(x + offset, row.values, width, label=company, color=palette[i])
    
    ax.set_xticks(x)
    ax.set_xticklabels(SUB_RATINGS, fontsize=10)
    ax.set_ylabel('Average Score (out of 5)', fontsize=12)
    ax.set_title('Sub-Rating Comparison: Top 10 Companies by Overall Rating', fontsize=14)
    ax.set_ylim(0, 5.5)
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9, title='Company')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    save_plot(plt, "20_top10_sub_ratings_grouped_bar.png")
    
    # --- 5.21 Scatter: Salary vs Work-Life Balance (colored by Overall Rating) ---
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(df['Salary'], df['Work-Life Balance'],
                         c=df['Rating'], cmap='RdYlGn', alpha=0.5,
                         s=df['#Reviews']/20 + 5, edgecolors='w', linewidth=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Overall Rating', fontsize=11)
    ax.set_xlabel('Salary Rating', fontsize=12)
    ax.set_ylabel('Work-Life Balance Rating', fontsize=12)
    ax.set_title('Salary vs Work-Life Balance\n(color = overall rating, size = #reviews)', fontsize=14)
    ax.set_xlim(-0.2, 5.2)
    ax.set_ylim(-0.2, 5.2)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Annotate companies with extreme trade-offs
    company_agg = df.groupby('Company').agg(
        avg_salary=('Salary', 'mean'),
        avg_wlb=('Work-Life Balance', 'mean'),
        avg_rating=('Rating', 'mean')
    ).reset_index()
    
    # Highlight: companies where salary >> WLB or WLB >> salary
    company_agg['diff'] = abs(company_agg['avg_salary'] - company_agg['avg_wlb'])
    extreme = company_agg.nlargest(8, 'diff')
    for _, row in extreme.iterrows():
        ax.annotate(row['Company'], (row['avg_salary'], row['avg_wlb']),
                    textcoords="offset points", xytext=(6, 6),
                    fontsize=8, ha='left',
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.6))
    save_plot(plt, "21_salary_vs_wlb_scatter.png")
    
    # --- 5.22 Stacked Area: Sub-Rating Composition Over Time ---
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.stackplot(monthly_sub.index, *[monthly_sub[c] for c in SUB_RATINGS],
                 labels=SUB_RATINGS, colors=sns.color_palette("Set3", len(SUB_RATINGS)), alpha=0.85)
    ax.set_title('Sub-Rating Composition Over Time (Stacked Area)', fontsize=14)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Cumulative Average Score', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), fontsize=9)
    ax.set_ylim(0, 35)
    save_plot(plt, "22_sub_ratings_stacked_area.png")
    
    print(f"\n  ✓ Section 5 complete — 10 plots saved.")

if __name__ == "__main__":
    run()
