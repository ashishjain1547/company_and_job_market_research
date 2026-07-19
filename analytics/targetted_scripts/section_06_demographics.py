"""
Section 6 script — auto-extracted from analyze_20260719.py.
Run standalone:  python section_06_demographics.py
Or via runner:   from section_06_demographics import run; run()
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi
from shared_config import df, company_demo, save_plot, _section, COLORS, SUB_RATINGS, current_year, OUTPUT_DIR

def run():
    _section("SECTION 6: Company Demographics & Scale (23-34)")

    # ── 6.23 ── Timeline: Company Founding Year with Rating ──
    companies_with_founding = company_demo[company_demo['founded'].notna()].sort_values('founded')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    # Color mapping: older = deeper blue, newer = lighter
    norm = plt.Normalize(companies_with_founding['founded'].min(), companies_with_founding['founded'].max())
    colors = plt.cm.Blues_r(0.3 + 0.7 * norm(companies_with_founding['founded']))
    bars = ax.barh(companies_with_founding['Company'], companies_with_founding['founded'],
                   color=colors, edgecolor='#2c3e50', linewidth=0.8)
    ax.set_title('Company Founding Timeline', fontsize=14, pad=15)
    ax.set_xlabel('Year Founded', fontsize=12)
    ax.set_ylabel('')
    # Add rating as text on bars
    for i, (_, row) in enumerate(companies_with_founding.iterrows()):
        ax.text(row['founded'] + 0.5, i, f"* {row['avg_rating']:.1f}",
                va='center', fontsize=10, fontweight='bold',
                color='#c0392b')
    # Add reference lines for eras
    for era_year, era_label, era_color in [(1970, 'Pre-1970', '#95a5a6'), (2000, '1970-2000', '#bdc3c7')]:
        ax.axvline(era_year, color=era_color, linestyle='--', alpha=0.5, linewidth=1)
        ax.text(era_year + 0.5, len(companies_with_founding) - 0.3, era_label,
                fontsize=8, color=era_color, fontstyle='italic')
    ax.invert_yaxis()
    save_plot(plt, "23_founding_timeline.png")
    
    # ── 6.24 ── Grouped Bar: India vs Global Employee Count ──
    emp_data = company_demo[company_demo['india_emp'].notna() & company_demo['global_emp'].notna()].sort_values('global_emp')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(emp_data))
    width = 0.35
    bars1 = ax.bar(x - width/2, emp_data['india_emp'], width, label='India Employees',
                   color='#ff9933', edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, emp_data['global_emp'], width, label='Global Employees',
                   color='#2874a6', edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(emp_data['Company'], rotation=30, ha='right', fontsize=10)
    ax.set_ylabel('Employee Count (upper cap)', fontsize=12)
    ax.set_title('India vs Global Employee Headcount by Company', fontsize=14, pad=15)
    ax.legend(fontsize=10)
    ax.set_yscale('log')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    # Annotate values on bars
    for bar in bars1:
        w = bar.get_width()
        ax.text(bar.get_x() + w/2, bar.get_height() * 1.02, f'{bar.get_height():,.0f}',
                ha='center', va='bottom', fontsize=7, fontweight='bold')
    for bar in bars2:
        w = bar.get_width()
        ax.text(bar.get_x() + w/2, bar.get_height() * 1.02, f'{bar.get_height():,.0f}',
                ha='center', va='bottom', fontsize=7)
    save_plot(plt, "24_india_vs_global_employees.png")
    
    # ── 6.25 ── Bar: India Employee % of Global Workforce ──
    pct_data = company_demo[company_demo['india_pct_of_global'].notna()].sort_values('india_pct_of_global')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    # Gradient from low to high India concentration
    pct_colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(pct_data)))
    bars = ax.barh(pct_data['Company'], pct_data['india_pct_of_global'], color=pct_colors, edgecolor='white')
    ax.axvline(50, color='#2c3e50', linestyle='--', linewidth=1.5, alpha=0.7, label='50% threshold')
    ax.set_title('India Workforce as % of Global Headcount', fontsize=14, pad=15)
    ax.set_xlabel('% of Global Employees in India', fontsize=12)
    ax.set_xlim(0, 110)
    for bar, (_, row) in zip(bars, pct_data.iterrows()):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{row["india_pct_of_global"]:.0f}%', va='center', fontsize=10, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    save_plot(plt, "25_india_pct_of_global.png")
    
    # ── 6.26 ── Scatter: Global Employee Count vs Rating (bubble = India employees) ──
    scatter_data = company_demo[company_demo['global_emp'].notna() & company_demo['avg_rating'].notna()]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bubble_sizes = scatter_data['india_emp'].fillna(1000) / 20 + 50
    scatter = ax.scatter(scatter_data['global_emp'], scatter_data['avg_rating'],
                         s=bubble_sizes, c=scatter_data['company_age'].fillna(20),
                         cmap='viridis', alpha=0.75, edgecolors='#2c3e50', linewidth=1)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Company Age (years)', fontsize=11)
    ax.set_xscale('log')
    ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
    ax.set_ylabel('Average Rating', fontsize=12)
    ax.set_title('Global Scale vs Rating\n(bubble size = India headcount, color = company age)', fontsize=14, pad=15)
    ax.set_ylim(scatter_data['avg_rating'].min() - 0.2, scatter_data['avg_rating'].max() + 0.3)
    ax.grid(True, linestyle='--', alpha=0.4)
    # Annotate all points
    for _, row in scatter_data.iterrows():
        offset = (12, 8) if row['avg_rating'] > scatter_data['avg_rating'].median() else (12, -12)
        ax.annotate(row['Company'], (row['global_emp'], row['avg_rating']),
                    textcoords="offset points", xytext=offset,
                    fontsize=9, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5, lw=0.8))
    # Add a reference line for average rating
    ax.axhline(scatter_data['avg_rating'].mean(), color='red', linestyle='--', alpha=0.5,
               label=f'Mean Rating: {scatter_data["avg_rating"].mean():.2f}')
    ax.legend(fontsize=9)
    save_plot(plt, "26_global_scale_vs_rating.png")
    
    # ── 6.27 ── Scatter: Company Age vs Rating ──
    age_data = company_demo[company_demo['company_age'].notna()]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    # Color by employee scale bracket
    def emp_bracket(val):
        if pd.isna(val): return 'Unknown'
        if val < 1000: return '<1K'
        if val < 10000: return '1K-10K'
        if val < 50000: return '10K-50K'
        return '50K+'
    
    age_data['emp_bracket'] = age_data['global_emp'].apply(emp_bracket)
    bracket_order = ['<1K', '1K-10K', '10K-50K', '50K+', 'Unknown']
    bracket_colors = {'<1K': '#e74c3c', '1K-10K': '#f39c12', '10K-50K': '#2ecc71', '50K+': '#3498db', 'Unknown': '#95a5a6'}
    
    for bracket in bracket_order:
        subset = age_data[age_data['emp_bracket'] == bracket]
        if len(subset) == 0:
            continue
        ax.scatter(subset['company_age'], subset['avg_rating'],
                   s=subset['total_reviews'] / 10 + 30, alpha=0.7,
                   c=bracket_colors[bracket], edgecolors='white', linewidth=0.8,
                   label=bracket, zorder=5)
    
    # Trend line
    mask = age_data['company_age'].notna() & age_data['avg_rating'].notna()
    if mask.sum() > 2:
        z = np.polyfit(age_data.loc[mask, 'company_age'], age_data.loc[mask, 'avg_rating'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(age_data['company_age'].min(), age_data['company_age'].max(), 100)
        ax.plot(x_line, p(x_line), 'k--', linewidth=1.5, alpha=0.6, label='Trend')
    
    # Annotate
    for _, row in age_data.iterrows():
        ax.annotate(row['Company'], (row['company_age'], row['avg_rating']),
                    textcoords="offset points", xytext=(6, 6),
                    fontsize=8, ha='left')
    ax.set_xlabel('Company Age (years since founding)', fontsize=12)
    ax.set_ylabel('Average Rating', fontsize=12)
    ax.set_title('Company Age vs Rating\n(color = global employee scale, size = total reviews)', fontsize=14, pad=15)
    ax.legend(title='Global Emp. Scale', fontsize=9, title_fontsize=10, loc='lower right')
    ax.grid(True, linestyle='--', alpha=0.4)
    save_plot(plt, "27_company_age_vs_rating.png")
    
    # ── 6.28 ── Heatmap: Companies with Demographic Data × Key Metrics ──
    demo_cols_for_heatmap = ['avg_rating', 'company_age', 'india_emp', 'global_emp',
                              'india_pct_of_global', 'total_reviews',
                              'avg_culture', 'avg_salary', 'avg_wlb']
    demo_heatmap_data = company_demo[company_demo['founded'].notna()].set_index('Company')[demo_cols_for_heatmap]
    
    # Rename for readability
    demo_heatmap_data.columns = ['Rating', 'Age (yrs)', 'India Emp', 'Global Emp',
                                  'India %', 'Reviews', 'Culture', 'Salary', 'WLB']
    
    # Normalize each column to 0-1 for the heatmap (helps visualize across different scales)
    demo_heatmap_norm = (demo_heatmap_data - demo_heatmap_data.min()) / (demo_heatmap_data.max() - demo_heatmap_data.min() + 1e-10)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(demo_heatmap_norm, annot=demo_heatmap_data.round(1), fmt='.0f',
                cmap='YlOrRd', ax=ax, linewidths=1, linecolor='white',
                annot_kws={'fontsize': 8}, cbar_kws={'label': 'Normalized Score (0-1)'})
    ax.set_title('Company Profile Comparison: Demographics & Key Metrics', fontsize=14, pad=15)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='both', labelsize=10)
    save_plot(plt, "28_company_profile_heatmap.png")
    
    # ── 6.29 ── Scatter: India Employee Count vs Sub-Ratings (Small Multiples) ──
    emp_sub_data = company_demo[company_demo['india_emp'].notna()]
    
    sub_rating_pairs = [
        ('avg_salary', 'Salary'),
        ('avg_wlb', 'Work-Life Balance'),
        ('avg_culture', 'Company Culture'),
        ('avg_satisfaction', 'Work Satisfaction'),
        ('avg_skill', 'Skill Development'),
        ('avg_security', 'Job Security'),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    axes = axes.flatten()
    
    for i, (col, label) in enumerate(sub_rating_pairs):
        ax = axes[i]
        scatter = ax.scatter(emp_sub_data['india_emp'], emp_sub_data[col],
                             s=emp_sub_data['total_reviews'] / 20 + 40,
                             c=emp_sub_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                             edgecolors='#2c3e50', linewidth=0.8)
        ax.set_xscale('log')
        ax.set_xlabel('India Employee Count (log)', fontsize=10)
        ax.set_ylabel(f'{label} Rating', fontsize=10)
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.set_xlim(emp_sub_data['india_emp'].min() * 0.8, emp_sub_data['india_emp'].max() * 1.3)
        ax.set_ylim(emp_sub_data[col].min() - 0.3, emp_sub_data[col].max() + 0.4)
        # Annotate
        for _, row in emp_sub_data.iterrows():
            ax.annotate(row['Company'], (row['india_emp'], row[col]),
                        textcoords="offset points", xytext=(5, 5),
                        fontsize=7, ha='left')
        # Correlation
        corr_val = emp_sub_data['india_emp'].corr(emp_sub_data[col])
        ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
                fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
    # Colorbar on the last subplot or as a shared one
    fig.suptitle('India Employee Scale vs Sub-Ratings\n(color = overall rating, size = total reviews)',
                 fontsize=16, y=1.01)
    plt.tight_layout()
    save_plot(plt, "29_india_emp_vs_sub_ratings.png")
    
    # ── 6.30 ── Industry-wise Comparison (for companies with industry + employee data) ──
    ind_data = company_demo[company_demo['industry'].notna() & company_demo['global_emp'].notna()]
    
    if len(ind_data) >= 3:
        fig, ax = plt.subplots(figsize=(12, 7))
        # Sort by global employee count
        ind_data = ind_data.sort_values('global_emp', ascending=False)
        colors_ind = sns.color_palette("Set2", len(ind_data))
        bars = ax.barh(ind_data['Company'], ind_data['global_emp'], color=colors_ind, edgecolor='white')
        ax.set_xscale('log')
        ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
        ax.set_title('Companies with Demographic Data: Global Employee Count by Industry', fontsize=14, pad=15)
    
        # Add industry and rating as annotation
        for i, (_, row) in enumerate(ind_data.iterrows()):
            industry_short = row['industry'][:35] + '...' if len(str(row['industry'])) > 35 else row['industry']
            ax.text(row['global_emp'] * 1.05, i,
                    f"*{row['avg_rating']:.1f} | {industry_short}",
                    va='center', fontsize=8, style='italic', color='#555')
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        save_plot(plt, "30_industry_employee_comparison.png")
    
    # ── 6.31 ── Founding Era Analysis: Rating by Era ──
    company_demo['founding_era'] = pd.cut(company_demo['founded'],
        bins=[1800, 1970, 2000, 2010, 2030],
        labels=['Pre-1970', '1970-1999', '2000-2010', 'Post-2010'])
    
    era_stats = company_demo.groupby('founding_era', observed=False).agg(
        avg_rating=('avg_rating', 'mean'),
        company_count=('Company', 'count'),
        avg_age=('company_age', 'mean'),
    ).dropna().reset_index()
    
    if len(era_stats) >= 2:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
        # Left: Bar chart - avg rating by era
        ax = axes[0]
        bars = ax.bar(era_stats['founding_era'], era_stats['avg_rating'],
                      color=sns.color_palette("viridis", len(era_stats)), edgecolor='white')
        ax.set_title('Average Rating by Founding Era', fontsize=13)
        ax.set_ylabel('Average Rating', fontsize=11)
        ax.set_xlabel('Founding Era', fontsize=11)
        ax.set_ylim(0, 5.5)
        for bar, val, cnt in zip(bars, era_stats['avg_rating'], era_stats['company_count']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{val:.2f}\n(n={int(cnt)})', ha='center', fontsize=10, fontweight='bold')
    
        # Right: Bar chart - company count by era
        ax = axes[1]
        bars = ax.bar(era_stats['founding_era'], era_stats['company_count'],
                      color=sns.color_palette("plasma", len(era_stats)), edgecolor='white')
        ax.set_title('Number of Companies per Founding Era', fontsize=13)
        ax.set_ylabel('Company Count', fontsize=11)
        ax.set_xlabel('Founding Era', fontsize=11)
        for bar, val in zip(bars, era_stats['company_count']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    str(int(val)), ha='center', fontsize=11, fontweight='bold')
    
        fig.suptitle('Founding Era Analysis', fontsize=15, y=1.02)
        plt.tight_layout()
        save_plot(plt, "31_founding_era_analysis.png")
    
    # ── 6.32 ── Radar Chart: Top Companies by Employee Scale (Sub-Rating Profile) ──
    top_emp_companies = company_demo[company_demo['global_emp'].notna()].nlargest(5, 'global_emp')
    radar_emp_data = top_emp_companies.set_index('Company')[
        ['avg_culture', 'avg_salary', 'avg_wlb', 'avg_satisfaction',
         'avg_skill', 'avg_security', 'avg_promotions']
    ]
    radar_emp_data.columns = SUB_RATINGS  # Align with existing sub-rating names
    
    N_emp = len(SUB_RATINGS)
    angles_emp = [n / float(N_emp) * 2 * pi for n in range(N_emp)]
    angles_emp += angles_emp[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    palette_emp = sns.color_palette("husl", len(radar_emp_data))
    for idx, (company, row) in enumerate(radar_emp_data.iterrows()):
        values = row.values.flatten().tolist()
        values += values[:1]
        ax.plot(angles_emp, values, 'o-', linewidth=2.5, label=company, color=palette_emp[idx])
        ax.fill(angles_emp, values, alpha=0.08, color=palette_emp[idx])
    
    ax.set_xticks(angles_emp[:-1])
    ax.set_xticklabels(SUB_RATINGS, fontsize=10)
    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
    ax.set_title('Sub-Rating Profiles: Top 5 Companies by Global Employee Count', fontsize=15, pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    save_plot(plt, "32_radar_top_by_employee_scale.png")
    
    # ── 6.33 ── Summary: Comprehensive Correlation (All Numeric Features) ──
    all_numeric_cols = ['Rating', '#Reviews',
                        'Industry level insights (%: -100 (below industry\'s average) to 100)',
                        'Sample Avg Insights'] + SUB_RATINGS + ['Founded in', 'India Employee Count', 'Global Employee Count']
    all_numeric = df[all_numeric_cols].select_dtypes(include=[np.number])
    all_corr = all_numeric.corr()
    
    fig, ax = plt.subplots(figsize=(16, 13))
    mask = np.triu(np.ones_like(all_corr, dtype=bool), k=1)
    sns.heatmap(all_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
                annot_kws={'fontsize': 7}, linewidths=0.5)
    ax.set_title('Comprehensive Correlation Matrix (All Numeric Features)', fontsize=15, pad=18)
    ax.tick_params(axis='both', labelsize=9)
    save_plot(plt, "33_comprehensive_correlation_heatmap.png")
    
    # ── 6.34 ── India Employee Count vs Global Employee Count (direct comparison) ──
    both_emp = company_demo[company_demo['india_emp'].notna() & company_demo['global_emp'].notna()]
    
    fig, ax = plt.subplots(figsize=(9, 9))
    # Reference line for 1:1 ratio
    max_emp = max(both_emp['india_emp'].max(), both_emp['global_emp'].max()) * 1.1
    ax.plot([0, max_emp], [0, max_emp], 'k--', alpha=0.3, linewidth=1, label='1:1 ratio')
    ax.fill_between([0, max_emp], [0, max_emp], [0, max_emp * 0.5], alpha=0.05, color='green', label='India-heavy')
    ax.fill_between([0, max_emp], [0, max_emp * 0.5], [0, 0], alpha=0.05, color='blue', label='Global-heavy')
    
    scatter = ax.scatter(both_emp['global_emp'], both_emp['india_emp'],
                         s=both_emp['total_reviews'] / 10 + 80,
                         c=both_emp['avg_rating'], cmap='RdYlGn', alpha=0.85,
                         edgecolors='#2c3e50', linewidth=1.2)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Average Rating', fontsize=11)
    ax.set_xlabel('Global Employee Count', fontsize=12)
    ax.set_ylabel('India Employee Count', fontsize=12)
    ax.set_title('India vs Global Employee Count\n(color = avg rating, size = reviews)', fontsize=14, pad=15)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(both_emp['global_emp'].min() * 0.7, both_emp['global_emp'].max() * 1.5)
    ax.set_ylim(both_emp['india_emp'].min() * 0.7, both_emp['india_emp'].max() * 1.5)
    ax.grid(True, linestyle='--', alpha=0.4)
    for _, row in both_emp.iterrows():
        ax.annotate(f"{row['Company']}\n({row['india_pct_of_global']:.0f}% in India)",
                    (row['global_emp'], row['india_emp']),
                    textcoords="offset points", xytext=(8, 8),
                    fontsize=8, ha='left')
    ax.legend(fontsize=9, loc='lower right')
    save_plot(plt, "34_india_vs_global_scatter.png")
    
    print(f"\n  ✓ Section 6 complete — 12 plots saved.")

if __name__ == "__main__":
    run()
