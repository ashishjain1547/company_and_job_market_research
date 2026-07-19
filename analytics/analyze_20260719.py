import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import time as _time

# ═══════════════════════════════════════════════════════════════════
# Progress tracking — start the clock immediately
# ═══════════════════════════════════════════════════════════════════
_script_start = _time.time()
_current_section = None

def _section(name):
    """Print a section header with timestamp."""
    global _current_section
    _current_section = name
    elapsed = _time.time() - _script_start
    print(f"\n{'='*70}")
    print(f"[{elapsed:6.1f}s] ═══ {name} ═══")
    print(f"{'='*70}")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
EXCEL_PATH = "/home/jain/Desktop/ws/public/company_and_job_market_research/ratings_and_reviews_at_ambitionbox.xlsx"
SAVE_DIR_BASE = "/home/jain/Desktop/ws/public/company_and_job_market_research/analytics/imgs"
SHEET_NAME = "Sheet1"

# Create a timestamped output folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(SAVE_DIR_BASE, f"img_{timestamp}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------
# 1. Data Loading & Preprocessing
# -------------------------------------------------------------------
df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

# Coerce all numeric-looking columns to numbers (fixes '-' and other
# non-numeric strings that break mean/sum/corr operations)
NUMERIC_COLS = [
    'Rating', '#Reviews',
    'Industry level insights (%: -100 (below industry\'s average) to 100)',
    'Sample Avg Insights',
    'Company Culture', 'Salary', 'Work-Life Balance',
    'Work Satisfaction', 'Skill Development', 'Job Security', 'Promotions',
    'Founded in', 'India Employee Count', 'Global Employee Count',
    'Avg Salary (L/Yr)', 'My YOE',
    'Median current employee tenure (in years)',
    'Employee Count Growth 6M %', 'Employee Count Growth 1Y %',
    'Employee Count Growth 2Y %',
    'Hiring Trend (6M)', 'New Hires (6M)',
]
for col in NUMERIC_COLS:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Parse dates (format: "Jan / 16 / 2026")
df['Date'] = pd.to_datetime(df['Date'], format='%b / %d / %Y')

# Sort descending by Date so that 'first()' aggregations
# and iloc[0] picks always use the latest row for each company
df = df.sort_values('Date', ascending=False).reset_index(drop=True)

# Extract month/year for later trends
df['YearMonth'] = df['Date'].dt.to_period('M')

# Summary statistics
print("Data loaded successfully. Shape:", df.shape)
print(f"  Companies: {df['Company'].nunique()}, Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print("  Columns:", list(df.columns))
print(f"  ⏱ Data loading & preprocessing took {_time.time() - _script_start:.1f}s\n")

# -------------------------------------------------------------------
# 2. Visualization Settings
# -------------------------------------------------------------------
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")
COLORS = sns.color_palette("husl", 10)

# Helper to save plots (with progress logging)
def save_plot(plt, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    rel = os.path.relpath(path, SAVE_DIR_BASE)
    print(f"  └─ saved → {rel}")

# -------------------------------------------------------------------
# 3. Mandatory Plots (with enhancements)
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# 4. Additional Insightful Plots
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# 5. Sub-Rating Analysis Plots
#    Columns: Company Culture, Salary, Work-Life Balance,
#             Work Satisfaction, Skill Development, Job Security, Promotions
# -------------------------------------------------------------------
_section("SECTION 5: Sub-Rating Analysis (13-22)")

SUB_RATINGS = [
    'Company Culture', 'Salary', 'Work-Life Balance',
    'Work Satisfaction', 'Skill Development', 'Job Security', 'Promotions'
]

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

# -------------------------------------------------------------------
# 6. Company Demographics & Scale Analysis (New Columns)
#    Columns: Founded in, India Employee Count, Global Employee Count
#    Also leverages: Company Industry (where available)
# -------------------------------------------------------------------
_section("SECTION 6: Company Demographics & Scale (23-34)")

NEW_COLS = ['Founded in', 'India Employee Count', 'Global Employee Count']

# Compute helper columns for company-level aggregation
company_demo = df.groupby('Company').agg(
    avg_rating=('Rating', 'mean'),
    total_reviews=('#Reviews', 'sum'),
    founded=('Founded in', 'first'),
    india_emp=('India Employee Count', 'first'),
    global_emp=('Global Employee Count', 'first'),
    industry=('Company Industry', 'first'),
    avg_culture=('Company Culture', 'mean'),
    avg_salary=('Salary', 'mean'),
    avg_wlb=('Work-Life Balance', 'mean'),
    avg_satisfaction=('Work Satisfaction', 'mean'),
    avg_skill=('Skill Development', 'mean'),
    avg_security=('Job Security', 'mean'),
    avg_promotions=('Promotions', 'mean'),
    median_tenure=('Median current employee tenure (in years)', 'first'),
).reset_index()

# Add derived metrics
current_year = 2026
company_demo['company_age'] = current_year - company_demo['founded']
company_demo['india_pct_of_global'] = (company_demo['india_emp'] / company_demo['global_emp'] * 100).round(1)

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
                    'Sample Avg Insights'] + SUB_RATINGS + NEW_COLS
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

# -------------------------------------------------------------------
# 7. Revenue Analysis (New Column: "Annual Revenue as of Jun 2026")
#    Values like: "USD 2.67 trillion", "USD 319 million",
#                 "Not publicly disclosed"
# -------------------------------------------------------------------
_section("SECTION 7: Revenue Analysis (35-45)")

import re

def _parse_revenue_usd(rev_str) -> float | None:
    """
    Parse revenue strings into numeric USD.
    Handles: 'USD 73.10 billion', '$14.4 billion (2025)',
             'USD 2.0 billion (FY2025, est.)', 'Not publicly disclosed', etc.
    Returns float (USD) or None if undisclosed/unparseable.
    """
    if not isinstance(rev_str, str):
        return None
    if 'not publicly disclosed' in rev_str.lower() or 'not available' in rev_str.lower():
        return None

    # Clean HTML entities, citations, parentheticals, stray spaces
    clean = re.sub(r'&#91;.*?&#93;', '', rev_str)
    clean = re.sub(r'\(.*?\)', '', clean)
    clean = clean.replace('$', 'USD ').replace('\u20b9', 'INR ')  # Rs.
    clean = re.sub(r'\s+', ' ', clean).strip()

    # Extract: [currency] [number] [scale_word]
    pattern = re.compile(
        r'(?:USD|US\s*\$?|INR|Rs\.?)\s*([\d,.]+)\s*(trillion|billion|million|crore|lakh)?',
        re.IGNORECASE,
    )
    m = pattern.search(clean)
    if not m:
        return None

    num = float(m.group(1).replace(',', ''))
    scale = (m.group(2) or '').lower()

    multipliers = {
        'trillion': 1e12, 'billion': 1e9, 'million': 1e6,
        'crore': 1e7, 'lakh': 1e5,
    }
    mult = multipliers.get(scale, 1)

    # Detect INR → USD conversion (crude heuristic: if INR value is in
    # trillions, it's likely INR, not USD; convert at ~85 INR/USD)
    inr_detected = bool(re.search(r'INR|Rs\.?|Rs.', rev_str, re.IGNORECASE))
    if inr_detected and scale == 'trillion':
        # INR trillion → USD billion (divide by ~85)
        return (num * 1e12) / 85.0
    if inr_detected and scale == 'crore':
        return (num * 1e7) / 85.0

    return num * mult


def _rev_fmt(val_usd: float) -> str:
    """Format a USD float into a readable short string."""
    if val_usd >= 1e12:
        return f'${val_usd/1e12:.1f}T'
    if val_usd >= 1e9:
        return f'${val_usd/1e9:.1f}B'
    if val_usd >= 1e6:
        return f'${val_usd/1e6:.0f}M'
    return f'${val_usd:,.0f}'


# Parse revenue column into numeric (add to company-level aggregation)
company_demo['revenue_usd'] = company_demo['Company'].map(
    lambda c: _parse_revenue_usd(
        df.loc[df['Company'] == c, 'Annual Revenue as of Jun 2026'].iloc[0]
    )
)
# Also add to main df for row-level plots
df['revenue_usd'] = df['Company'].map(
    company_demo.set_index('Company')['revenue_usd']
)

# Flag which companies disclosed revenue
company_demo['has_revenue'] = company_demo['revenue_usd'].notna()
rev_data = company_demo[company_demo['has_revenue']].copy()
rev_data['revenue_per_employee'] = (
    rev_data['revenue_usd'] / rev_data['global_emp']
)
rev_data['revenue_per_india_employee'] = (
    rev_data['revenue_usd'] / rev_data['india_emp']
)

num_disclosed = company_demo['has_revenue'].sum()
num_total = len(company_demo)
print(
    f"\nRevenue parsed: {num_disclosed}/{num_total} companies "
    f"have disclosed revenue"
)

# ── 7.35 ── Revenue Distribution (Histogram, log scale) ──
fig, ax = plt.subplots(figsize=(10, 6))
log_rev = np.log10(rev_data['revenue_usd'].dropna())
sns.histplot(log_rev, bins=15, kde=True, color='#2ecc71',
             edgecolor='#1e8449', ax=ax)
ax.set_title('Distribution of Annual Revenue (Log Scale)',
             fontsize=14, pad=15)
ax.set_xlabel('Log₁₀(Annual Revenue in USD)', fontsize=12)
ax.set_ylabel('Number of Companies', fontsize=12)
# Add original-scale annotations on the x-axis
tick_positions = [6, 7, 8, 9, 10, 11, 12]
tick_labels = ['$1M', '$10M', '$100M', '$1B', '$10B', '$100B', '$1T']
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, fontsize=9)
ax.axvline(log_rev.median(), color='red', linestyle='--', linewidth=2,
           label=f'Median: {_rev_fmt(rev_data["revenue_usd"].median())}')
ax.legend(fontsize=10)
save_plot(plt, "35_revenue_distribution_hist.png")

# ── 7.36 ── Top Companies by Annual Revenue (Horizontal Bar) ──
top_rev = rev_data.nlargest(20, 'revenue_usd').sort_values('revenue_usd')

fig, ax = plt.subplots(figsize=(12, 8))
rev_colors = plt.cm.YlOrRd(0.2 + 0.7 * np.linspace(0, 1, len(top_rev)))
bars = ax.barh(top_rev['Company'], top_rev['revenue_usd'],
               color=rev_colors, edgecolor='white')
ax.set_xscale('log')
ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_title('Top Companies by Annual Revenue (as of Jun 2026)',
             fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.4)
for bar, (_, row) in zip(bars, top_rev.iterrows()):
    ax.text(bar.get_width() * 1.02, bar.get_y() + bar.get_height() / 2,
            f'{_rev_fmt(row["revenue_usd"]):>6s}  *{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')
save_plot(plt, "36_top_companies_by_revenue.png")

# ── 7.37 ── Revenue vs Rating (Scatter, bubble = global employees) ──
fig, ax = plt.subplots(figsize=(12, 7))
scatter = ax.scatter(
    rev_data['revenue_usd'], rev_data['avg_rating'],
    s=rev_data['global_emp'].fillna(1000) / 35 + 80,
    c=rev_data['company_age'].fillna(20), cmap='viridis',
    alpha=0.8, edgecolors='#2c3e50', linewidth=1.2,
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Company Age (years)', fontsize=11)
ax.set_xscale('log')
ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_ylabel('Average Rating', fontsize=12)
ax.set_title(
    'Revenue vs Rating\n'
    '(bubble size = global employees, color = company age)',
    fontsize=14, pad=15,
)
ax.grid(True, linestyle='--', alpha=0.4)
# Trend line
mask = rev_data['revenue_usd'].notna() & rev_data['avg_rating'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(rev_data.loc[mask, 'revenue_usd']),
                   rev_data.loc[mask, 'avg_rating'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(rev_data['revenue_usd'].min()),
                         np.log10(rev_data['revenue_usd'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7,
            label='Trend')
# Annotate all points
for _, row in rev_data.iterrows():
    ax.annotate(row['Company'], (row['revenue_usd'], row['avg_rating']),
                textcoords="offset points", xytext=(6, 6),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
ax.set_ylim(rev_data['avg_rating'].min() - 0.3,
            rev_data['avg_rating'].max() + 0.4)
save_plot(plt, "37_revenue_vs_rating.png")

# ── 7.38 ── Revenue vs Global Employee Count (Scatter with trend) ──
both_data = rev_data[rev_data['global_emp'].notna()]

fig, ax = plt.subplots(figsize=(10, 8))
scatter = ax.scatter(
    both_data['global_emp'], both_data['revenue_usd'],
    s=both_data['avg_rating'] * 40 + 20,
    c=both_data['india_pct_of_global'].fillna(50), cmap='coolwarm',
    alpha=0.85, edgecolors='#2c3e50', linewidth=1,
    vmin=0, vmax=100,
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('India Workforce %', fontsize=11)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
ax.set_ylabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_title(
    'Revenue vs Global Employees\n'
    '(color = India workforce %, size = rating)',
    fontsize=14, pad=15,
)
ax.grid(True, linestyle='--', alpha=0.4)

# Revenue-per-employee reference lines
emp_min = both_data['global_emp'].min() * 0.8
emp_max = both_data['global_emp'].max() * 1.2
emp_range = np.logspace(np.log10(emp_min), np.log10(emp_max), 100)
for rpe_usd, label, ls, col in [
    (50_000, '$50K/emp', ':', '#95a5a6'),
    (200_000, '$200K/emp', '--', '#7f8c8d'),
    (1_000_000, '$1M/emp', '-.', '#555'),
]:
    ax.plot(emp_range, rpe_usd * emp_range, ls, color=col, alpha=0.5,
            linewidth=1, label=label)

for _, row in both_data.iterrows():
    ax.annotate(row['Company'], (row['global_emp'], row['revenue_usd']),
                textcoords="offset points", xytext=(7, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9, title='Revenue/Emp')
save_plot(plt, "38_revenue_vs_employees.png")

# ── 7.39 ── Revenue per Employee (Bar Chart, efficiency metric) ──
rpe_data = rev_data[
    rev_data['revenue_per_employee'].notna()
    & (rev_data['revenue_per_employee'] > 0)
].sort_values('revenue_per_employee')

fig, ax = plt.subplots(figsize=(10, 7))
rpe_colors = plt.cm.RdYlGn(
    0.15 + 0.7 * np.linspace(0, 1, len(rpe_data))
)
bars = ax.barh(rpe_data['Company'], rpe_data['revenue_per_employee'],
               color=rpe_colors, edgecolor='white')
ax.set_xscale('log')
ax.set_xlabel('Revenue per Global Employee (USD, log scale)', fontsize=12)
ax.set_title(
    'Revenue per Employee (Efficiency Proxy)\n'
    'Higher = more revenue generated per head',
    fontsize=14, pad=15,
)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.axvline(50_000, color='#e74c3c', linestyle='--', linewidth=1.5,
           alpha=0.6, label='$50K/emp (typical IT services)')
for bar, (_, row) in zip(bars, rpe_data.iterrows()):
    rpe_k = row['revenue_per_employee'] / 1_000
    ax.text(row['revenue_per_employee'] * 1.05,
            bar.get_y() + bar.get_height() / 2,
            f'${rpe_k:,.0f}K', va='center', fontsize=9, fontweight='bold')
ax.legend(fontsize=9, loc='lower right')
save_plot(plt, "39_revenue_per_employee.png")

# ── 7.40 ── Revenue vs Total Reviews (Scatter) ──
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(
    rev_data['revenue_usd'], rev_data['total_reviews'],
    s=rev_data['avg_rating'] * 50 + 30,
    c=rev_data['company_age'].fillna(20), cmap='plasma',
    alpha=0.8, edgecolors='white', linewidth=1,
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Company Age (years)', fontsize=11)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_ylabel('Total Reviews (log scale)', fontsize=12)
ax.set_title(
    'Revenue vs Review Volume\n'
    '(size = rating, color = company age)',
    fontsize=14, pad=15,
)
ax.grid(True, linestyle='--', alpha=0.4)
# Trend line
mask = (rev_data['revenue_usd'].notna()
        & (rev_data['total_reviews'] > 0))
if mask.sum() > 2:
    z = np.polyfit(np.log10(rev_data.loc[mask, 'revenue_usd']),
                   np.log10(rev_data.loc[mask, 'total_reviews']), 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(rev_data['revenue_usd'].min()),
                         np.log10(rev_data['revenue_usd'].max()), 100)
    ax.plot(10 ** x_line, 10 ** p(x_line), 'k--', linewidth=1.5,
            alpha=0.6, label=f'Slope: {z[0]:.2f}')
for _, row in rev_data.iterrows():
    ax.annotate(row['Company'],
                (row['revenue_usd'], row['total_reviews']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "40_revenue_vs_reviews.png")

# ── 7.41 ── Revenue per Employee vs India Workforce % ──
rpe_pct_data = rev_data[
    rev_data['revenue_per_employee'].notna()
    & rev_data['india_pct_of_global'].notna()
]

fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(
    rpe_pct_data['india_pct_of_global'],
    rpe_pct_data['revenue_per_employee'],
    s=rpe_pct_data['total_reviews'] / 10 + 50,
    c=rpe_pct_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
    edgecolors='#2c3e50', linewidth=1,
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_yscale('log')
ax.set_xlabel('India Workforce as % of Global', fontsize=12)
ax.set_ylabel('Revenue per Employee (USD, log scale)', fontsize=12)
ax.set_title(
    'Revenue Efficiency vs India Workforce Concentration\n'
    '(size = reviews, color = rating)',
    fontsize=14, pad=15,
)
ax.axvline(50, color='#7f8c8d', linestyle='--', alpha=0.5,
           label='50% India workforce')
ax.grid(True, linestyle='--', alpha=0.4)
for _, row in rpe_pct_data.iterrows():
    ax.annotate(row['Company'],
                (row['india_pct_of_global'],
                 row['revenue_per_employee']),
                textcoords="offset points", xytext=(6, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "41_revenue_per_emp_vs_india_pct.png")

# ── 7.42 ── Revenue vs Company Age ──
age_rev_data = rev_data[rev_data['company_age'].notna()]

fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(
    age_rev_data['company_age'], age_rev_data['revenue_usd'],
    s=age_rev_data['global_emp'].fillna(1000) / 30 + 60,
    c=age_rev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
    edgecolors='white', linewidth=1.2,
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_yscale('log')
ax.set_xlabel('Company Age (years since founding)', fontsize=12)
ax.set_ylabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_title(
    'Revenue vs Company Age\n'
    '(size = global employees, color = rating)',
    fontsize=14, pad=15,
)
ax.grid(True, linestyle='--', alpha=0.4)
# Trend line
mask = (age_rev_data['company_age'].notna()
        & age_rev_data['revenue_usd'].notna())
if mask.sum() > 2:
    z = np.polyfit(age_rev_data.loc[mask, 'company_age'],
                   np.log10(age_rev_data.loc[mask, 'revenue_usd']), 1)
    p = np.poly1d(z)
    x_line = np.linspace(age_rev_data['company_age'].min(),
                         age_rev_data['company_age'].max(), 100)
    ax.plot(x_line, 10 ** p(x_line), 'k--', linewidth=1.5, alpha=0.6,
            label='Trend')
for _, row in age_rev_data.iterrows():
    ax.annotate(row['Company'],
                (row['company_age'], row['revenue_usd']),
                textcoords="offset points", xytext=(6, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "42_revenue_vs_company_age.png")

# ── 7.43 ── Revenue Category Breakdown (Pie + Counts) ──
bins_rev = [0, 1e9, 10e9, 50e9, 200e9, np.inf]
labels_rev = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
rev_data['revenue_tier'] = pd.cut(
    rev_data['revenue_usd'], bins=bins_rev, labels=labels_rev, right=False,
)
tier_counts = (
    rev_data['revenue_tier'].value_counts()
    .reindex(labels_rev).fillna(0).astype(int)
)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Left: Pie chart
tier_colors = sns.color_palette("YlOrRd", len(labels_rev))
wedges, texts, autotexts = axes[0].pie(
    tier_counts.values, labels=None, autopct='%1.1f%%',
    startangle=90, colors=tier_colors,
    explode=[0.02] * len(labels_rev),
)
axes[0].set_title('Revenue Tier Distribution', fontsize=13)

# Right: Bar chart with average rating per tier
tier_avg_rating = (
    rev_data.groupby('revenue_tier', observed=False)['avg_rating']
    .mean().reindex(labels_rev)
)
bars = axes[1].bar(labels_rev, tier_counts.values, color=tier_colors,
                   edgecolor='white')
axes[1].set_title('Companies per Revenue Tier', fontsize=13)
axes[1].set_xlabel('Revenue Tier', fontsize=11)
axes[1].set_ylabel('Number of Companies', fontsize=11)
for bar, count, rating in zip(bars, tier_counts.values,
                               tier_avg_rating.values):
    if count > 0:
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.15,
                     f'n={count}\n*{rating:.1f}',
                     ha='center', fontsize=10, fontweight='bold')

# Combined legend
axes[0].legend(
    wedges,
    [f'{lbl} (n={cnt})' for lbl, cnt in zip(labels_rev, tier_counts.values)],
    title="Revenue Tier", loc="center left",
    bbox_to_anchor=(1, 0.5), fontsize=9,
)

fig.suptitle('Revenue Segmentation Analysis', fontsize=15, y=1.02)
plt.tight_layout()
save_plot(plt, "43_revenue_tier_breakdown.png")

# ── 7.44 ── Revenue vs Sub-Ratings (Small Multiples) ──
sub_rating_cols_map = {
    'avg_culture': 'Culture',
    'avg_salary': 'Salary',
    'avg_wlb': 'Work-Life Balance',
    'avg_satisfaction': 'Work Satisfaction',
    'avg_skill': 'Skill Development',
    'avg_security': 'Job Security',
    'avg_promotions': 'Promotions',
}

fig, axes = plt.subplots(3, 3, figsize=(18, 16))
axes = axes.flatten()

for i, (col, label) in enumerate(sub_rating_cols_map.items()):
    ax = axes[i]
    sub_data = rev_data[rev_data[col].notna()]
    scatter = ax.scatter(
        sub_data['revenue_usd'], sub_data[col],
        s=sub_data['total_reviews'] / 25 + 40,
        c=sub_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
        edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5,
    )
    ax.set_xscale('log')
    ax.set_xlabel('Revenue (USD, log)', fontsize=9)
    ax.set_ylabel(f'{label} Rating', fontsize=9)
    ax.set_title(f'{label}', fontsize=11, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_ylim(sub_data[col].min() - 0.4, sub_data[col].max() + 0.5)

    # Trend line
    mask = sub_data['revenue_usd'].notna() & sub_data[col].notna()
    if mask.sum() > 2:
        z = np.polyfit(np.log10(sub_data.loc[mask, 'revenue_usd']),
                       sub_data.loc[mask, col], 1)
        p = np.poly1d(z)
        x_line = np.linspace(np.log10(sub_data['revenue_usd'].min()),
                             np.log10(sub_data['revenue_usd'].max()), 100)
        ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1, alpha=0.6)

    # Correlation annotation
    corr_val = np.log10(sub_data['revenue_usd']).corr(sub_data[col])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    # Annotate outliers
    for _, row in sub_data.iterrows():
        ax.annotate(row['Company'], (row['revenue_usd'], row[col]),
                    textcoords="offset points", xytext=(4, 3),
                    fontsize=6, ha='left', alpha=0.9)

# Hide extra subplots
for j in range(len(sub_rating_cols_map), len(axes)):
    axes[j].set_visible(False)

fig.suptitle(
    'Revenue vs Sub-Ratings\n'
    '(color = overall rating, size = total reviews)',
    fontsize=16, y=1.01,
)
plt.tight_layout()
save_plot(plt, "44_revenue_vs_sub_ratings.png")

# ── 7.45 ── Summary: Revenue Correlation Heatmap ──
rev_corr_cols = [
    'revenue_usd', 'avg_rating', 'total_reviews',
    'global_emp', 'india_emp', 'india_pct_of_global', 'company_age',
]
rev_corr_labels = [
    'Revenue', 'Rating', 'Reviews', 'Global Emp',
    'India Emp', 'India %', 'Age (yrs)',
]

rev_corr_data = company_demo[rev_corr_cols].copy()
# Log-transform revenue and employee counts for correlation
for col in ['revenue_usd', 'global_emp', 'india_emp', 'total_reviews']:
    rev_corr_data[col] = np.log10(rev_corr_data[col].replace(0, np.nan))
rev_corr_data.columns = rev_corr_labels
rev_corr = rev_corr_data.corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(rev_corr, dtype=bool), k=1)
sns.heatmap(rev_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
            annot_kws={'fontsize': 10}, linewidths=0.5,
            cbar_kws={'label': 'Pearson r (log-transformed)'})
ax.set_title(
    'Revenue & Business Scale Correlation Matrix\n'
    '(log₁₀ transformed for scale variables)',
    fontsize=13, pad=15,
)
ax.tick_params(axis='both', labelsize=10)
save_plot(plt, "45_revenue_correlation_heatmap.png")

print(f"\nRevenue section plots saved (35–45).")
print(f"  ✓ Section 7 complete — 11 plots saved.")

# -------------------------------------------------------------------
# 8. Salary & Experience Analysis (New Columns)
#    Columns: Avg Salary (L/Yr) — in Lakhs/Year for ~13 YOE professional
#             My YOE — Years of Experience (constant: 13 yrs)
# -------------------------------------------------------------------
_section("SECTION 8: Salary & Experience Analysis (46-58)")

# Build company-level salary aggregates
company_salary = df.groupby('Company').agg(
    avg_salary_lyr=('Avg Salary (L/Yr)', 'mean'),
    salary_count=('Avg Salary (L/Yr)', 'count'),
    avg_rating=('Rating', 'mean'),
    total_reviews=('#Reviews', 'sum'),
    avg_salary_sub=('Salary', 'mean'),           # Salary sub-rating
    avg_wlb=('Work-Life Balance', 'mean'),
    avg_culture=('Company Culture', 'mean'),
    avg_satisfaction=('Work Satisfaction', 'mean'),
    avg_skill=('Skill Development', 'mean'),
    avg_security=('Job Security', 'mean'),
    avg_promotions=('Promotions', 'mean'),
    industry_deviation=('Industry level insights (%: -100 (below industry\'s average) to 100)', 'mean'),
    global_emp=('Global Employee Count', 'first'),
    india_emp=('India Employee Count', 'first'),
    founded=('Founded in', 'first'),
).reset_index()

# Merge revenue data
company_salary['revenue_usd'] = company_salary['Company'].map(
    lambda c: company_demo.set_index('Company')['revenue_usd'].get(c)
)
company_salary['company_age'] = current_year - company_salary['founded']

# Salary per YOE (proxy for per-year earning efficiency)
company_salary['salary_per_yoe'] = company_salary['avg_salary_lyr'] / 13.0

print(
    f"\nSalary data: {company_salary['avg_salary_lyr'].notna().sum()} companies "
    f"have salary data. "
    f"Range: Rs.{company_salary['avg_salary_lyr'].min():.1f}L–"
    f"Rs.{company_salary['avg_salary_lyr'].max():.1f}L/yr, "
    f"Median: Rs.{company_salary['avg_salary_lyr'].median():.1f}L/yr"
)

# ── 8.46 ── Salary Distribution (Histogram + KDE) ──
salary_clean = df['Avg Salary (L/Yr)'].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(salary_clean, bins=20, kde=True, color='#8e44ad',
             edgecolor='#6c3483', ax=ax)
ax.axvline(salary_clean.mean(), color='red', linestyle='--', linewidth=2,
           label=f'Mean: Rs.{salary_clean.mean():.1f}L/yr')
ax.axvline(salary_clean.median(), color='#e67e22', linestyle='--', linewidth=2,
           label=f'Median: Rs.{salary_clean.median():.1f}L/yr')
ax.set_title('Distribution of Average Salary (Lakhs/Year)\nfor ~13 YOE Professionals', fontsize=14, pad=15)
ax.set_xlabel('Avg Salary (Lakhs/Year)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.legend(fontsize=10)
save_plot(plt, "46_salary_distribution_hist.png")

# ── 8.47 ── Top Companies by Average Salary (Bar Chart) ──
top_salary = company_salary.dropna(subset=['avg_salary_lyr']).nlargest(20, 'avg_salary_lyr').sort_values('avg_salary_lyr')

fig, ax = plt.subplots(figsize=(12, 8))
sal_colors = plt.cm.RdYlGn(0.2 + 0.7 * np.linspace(0, 1, len(top_salary)))
bars = ax.barh(top_salary['Company'], top_salary['avg_salary_lyr'],
               color=sal_colors, edgecolor='white')
ax.set_xlabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Top 20 Companies by Average Salary\n(for ~13 YOE professionals)', fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.4)
for bar, (_, row) in zip(bars, top_salary.iterrows()):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'Rs.{row["avg_salary_lyr"]:.1f}L  *{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')
save_plot(plt, "47_top_companies_by_salary.png")

# ── 8.48 ── Salary vs Overall Rating (Scatter with regression) ──
sal_rating_data = company_salary.dropna(subset=['avg_salary_lyr', 'avg_rating'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(sal_rating_data['avg_rating'], sal_rating_data['avg_salary_lyr'],
                     s=sal_rating_data['total_reviews'] / 10 + 60,
                     c=sal_rating_data['company_age'].fillna(20), cmap='viridis',
                     alpha=0.8, edgecolors='#2c3e50', linewidth=1)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Company Age (years)', fontsize=11)
ax.set_xlabel('Average Overall Rating', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs Overall Rating\n(size = total reviews, color = company age)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Regression line
mask = sal_rating_data['avg_rating'].notna() & sal_rating_data['avg_salary_lyr'].notna()
if mask.sum() > 2:
    z = np.polyfit(sal_rating_data.loc[mask, 'avg_rating'],
                   sal_rating_data.loc[mask, 'avg_salary_lyr'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(sal_rating_data['avg_rating'].min(),
                         sal_rating_data['avg_rating'].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7,
            label=f'Slope: {z[0]:.1f} L/*')
    corr_val = sal_rating_data['avg_rating'].corr(sal_rating_data['avg_salary_lyr'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=11, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

for _, row in sal_rating_data.iterrows():
    ax.annotate(row['Company'], (row['avg_rating'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "48_salary_vs_rating.png")

# ── 8.49 ── Salary vs Revenue (Scatter, bubble = global employees) ──
sal_rev_data = company_salary.dropna(subset=['avg_salary_lyr', 'revenue_usd'])

fig, ax = plt.subplots(figsize=(12, 7))
scatter = ax.scatter(sal_rev_data['revenue_usd'], sal_rev_data['avg_salary_lyr'],
                     s=sal_rev_data['global_emp'].fillna(1000) / 30 + 80,
                     c=sal_rev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='#2c3e50', linewidth=1.2, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xscale('log')
ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs Company Revenue\n(size = global employees, color = rating)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

mask = sal_rev_data['revenue_usd'].notna() & sal_rev_data['avg_salary_lyr'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(sal_rev_data.loc[mask, 'revenue_usd']),
                   sal_rev_data.loc[mask, 'avg_salary_lyr'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(sal_rev_data['revenue_usd'].min()),
                         np.log10(sal_rev_data['revenue_usd'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in sal_rev_data.iterrows():
    ax.annotate(row['Company'], (row['revenue_usd'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "49_salary_vs_revenue.png")

# ── 8.50 ── Salary vs India Employee Count ──
sal_india_data = company_salary.dropna(subset=['avg_salary_lyr', 'india_emp'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(sal_india_data['india_emp'], sal_india_data['avg_salary_lyr'],
                     s=sal_india_data['total_reviews'] / 10 + 60,
                     c=sal_india_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xscale('log')
ax.set_xlabel('India Employee Count (log scale)', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs India Workforce Scale\n(size = reviews, color = rating)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

mask = sal_india_data['india_emp'].notna() & sal_india_data['avg_salary_lyr'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(sal_india_data.loc[mask, 'india_emp']),
                   sal_india_data.loc[mask, 'avg_salary_lyr'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(sal_india_data['india_emp'].min()),
                         np.log10(sal_india_data['india_emp'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in sal_india_data.iterrows():
    ax.annotate(row['Company'], (row['india_emp'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "50_salary_vs_india_employees.png")

# ── 8.51 ── Salary vs Sub-Ratings (Small Multiples) ──
salary_sub_map = {
    'avg_salary_sub': 'Salary (Sub-Rating)',
    'avg_wlb': 'Work-Life Balance',
    'avg_culture': 'Company Culture',
    'avg_satisfaction': 'Work Satisfaction',
    'avg_skill': 'Skill Development',
    'avg_security': 'Job Security',
    'avg_promotions': 'Promotions',
}

sal_sub_data = company_salary.dropna(subset=['avg_salary_lyr'])

fig, axes = plt.subplots(3, 3, figsize=(18, 16))
axes = axes.flatten()

for i, (col, label) in enumerate(salary_sub_map.items()):
    ax = axes[i]
    sub_clean = sal_sub_data.dropna(subset=[col])
    scatter = ax.scatter(sub_clean[col], sub_clean['avg_salary_lyr'],
                         s=sub_clean['total_reviews'] / 15 + 50,
                         c=sub_clean['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
    ax.set_xlabel(f'{label} Rating', fontsize=10)
    ax.set_ylabel('Avg Salary (L/yr)', fontsize=10)
    ax.set_title(f'{label}', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_xlim(sub_clean[col].min() - 0.3, sub_clean[col].max() + 0.4)
    ax.set_ylim(sub_clean['avg_salary_lyr'].min() - 5,
                sub_clean['avg_salary_lyr'].max() + 5)

    # Regression
    mask = sub_clean[col].notna() & sub_clean['avg_salary_lyr'].notna()
    if mask.sum() > 2:
        z = np.polyfit(sub_clean.loc[mask, col],
                       sub_clean.loc[mask, 'avg_salary_lyr'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sub_clean[col].min(), sub_clean[col].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.2, alpha=0.6)
    corr_val = sub_clean[col].corr(sub_clean['avg_salary_lyr'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    for _, row in sub_clean.iterrows():
        ax.annotate(row['Company'], (row[col], row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(4, 3),
                    fontsize=6, ha='left', alpha=0.85)

for j in range(len(salary_sub_map), len(axes)):
    axes[j].set_visible(False)

fig.suptitle('Salary vs Sub-Ratings\n(color = overall rating, size = total reviews)',
             fontsize=16, y=1.01)
plt.tight_layout()
save_plot(plt, "51_salary_vs_sub_ratings.png")

# ── 8.52 ── Salary vs Industry Deviation ──
sal_dev_data = company_salary.dropna(subset=['avg_salary_lyr', 'industry_deviation'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(sal_dev_data['industry_deviation'], sal_dev_data['avg_salary_lyr'],
                     s=sal_dev_data['total_reviews'] / 10 + 60,
                     c=sal_dev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.axvline(0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.set_xlabel('Industry Deviation (%)', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs Industry Deviation\n(size = reviews, color = rating)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Annotate all points
for _, row in sal_dev_data.iterrows():
    ax.annotate(row['Company'], (row['industry_deviation'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')

# Annotate quadrants
ax.text(0.98, 0.98, 'Above Industry\nHigh Salary → *',
        transform=ax.transAxes, fontsize=9, ha='right', va='top',
        bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.3))
ax.text(0.02, 0.98, 'Below Industry\nHigh Salary',
        transform=ax.transAxes, fontsize=9, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.3))
ax.text(0.98, 0.02, 'Above Industry\nLow Salary',
        transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3))
ax.text(0.02, 0.02, 'Below Industry\nLow Salary',
        transform=ax.transAxes, fontsize=9, ha='left', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.3))

save_plot(plt, "52_salary_vs_industry_deviation.png")

# ── 8.53 ── Salary/YOE Ratio by Company (Top 20) ──
# (Since YOE is constant at 13, this is effectively salary ÷ 13, but
#  placed here so the metric is readily interpretable if YOE varies later)
top_salary_per_yoe = company_salary.dropna(subset=['salary_per_yoe']).nlargest(20, 'salary_per_yoe').sort_values('salary_per_yoe')

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(top_salary_per_yoe['Company'], top_salary_per_yoe['salary_per_yoe'],
               color=plt.cm.Blues(0.3 + 0.7 * np.linspace(0, 1, len(top_salary_per_yoe))),
               edgecolor='white')
ax.set_xlabel('Salary per Year of Experience (Lakhs/YOE)', fontsize=12)
ax.set_title('Top 20 Companies by Salary per Year of Experience\n(Avg Salary ÷ Years of Experience)', fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.4)
for bar, (_, row) in zip(bars, top_salary_per_yoe.iterrows()):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'Rs.{row["salary_per_yoe"]:.1f}L/YOE  (Rs.{row["avg_salary_lyr"]:.0f}L @ 13yr)',
            va='center', fontsize=8.5, fontweight='bold')
save_plot(plt, "53_salary_per_yoe_by_company.png")

# ── 8.54 ── Salary Distribution by Revenue Tier (Violin Plot) ──
rev_tier_sal = company_salary.dropna(subset=['avg_salary_lyr', 'revenue_usd']).copy()
rev_tier_sal['revenue_tier'] = pd.cut(
    rev_tier_sal['revenue_usd'],
    bins=[0, 1e9, 10e9, 50e9, 200e9, np.inf],
    labels=['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B'],
    right=False,
)

fig, ax = plt.subplots(figsize=(12, 7))
tier_order = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
tier_palette = sns.color_palette("YlOrRd", len(tier_order))
sns.violinplot(data=rev_tier_sal, x='revenue_tier', y='avg_salary_lyr',
               hue='revenue_tier', palette=tier_palette, legend=False,
               order=tier_order, inner='quartile', ax=ax)
sns.stripplot(data=rev_tier_sal, x='revenue_tier', y='avg_salary_lyr',
              color='black', alpha=0.3, size=5, jitter=True, ax=ax)
# Annotate company names on stripplot points
for _, row in rev_tier_sal.iterrows():
    tier_idx = tier_order.index(row['revenue_tier']) if row['revenue_tier'] in tier_order else -1
    if tier_idx >= 0:
        ax.annotate(row['Company'], (tier_idx, row['avg_salary_lyr']),
                    textcoords="offset points", xytext=(0, 8),
                    fontsize=6, ha='center', alpha=0.7)

ax.set_title('Salary Distribution by Company Revenue Tier\n(for ~13 YOE professionals)', fontsize=14, pad=15)
ax.set_xlabel('Revenue Tier', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.3)
save_plot(plt, "54_salary_by_revenue_tier_violin.png")

# ── 8.55 ── Salary vs Total Reviews (Scatter) ──
sal_rev_count = company_salary.dropna(subset=['avg_salary_lyr', 'total_reviews'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(sal_rev_count['total_reviews'], sal_rev_count['avg_salary_lyr'],
                     s=sal_rev_count['avg_rating'] * 50 + 30,
                     c=sal_rev_count['company_age'].fillna(20), cmap='plasma',
                     alpha=0.8, edgecolors='white', linewidth=1)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Company Age (years)', fontsize=11)
ax.set_xscale('log')
ax.set_xlabel('Total Reviews (log scale)', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs Review Volume\n(size = rating, color = company age)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

mask = sal_rev_count['total_reviews'].notna() & sal_rev_count['avg_salary_lyr'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(sal_rev_count.loc[mask, 'total_reviews']),
                   sal_rev_count.loc[mask, 'avg_salary_lyr'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(sal_rev_count['total_reviews'].min()),
                         np.log10(sal_rev_count['total_reviews'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in sal_rev_count.iterrows():
    ax.annotate(row['Company'], (row['total_reviews'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "55_salary_vs_reviews.png")

# ── 8.56 ── Salary vs Company Age ──
sal_age_data = company_salary.dropna(subset=['avg_salary_lyr', 'company_age'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(sal_age_data['company_age'], sal_age_data['avg_salary_lyr'],
                     s=sal_age_data['global_emp'].fillna(1000) / 30 + 60,
                     c=sal_age_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1.2, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xlabel('Company Age (years since founding)', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs Company Age\n(size = global employees, color = rating)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

mask = sal_age_data['company_age'].notna() & sal_age_data['avg_salary_lyr'].notna()
if mask.sum() > 2:
    z = np.polyfit(sal_age_data.loc[mask, 'company_age'],
                   sal_age_data.loc[mask, 'avg_salary_lyr'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(sal_age_data['company_age'].min(),
                         sal_age_data['company_age'].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    corr_val = sal_age_data['company_age'].corr(sal_age_data['avg_salary_lyr'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=11, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

for _, row in sal_age_data.iterrows():
    ax.annotate(row['Company'], (row['company_age'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "56_salary_vs_company_age.png")

# ── 8.57 ── Salary vs Work-Life Balance (colored by Rating, bubble = revenue) ──
sal_wlb_data = company_salary.dropna(subset=['avg_salary_lyr', 'avg_wlb'])

fig, ax = plt.subplots(figsize=(11, 7))
bubble_sizes = sal_wlb_data['revenue_usd'].fillna(1e9).apply(
    lambda x: np.log10(x + 1) * 25 + 40
)
scatter = ax.scatter(sal_wlb_data['avg_wlb'], sal_wlb_data['avg_salary_lyr'],
                     s=bubble_sizes,
                     c=sal_wlb_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xlabel('Work-Life Balance Rating', fontsize=12)
ax.set_ylabel('Average Salary (Lakhs/Year)', fontsize=12)
ax.set_title('Salary vs Work-Life Balance\n(size = revenue, color = rating)\n"Can you have both high salary AND good WLB?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Quadrant reference lines
ax.axvline(sal_wlb_data['avg_wlb'].median(), color='gray', linestyle='--',
           alpha=0.4, linewidth=1)
ax.axhline(sal_wlb_data['avg_salary_lyr'].median(), color='gray', linestyle='--',
           alpha=0.4, linewidth=1)

# Quadrant labels
ax.text(0.98, 0.98, 'HIGH Salary\nGOOD WLB [BEST]', transform=ax.transAxes,
        fontsize=9, ha='right', va='top', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
ax.text(0.02, 0.98, 'LOW Salary\nGOOD WLB', transform=ax.transAxes,
        fontsize=9, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
ax.text(0.98, 0.02, 'HIGH Salary\nPOOR WLB [!]', transform=ax.transAxes,
        fontsize=9, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))
ax.text(0.02, 0.02, 'LOW Salary\nPOOR WLB', transform=ax.transAxes,
        fontsize=9, ha='left', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#95a5a6', alpha=0.25))

for _, row in sal_wlb_data.iterrows():
    ax.annotate(row['Company'], (row['avg_wlb'], row['avg_salary_lyr']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
# Correlation
corr_val = sal_wlb_data['avg_wlb'].corr(sal_wlb_data['avg_salary_lyr'])
ax.text(0.5, 0.01, f'Correlation (WLB vs Salary): r={corr_val:.2f}',
        transform=ax.transAxes, fontsize=10, ha='center', fontstyle='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
save_plot(plt, "57_salary_vs_wlb_quadrant.png")

# ── 8.58 ── Comprehensive Correlation Heatmap with Salary ──
salary_corr_cols = [
    'avg_salary_lyr', 'avg_rating', 'total_reviews',
    'avg_salary_sub', 'avg_wlb', 'avg_culture', 'avg_satisfaction',
    'avg_skill', 'avg_security', 'avg_promotions',
    'industry_deviation', 'global_emp', 'india_emp', 'company_age',
]
salary_corr_labels = [
    'Salary (L/Yr)', 'Rating', 'Reviews',
    'Salary *', 'WLB *', 'Culture *', 'Satisfaction *',
    'Skill *', 'Security *', 'Promotions *',
    'Ind. Dev%', 'Global Emp', 'India Emp', 'Age (yrs)',
]

salary_corr_df = company_salary[salary_corr_cols].copy()
# Log-transform scale variables
for col in ['global_emp', 'india_emp', 'total_reviews']:
    salary_corr_df[col] = np.log10(salary_corr_df[col].replace(0, np.nan))
salary_corr_df.columns = salary_corr_labels
salary_corr = salary_corr_df.corr()

fig, ax = plt.subplots(figsize=(14, 12))
mask = np.triu(np.ones_like(salary_corr, dtype=bool), k=1)
sns.heatmap(salary_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
            annot_kws={'fontsize': 8}, linewidths=0.5,
            cbar_kws={'label': 'Pearson r (log₁₀ for scale vars)'})
ax.set_title('Salary & Experience: Comprehensive Correlation Matrix\n(log₁₀ transformed for employee count & review variables)',
             fontsize=14, pad=18)
ax.tick_params(axis='both', labelsize=9)
save_plot(plt, "58_salary_correlation_heatmap.png")

print(f"\nSalary & Experience section plots saved (46–58).")
print(f"  ✓ Section 8 complete — 13 plots saved.")

# -------------------------------------------------------------------
# 9. Employee Tenure Analysis (New Column)
#    Column: "Median current employee tenure (in years)"
#    What it reveals: How long employees typically stay at each company.
#    Longer tenure often signals better retention, job security,
#    and possibly career growth, but could also indicate stagnation.
# -------------------------------------------------------------------
_section("SECTION 9: Employee Tenure Analysis (59-74)")

TENURE_COL = 'Median current employee tenure (in years)'

# Build a dedicated company-level tenure dataframe for convenience
company_tenure = company_demo[['Company', 'avg_rating', 'total_reviews',
    'company_age', 'global_emp', 'india_emp', 'india_pct_of_global',
    'revenue_usd', 'median_tenure',
    'avg_culture', 'avg_salary', 'avg_wlb', 'avg_satisfaction',
    'avg_skill', 'avg_security', 'avg_promotions']].copy()

# Filter to companies that have tenure data
tenure_data = company_tenure[company_tenure['median_tenure'].notna()].copy()
num_tenure = len(tenure_data)
print(
    f"\nTenure data: {num_tenure} companies have median tenure data."
    f"\n  Range: {tenure_data['median_tenure'].min():.1f} – "
    f"{tenure_data['median_tenure'].max():.1f} years, "
    f"Median: {tenure_data['median_tenure'].median():.1f} years"
)

# ── 9.59 ── Tenure Distribution (Histogram + KDE) ──
tenure_clean = df[TENURE_COL].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(tenure_clean, bins=18, kde=True, color='#1abc9c',
             edgecolor='#16a085', ax=ax)
ax.axvline(tenure_clean.mean(), color='#e74c3c', linestyle='--', linewidth=2,
           label=f'Mean: {tenure_clean.mean():.1f} yrs')
ax.axvline(tenure_clean.median(), color='#f39c12', linestyle='--', linewidth=2,
           label=f'Median: {tenure_clean.median():.1f} yrs')
ax.set_title('Distribution of Median Current Employee Tenure', fontsize=14, pad=15)
ax.set_xlabel('Median Tenure (Years)', fontsize=12)
ax.set_ylabel('Number of Companies', fontsize=12)
ax.legend(fontsize=10)
save_plot(plt, "59_tenure_distribution_hist.png")

# ── 9.60 ── Top 20 Companies by Longest Median Tenure ──
top_tenure = tenure_data.nlargest(20, 'median_tenure').sort_values('median_tenure')

fig, ax = plt.subplots(figsize=(12, 8))
tenure_bar_colors = plt.cm.Greens(0.3 + 0.7 * np.linspace(0, 1, len(top_tenure)))
bars = ax.barh(top_tenure['Company'], top_tenure['median_tenure'],
               color=tenure_bar_colors, edgecolor='white')
ax.set_xlabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Top 20 Companies by Longest Median Employee Tenure', fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.4)
for bar, (_, row) in zip(bars, top_tenure.iterrows()):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'{row["median_tenure"]:.1f} yrs  *{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')
save_plot(plt, "60_top_companies_by_tenure.png")

# ── 9.61 ── Bottom 20 Companies by Shortest Median Tenure ──
bottom_tenure = tenure_data.nsmallest(20, 'median_tenure').sort_values('median_tenure', ascending=False)

fig, ax = plt.subplots(figsize=(12, 8))
low_tenure_colors = plt.cm.Reds(0.3 + 0.7 * np.linspace(0, 1, len(bottom_tenure)))
bars = ax.barh(bottom_tenure['Company'], bottom_tenure['median_tenure'],
               color=low_tenure_colors, edgecolor='white')
ax.set_xlabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Bottom 20 Companies by Shortest Median Employee Tenure\n(Potential retention risk)', fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.4)
for bar, (_, row) in zip(bars, bottom_tenure.iterrows()):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'{row["median_tenure"]:.1f} yrs  *{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')
save_plot(plt, "61_bottom_companies_by_tenure.png")

# ── 9.62 ── Tenure vs Overall Rating (Scatter with regression) ──
tenure_rating_data = tenure_data.dropna(subset=['avg_rating'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(tenure_rating_data['avg_rating'], tenure_rating_data['median_tenure'],
                     s=tenure_rating_data['total_reviews'] / 10 + 60,
                     c=tenure_rating_data['company_age'].fillna(20), cmap='viridis',
                     alpha=0.8, edgecolors='#2c3e50', linewidth=1)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Company Age (years)', fontsize=11)
ax.set_xlabel('Average Overall Rating', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs Overall Rating\n(size = total reviews, color = company age)\n"Are better-rated companies better at retaining talent?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Regression line
mask = tenure_rating_data['avg_rating'].notna() & tenure_rating_data['median_tenure'].notna()
if mask.sum() > 2:
    z = np.polyfit(tenure_rating_data.loc[mask, 'avg_rating'],
                   tenure_rating_data.loc[mask, 'median_tenure'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(tenure_rating_data['avg_rating'].min(),
                         tenure_rating_data['avg_rating'].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7,
            label=f'Slope: {z[0]:.2f} yr/*')
    corr_val = tenure_rating_data['avg_rating'].corr(tenure_rating_data['median_tenure'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=11, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

for _, row in tenure_rating_data.iterrows():
    ax.annotate(row['Company'], (row['avg_rating'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "62_tenure_vs_rating.png")

# ── 9.63 ── Tenure vs Company Age (Scatter, bubble = global employees) ──
tenure_age_data = tenure_data.dropna(subset=['company_age'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(tenure_age_data['company_age'], tenure_age_data['median_tenure'],
                     s=tenure_age_data['global_emp'].fillna(1000) / 30 + 60,
                     c=tenure_age_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1.2, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xlabel('Company Age (years since founding)', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs Company Age\n(size = global employees, color = rating)\n"Do older companies naturally retain longer?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Trend line
mask = tenure_age_data['company_age'].notna() & tenure_age_data['median_tenure'].notna()
if mask.sum() > 2:
    z = np.polyfit(tenure_age_data.loc[mask, 'company_age'],
                   tenure_age_data.loc[mask, 'median_tenure'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(tenure_age_data['company_age'].min(),
                         tenure_age_data['company_age'].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    corr_val = tenure_age_data['company_age'].corr(tenure_age_data['median_tenure'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=11, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

for _, row in tenure_age_data.iterrows():
    ax.annotate(row['Company'], (row['company_age'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "63_tenure_vs_company_age.png")

# ── 9.64 ── Tenure vs Sub-Ratings (Small Multiples) ──
tenure_sub_map = {
    'avg_culture': 'Company Culture',
    'avg_salary': 'Salary (Sub-Rating)',
    'avg_wlb': 'Work-Life Balance',
    'avg_satisfaction': 'Work Satisfaction',
    'avg_skill': 'Skill Development',
    'avg_security': 'Job Security',
    'avg_promotions': 'Promotions',
}

fig, axes = plt.subplots(3, 3, figsize=(18, 16))
axes = axes.flatten()

for i, (col, label) in enumerate(tenure_sub_map.items()):
    ax = axes[i]
    sub_clean = tenure_data.dropna(subset=[col])
    scatter = ax.scatter(sub_clean[col], sub_clean['median_tenure'],
                         s=sub_clean['total_reviews'] / 15 + 50,
                         c=sub_clean['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
    ax.set_xlabel(f'{label} Rating', fontsize=10)
    ax.set_ylabel('Median Tenure (yrs)', fontsize=10)
    ax.set_title(f'{label}', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_xlim(sub_clean[col].min() - 0.3, sub_clean[col].max() + 0.4)
    ax.set_ylim(sub_clean['median_tenure'].min() - 0.8,
                sub_clean['median_tenure'].max() + 0.8)

    # Regression
    mask = sub_clean[col].notna() & sub_clean['median_tenure'].notna()
    if mask.sum() > 2:
        z = np.polyfit(sub_clean.loc[mask, col],
                       sub_clean.loc[mask, 'median_tenure'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sub_clean[col].min(), sub_clean[col].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.2, alpha=0.6)
    corr_val = sub_clean[col].corr(sub_clean['median_tenure'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    for _, row in sub_clean.iterrows():
        ax.annotate(row['Company'], (row[col], row['median_tenure']),
                    textcoords="offset points", xytext=(4, 3),
                    fontsize=6, ha='left', alpha=0.85)

for j in range(len(tenure_sub_map), len(axes)):
    axes[j].set_visible(False)

fig.suptitle('Employee Tenure vs Sub-Ratings\n(color = overall rating, size = total reviews)',
             fontsize=16, y=1.01)
plt.tight_layout()
save_plot(plt, "64_tenure_vs_sub_ratings.png")

# ── 9.65 ── Tenure vs Salary (Scatter with quadrant analysis) ──
tenure_sal_data = tenure_data.dropna(subset=['avg_salary'])

fig, ax = plt.subplots(figsize=(11, 7))
bubble_sizes = tenure_sal_data['revenue_usd'].fillna(1e9).apply(
    lambda x: np.log10(x + 1) * 25 + 40
)
scatter = ax.scatter(tenure_sal_data['avg_salary'], tenure_sal_data['median_tenure'],
                     s=bubble_sizes,
                     c=tenure_sal_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xlabel('Salary Sub-Rating (0–5)', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs Salary Rating\n(size = revenue, color = rating)\n"Does paying well keep employees longer?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Quadrant reference lines
ax.axvline(tenure_sal_data['avg_salary'].median(), color='gray', linestyle='--',
           alpha=0.4, linewidth=1)
ax.axhline(tenure_sal_data['median_tenure'].median(), color='gray', linestyle='--',
           alpha=0.4, linewidth=1)

# Quadrant labels
ax.text(0.98, 0.98, 'HIGH Pay\nLONG Tenure [★]', transform=ax.transAxes,
        fontsize=9, ha='right', va='top', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
ax.text(0.02, 0.98, 'LOW Pay\nLONG Tenure', transform=ax.transAxes,
        fontsize=9, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
ax.text(0.98, 0.02, 'HIGH Pay\nSHORT Tenure', transform=ax.transAxes,
        fontsize=9, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))
ax.text(0.02, 0.02, 'LOW Pay\nSHORT Tenure [!]', transform=ax.transAxes,
        fontsize=9, ha='left', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#95a5a6', alpha=0.25))

for _, row in tenure_sal_data.iterrows():
    ax.annotate(row['Company'], (row['avg_salary'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
corr_val = tenure_sal_data['avg_salary'].corr(tenure_sal_data['median_tenure'])
ax.text(0.5, 0.01, f'Correlation (Salary* vs Tenure): r={corr_val:.2f}',
        transform=ax.transAxes, fontsize=10, ha='center', fontstyle='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
save_plot(plt, "65_tenure_vs_salary_quadrant.png")

# ── 9.66 ── Tenure vs Global Employee Count (Scatter) ──
tenure_emp_data = tenure_data.dropna(subset=['global_emp'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(tenure_emp_data['global_emp'], tenure_emp_data['median_tenure'],
                     s=tenure_emp_data['total_reviews'] / 10 + 60,
                     c=tenure_emp_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xscale('log')
ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs Company Size\n(size = reviews, color = rating)\n"Do bigger companies retain employees longer?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

# Trend line
mask = tenure_emp_data['global_emp'].notna() & tenure_emp_data['median_tenure'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(tenure_emp_data.loc[mask, 'global_emp']),
                   tenure_emp_data.loc[mask, 'median_tenure'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(tenure_emp_data['global_emp'].min()),
                         np.log10(tenure_emp_data['global_emp'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in tenure_emp_data.iterrows():
    ax.annotate(row['Company'], (row['global_emp'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "66_tenure_vs_company_size.png")

# ── 9.67 ── Tenure by Revenue Tier (Violin Plot) ──
tenure_rev_data = tenure_data.dropna(subset=['revenue_usd']).copy()
tenure_rev_data['revenue_tier'] = pd.cut(
    tenure_rev_data['revenue_usd'],
    bins=[0, 1e9, 10e9, 50e9, 200e9, np.inf],
    labels=['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B'],
    right=False,
)

fig, ax = plt.subplots(figsize=(12, 7))
tier_order = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
tier_palette_tenure = sns.color_palette("GnBu_d", len(tier_order))
sns.violinplot(data=tenure_rev_data, x='revenue_tier', y='median_tenure',
               hue='revenue_tier', palette=tier_palette_tenure, legend=False,
               order=tier_order, inner='quartile', ax=ax)
sns.stripplot(data=tenure_rev_data, x='revenue_tier', y='median_tenure',
              color='black', alpha=0.3, size=5, jitter=True, ax=ax)
# Annotate company names
for _, row in tenure_rev_data.iterrows():
    tier_idx = tier_order.index(row['revenue_tier']) if row['revenue_tier'] in tier_order else -1
    if tier_idx >= 0:
        ax.annotate(row['Company'], (tier_idx, row['median_tenure']),
                    textcoords="offset points", xytext=(0, 8),
                    fontsize=6, ha='center', alpha=0.7)

ax.set_title('Employee Tenure Distribution by Revenue Tier\n"Do deep-pocket companies retain longer?"', fontsize=14, pad=15)
ax.set_xlabel('Revenue Tier', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.3)
save_plot(plt, "67_tenure_by_revenue_tier_violin.png")

# ── 9.68 ── Tenure vs Industry Deviation ──
tenure_dev_data = tenure_data.dropna(subset=['median_tenure'])
# Get industry deviation from company_demo
tenure_dev_data = tenure_dev_data.merge(
    company_demo[['Company', 'avg_rating']].rename(columns={'avg_rating': 'rating_ref'}),
    on='Company', how='left'
)

# Actually, let's compute industry deviation properly
ind_dev_map = df.groupby('Company')[
    'Industry level insights (%: -100 (below industry\'s average) to 100)'
].mean()
tenure_dev_data['industry_deviation'] = tenure_dev_data['Company'].map(ind_dev_map)
tenure_dev_data = tenure_dev_data.dropna(subset=['industry_deviation'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(tenure_dev_data['industry_deviation'], tenure_dev_data['median_tenure'],
                     s=tenure_dev_data['total_reviews'] / 10 + 60,
                     c=tenure_dev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.axvline(0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.set_xlabel('Industry Deviation (%)', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs Industry Standing\n"Do industry-leading companies have better retention?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

for _, row in tenure_dev_data.iterrows():
    ax.annotate(row['Company'], (row['industry_deviation'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')

# Quadrant labels
ax.text(0.98, 0.98, 'Above Industry\nLONG Tenure [★]',
        transform=ax.transAxes, fontsize=9, ha='right', va='top',
        bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
ax.text(0.02, 0.98, 'Below Industry\nLONG Tenure',
        transform=ax.transAxes, fontsize=9, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
ax.text(0.98, 0.02, 'Above Industry\nSHORT Tenure',
        transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.25))
ax.text(0.02, 0.02, 'Below Industry\nSHORT Tenure [!]',
        transform=ax.transAxes, fontsize=9, ha='left', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))

save_plot(plt, "68_tenure_vs_industry_deviation.png")

# ── 9.69 ── Tenure vs India Workforce % ──
tenure_india_data = tenure_data.dropna(subset=['india_pct_of_global'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(tenure_india_data['india_pct_of_global'],
                     tenure_india_data['median_tenure'],
                     s=tenure_india_data['total_reviews'] / 10 + 60,
                     c=tenure_india_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.axvline(50, color='#7f8c8d', linestyle='--', alpha=0.5,
           label='50% India workforce')
ax.set_xlabel('India Workforce as % of Global', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs India Workforce Concentration\n(size = reviews, color = rating)',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

mask = tenure_india_data['india_pct_of_global'].notna() & tenure_india_data['median_tenure'].notna()
if mask.sum() > 2:
    z = np.polyfit(tenure_india_data.loc[mask, 'india_pct_of_global'],
                   tenure_india_data.loc[mask, 'median_tenure'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(tenure_india_data['india_pct_of_global'].min(),
                         tenure_india_data['india_pct_of_global'].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in tenure_india_data.iterrows():
    ax.annotate(row['Company'],
                (row['india_pct_of_global'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "69_tenure_vs_india_pct.png")

# ── 9.70 ── Tenure Heatmap: Top 15 Companies × Key Metrics ──
tenure_heatmap_cols = [
    'median_tenure', 'avg_rating', 'company_age',
    'avg_culture', 'avg_salary', 'avg_wlb',
    'avg_satisfaction', 'avg_skill', 'avg_security', 'avg_promotions',
]
tenure_heatmap_labels = [
    'Tenure (yrs)', 'Rating', 'Age (yrs)',
    'Culture', 'Salary*', 'WLB',
    'Satisfaction', 'Skill', 'Security', 'Promotions',
]

top15_by_tenure = tenure_data.nlargest(15, 'median_tenure').set_index('Company')
tenure_heatmap_raw = top15_by_tenure[tenure_heatmap_cols]
tenure_heatmap_raw.columns = tenure_heatmap_labels

# Normalize columns to 0-1 for colormap
tenure_heatmap_norm = (tenure_heatmap_raw - tenure_heatmap_raw.min()) / \
                      (tenure_heatmap_raw.max() - tenure_heatmap_raw.min() + 1e-10)

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(tenure_heatmap_norm, annot=tenure_heatmap_raw.round(1), fmt='.1f',
            cmap='YlOrRd', ax=ax, linewidths=1, linecolor='white',
            annot_kws={'fontsize': 9}, cbar_kws={'label': 'Normalized Score (0–1)'})
ax.set_title('Top 15 Companies by Longest Tenure: Key Metrics Comparison', fontsize=14, pad=15)
ax.set_xlabel('')
ax.set_ylabel('')
ax.tick_params(axis='both', labelsize=10)
save_plot(plt, "70_tenure_heatmap_top15.png")

# ── 9.71 ── Tenure: Founding Era Breakdown ──
tenure_era_data = tenure_data.dropna(subset=['company_age']).copy()
tenure_era_data['founding_era'] = pd.cut(
    2026 - tenure_era_data['company_age'],
    bins=[1800, 1970, 2000, 2010, 2030],
    labels=['Pre-1970', '1970-1999', '2000-2010', 'Post-2010'],
)

tenure_era_stats = tenure_era_data.groupby('founding_era', observed=False).agg(
    avg_tenure=('median_tenure', 'mean'),
    median_tenure=('median_tenure', 'median'),
    company_count=('Company', 'count'),
).dropna().reset_index()

if len(tenure_era_stats) >= 2:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: avg tenure by era
    ax = axes[0]
    bars = ax.bar(tenure_era_stats['founding_era'], tenure_era_stats['avg_tenure'],
                  color=sns.color_palette("Greens_r", len(tenure_era_stats)), edgecolor='white')
    ax.set_title('Average Employee Tenure by Founding Era', fontsize=13)
    ax.set_ylabel('Average Median Tenure (Years)', fontsize=11)
    ax.set_xlabel('Founding Era', fontsize=11)
    ax.set_ylim(0, tenure_era_stats['avg_tenure'].max() * 1.3)
    for bar, val, cnt in zip(bars, tenure_era_stats['avg_tenure'], tenure_era_stats['company_count']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                f'{val:.1f} yrs\n(n={int(cnt)})', ha='center', fontsize=10, fontweight='bold')

    # Right: company count by era
    ax = axes[1]
    bars = ax.bar(tenure_era_stats['founding_era'], tenure_era_stats['company_count'],
                  color=sns.color_palette("Blues_r", len(tenure_era_stats)), edgecolor='white')
    ax.set_title('Number of Companies with Tenure Data per Era', fontsize=13)
    ax.set_ylabel('Company Count', fontsize=11)
    ax.set_xlabel('Founding Era', fontsize=11)
    for bar, val in zip(bars, tenure_era_stats['company_count']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(int(val)), ha='center', fontsize=11, fontweight='bold')

    fig.suptitle('Employee Tenure by Founding Era', fontsize=15, y=1.02)
    plt.tight_layout()
    save_plot(plt, "71_tenure_by_founding_era.png")

# ── 9.72 ── Tenure: Comprehensive Correlation Heatmap ──
tenure_corr_cols = [
    'median_tenure', 'avg_rating', 'total_reviews',
    'company_age', 'global_emp', 'india_emp', 'india_pct_of_global',
    'avg_culture', 'avg_salary', 'avg_wlb',
    'avg_satisfaction', 'avg_skill', 'avg_security', 'avg_promotions',
]
tenure_corr_labels = [
    'Tenure (yrs)', 'Rating', 'Reviews',
    'Age (yrs)', 'Global Emp', 'India Emp', 'India %',
    'Culture', 'Salary*', 'WLB',
    'Satisfaction', 'Skill', 'Security', 'Promotions',
]

tenure_corr_df = tenure_data[tenure_corr_cols].copy()
# Log-transform scale variables
for col in ['global_emp', 'india_emp', 'total_reviews']:
    tenure_corr_df[col] = np.log10(tenure_corr_df[col].replace(0, np.nan))
tenure_corr_df.columns = tenure_corr_labels
tenure_corr = tenure_corr_df.corr()

fig, ax = plt.subplots(figsize=(14, 12))
mask = np.triu(np.ones_like(tenure_corr, dtype=bool), k=1)
sns.heatmap(tenure_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
            annot_kws={'fontsize': 8}, linewidths=0.5,
            cbar_kws={'label': 'Pearson r (log₁₀ for scale vars)'})
# Highlight the tenure row
for i in range(tenure_corr.shape[1]):
    if i > 0:  # Skip self-correlation
        val = tenure_corr.iloc[0, i]
        color = '#2ecc71' if val > 0 else '#e74c3c' if val < -0.1 else '#666'
        ax.text(i + 0.5, 0.5, f'{val:.2f}', ha='center', va='center',
                fontsize=10, fontweight='bold', color=color)
ax.set_title('Employee Tenure: Comprehensive Correlation Matrix\n(log₁₀ transformed for employee count & review variables)\nFirst row = what correlates with tenure',
             fontsize=14, pad=18)
ax.tick_params(axis='both', labelsize=9)
save_plot(plt, "72_tenure_correlation_heatmap.png")

# ── 9.73 ── Tenure vs Revenue (Scatter) ──
tenure_rev_scatter = tenure_data.dropna(subset=['revenue_usd'])

fig, ax = plt.subplots(figsize=(12, 7))
scatter = ax.scatter(tenure_rev_scatter['revenue_usd'],
                     tenure_rev_scatter['median_tenure'],
                     s=tenure_rev_scatter['global_emp'].fillna(1000) / 30 + 80,
                     c=tenure_rev_scatter['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='#2c3e50', linewidth=1.2, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xscale('log')
ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_ylabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('Employee Tenure vs Company Revenue\n(size = global employees, color = rating)\n"Revenue-rich = retention-rich?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.4)

mask = tenure_rev_scatter['revenue_usd'].notna() & tenure_rev_scatter['median_tenure'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(tenure_rev_scatter.loc[mask, 'revenue_usd']),
                   tenure_rev_scatter.loc[mask, 'median_tenure'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(tenure_rev_scatter['revenue_usd'].min()),
                         np.log10(tenure_rev_scatter['revenue_usd'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in tenure_rev_scatter.iterrows():
    ax.annotate(row['Company'], (row['revenue_usd'], row['median_tenure']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "73_tenure_vs_revenue.png")

# ── 9.74 ── Tenure: "Retention Scorecard" — Combined Bar (Tenure + Rating) ──
# Sort by tenure, annotate with rating; a quick-glance retention dashboard
scorecard_data = tenure_data.nlargest(25, 'median_tenure').sort_values('median_tenure')

fig, ax = plt.subplots(figsize=(12, 9))
# Color bars by rating (green = high rating, red = lower)
scorecard_norm = plt.Normalize(scorecard_data['avg_rating'].min(),
                                scorecard_data['avg_rating'].max())
scorecard_colors = plt.cm.RdYlGn(0.15 + 0.7 * scorecard_norm(scorecard_data['avg_rating']))
bars = ax.barh(scorecard_data['Company'], scorecard_data['median_tenure'],
               color=scorecard_colors, edgecolor='#2c3e50', linewidth=0.8)
ax.set_xlabel('Median Employee Tenure (Years)', fontsize=12)
ax.set_title('🏆 Retention Scorecard: Top 25 Companies by Employee Tenure\n(Color = overall rating: green→high, red→lower)',
             fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.4)

# Add a colorbar as legend for rating
sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=scorecard_norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('Overall Rating', fontsize=11)

for bar, (_, row) in zip(bars, scorecard_data.iterrows()):
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
            f'{row["median_tenure"]:.1f} yrs  ★{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')
save_plot(plt, "74_tenure_retention_scorecard.png")

print(f"\nEmployee Tenure section plots saved (59–74).")
print(f"  ✓ Section 9 complete — 16 plots saved.")

# -------------------------------------------------------------------
# 10. Employee Count Growth & Hiring Trends Analysis (New Columns)
#     Columns: Employee Count Growth 6M %, Employee Count Growth 1Y %,
#              Employee Count Growth 2Y %,
#              Hiring Trend (6M), New Hires (6M)
#     What they reveal: Which companies are expanding headcount fastest,
#     hiring momentum, and how growth correlates with ratings, revenue,
#     and other company attributes.
# -------------------------------------------------------------------
_section("SECTION 10: Employee Growth & Hiring Trends (75-91)")

GROWTH_COLS = [
    'Employee Count Growth 6M %',
    'Employee Count Growth 1Y %',
    'Employee Count Growth 2Y %',
]
HIRING_COLS = ['Hiring Trend (6M)', 'New Hires (6M)']

# Build company-level growth aggregates (latest snapshot per company)
company_growth = df.groupby('Company').agg(
    growth_6m=('Employee Count Growth 6M %', 'first'),
    growth_1y=('Employee Count Growth 1Y %', 'first'),
    growth_2y=('Employee Count Growth 2Y %', 'first'),
    hiring_trend_6m=('Hiring Trend (6M)', 'first'),
    new_hires_6m=('New Hires (6M)', 'first'),
    avg_rating=('Rating', 'mean'),
    total_reviews=('#Reviews', 'sum'),
    global_emp=('Global Employee Count', 'first'),
    india_emp=('India Employee Count', 'first'),
    company_age=('Founded in', 'first'),
    avg_salary_lyr=('Avg Salary (L/Yr)', 'mean'),
    avg_culture=('Company Culture', 'mean'),
    avg_salary_sub=('Salary', 'mean'),
    avg_wlb=('Work-Life Balance', 'mean'),
    avg_satisfaction=('Work Satisfaction', 'mean'),
    avg_skill=('Skill Development', 'mean'),
    avg_security=('Job Security', 'mean'),
    avg_promotions=('Promotions', 'mean'),
    median_tenure=('Median current employee tenure (in years)', 'first'),
    industry_deviation=('Industry level insights (%: -100 (below industry\'s average) to 100)', 'mean'),
).reset_index()

# Merge revenue
company_growth['revenue_usd'] = company_growth['Company'].map(
    lambda c: company_demo.set_index('Company')['revenue_usd'].get(c)
)
company_growth['company_age'] = current_year - company_growth['company_age']

# Print summary stats
for col in GROWTH_COLS + HIRING_COLS:
    clean = company_growth[col].dropna()
    if len(clean) > 0:
        print(f"  {col}: n={len(clean)}, "
              f"min={clean.min():.1f}, max={clean.max():.1f}, "
              f"median={clean.median():.1f}, mean={clean.mean():.1f}")

# ── 10.75 ── Employee Growth Distribution: 6M vs 1Y vs 2Y (Overlaid KDE) ──
fig, ax = plt.subplots(figsize=(11, 6))
growth_palette = ['#e74c3c', '#f39c12', '#2ecc71']
growth_labels = ['6-Month Growth %', '1-Year Growth %', '2-Year Growth %']

for col, color, label in zip(GROWTH_COLS, growth_palette, growth_labels):
    clean = company_growth[col].dropna()
    if len(clean) > 1:
        sns.kdeplot(clean, color=color, linewidth=2.5, label=label, ax=ax, fill=True, alpha=0.12)

ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
ax.set_title('Distribution of Employee Count Growth Rates\n(6-Month, 1-Year, 2-Year Horizons)', fontsize=14, pad=15)
ax.set_xlabel('Employee Count Growth (%)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.legend(fontsize=11)

# Add median markers
for col, color, label, y_offset in zip(GROWTH_COLS, growth_palette, growth_labels, [0.85, 0.78, 0.71]):
    med = company_growth[col].median()
    if not pd.isna(med):
        ax.axvline(med, color=color, linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(med, ax.get_ylim()[1] * y_offset, f'{label.split()[0]} median: {med:+.1f}%',
                color=color, fontsize=9, fontweight='bold', rotation=90, va='top')

ax.grid(True, linestyle='--', alpha=0.3)
save_plot(plt, "75_employee_growth_distribution.png")

# ── 10.76 ── Top Companies by Employee Growth (Grouped Bar: 6M, 1Y, 2Y) ──
growth_ranked = company_growth.dropna(subset=['growth_2y']).nlargest(15, 'growth_2y').sort_values('growth_2y')

fig, ax = plt.subplots(figsize=(14, 8))
x = np.arange(len(growth_ranked))
width = 0.25
bars1 = ax.barh(x - width, growth_ranked['growth_6m'], width,
                label='6-Month Growth %', color='#e74c3c', edgecolor='white', alpha=0.85)
bars2 = ax.barh(x, growth_ranked['growth_1y'], width,
                label='1-Year Growth %', color='#f39c12', edgecolor='white', alpha=0.85)
bars3 = ax.barh(x + width, growth_ranked['growth_2y'], width,
                label='2-Year Growth %', color='#2ecc71', edgecolor='white', alpha=0.85)

ax.set_yticks(x)
ax.set_yticklabels(growth_ranked['Company'], fontsize=10)
ax.set_xlabel('Employee Count Growth (%)', fontsize=12)
ax.set_title('Top 15 Companies by Employee Headcount Growth\n(3 time horizons compared)', fontsize=14, pad=15)
ax.legend(fontsize=10, loc='lower right')
ax.axvline(0, color='black', linewidth=0.8)
ax.grid(axis='x', linestyle='--', alpha=0.3)

# Annotate 2Y growth values
for bar, (_, row) in zip(bars3, growth_ranked.iterrows()):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f'★{row["avg_rating"]:.1f}', va='center', fontsize=8, fontweight='bold', color='#2c3e50')
save_plot(plt, "76_top_companies_by_growth.png")

# ── 10.77 ── Employee Growth vs Overall Rating (Scatter, 3 horizons as small multiples) ──
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
growth_vs_rating_map = [
    ('growth_6m', '6-Month Growth %', axes[0]),
    ('growth_1y', '1-Year Growth %', axes[1]),
    ('growth_2y', '2-Year Growth %', axes[2]),
]

for col, label, ax in growth_vs_rating_map:
    plot_data = company_growth.dropna(subset=[col, 'avg_rating'])
    scatter = ax.scatter(plot_data['avg_rating'], plot_data[col],
                         s=plot_data['total_reviews'] / 10 + 50,
                         c=plot_data['company_age'].fillna(20), cmap='viridis',
                         alpha=0.8, edgecolors='#2c3e50', linewidth=0.8)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_xlabel('Average Overall Rating', fontsize=11)
    ax.set_ylabel(label, fontsize=11)
    ax.set_title(label, fontsize=13, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3)

    # Trend line
    mask = plot_data['avg_rating'].notna() & plot_data[col].notna()
    if mask.sum() > 2:
        z = np.polyfit(plot_data.loc[mask, 'avg_rating'], plot_data.loc[mask, col], 1)
        p = np.poly1d(z)
        x_line = np.linspace(plot_data['avg_rating'].min(), plot_data['avg_rating'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7)
    corr_val = plot_data['avg_rating'].corr(plot_data[col])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    # Annotate outliers
    for _, row in plot_data.iterrows():
        if abs(row[col]) > plot_data[col].std() * 1.5 or row['avg_rating'] > 4.2 or row['avg_rating'] < 2.5:
            ax.annotate(row['Company'], (row['avg_rating'], row[col]),
                        textcoords="offset points", xytext=(5, 5),
                        fontsize=6, ha='left', alpha=0.85)

# Shared colorbar
cbar = fig.colorbar(scatter, ax=axes, orientation='vertical', fraction=0.02, pad=0.04)
cbar.set_label('Company Age (years)', fontsize=11)

fig.suptitle('Employee Growth vs Overall Rating\n(size = total reviews, color = company age)\n"Are higher-rated companies growing faster?"',
             fontsize=16, y=1.03)
plt.tight_layout()
save_plot(plt, "77_growth_vs_rating_small_multiples.png")

# ── 10.78 ── Growth Acceleration/Deceleration: 6M vs 2Y (Scatter) ──
growth_compare = company_growth.dropna(subset=['growth_6m', 'growth_2y'])

fig, ax = plt.subplots(figsize=(10, 8))
# Reference line: identical growth
all_vals = pd.concat([growth_compare['growth_6m'], growth_compare['growth_2y']])
min_val, max_val = all_vals.min() - 5, all_vals.max() + 5
ax.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.3, linewidth=1, label='Equal growth')
ax.fill_between([min_val, max_val], [min_val, max_val], max_val + 20,
                alpha=0.05, color='green', label='Accelerating (2Y > 6M)')
ax.fill_between([min_val, max_val], min_val - 20, [min_val, max_val],
                alpha=0.05, color='red', label='Decelerating (6M > 2Y)')

scatter = ax.scatter(growth_compare['growth_2y'], growth_compare['growth_6m'],
                     s=growth_compare['global_emp'].fillna(1000) / 30 + 60,
                     c=growth_compare['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='#2c3e50', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)

ax.set_xlabel('2-Year Employee Growth (%)', fontsize=12)
ax.set_ylabel('6-Month Employee Growth (%)', fontsize=12)
ax.set_title('Growth Momentum: Short-Term (6M) vs Long-Term (2Y)\n(size = global employees, color = rating)\n"Who is accelerating vs. decelerating?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.3)

for _, row in growth_compare.iterrows():
    ax.annotate(row['Company'], (row['growth_2y'], row['growth_6m']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9, loc='upper left')
save_plot(plt, "78_growth_momentum_6m_vs_2y.png")

# ── 10.79 ── Hiring Trend Distribution ──
hiring_trend_clean = company_growth['hiring_trend_6m'].dropna()

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(hiring_trend_clean, bins=20, kde=True, color='#8e44ad',
             edgecolor='#6c3483', ax=ax)
ax.axvline(hiring_trend_clean.mean(), color='red', linestyle='--', linewidth=2,
           label=f'Mean: {hiring_trend_clean.mean():+.1f}%')
ax.axvline(hiring_trend_clean.median(), color='#e67e22', linestyle='--', linewidth=2,
           label=f'Median: {hiring_trend_clean.median():+.1f}%')
ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.4)
ax.set_title('Distribution of Hiring Trend (6-Month)\n% Change in New Hires: 6 Months Ago vs Last Month', fontsize=14, pad=15)
ax.set_xlabel('Hiring Trend (%)', fontsize=12)
ax.set_ylabel('Number of Companies', fontsize=12)
ax.legend(fontsize=10)
save_plot(plt, "79_hiring_trend_distribution.png")

# ── 10.80 ── Top & Bottom Companies by Hiring Trend ──
hiring_ranked = company_growth.dropna(subset=['hiring_trend_6m']).sort_values('hiring_trend_6m')
bottom_hiring = hiring_ranked.head(10)   # Most negative (declining hiring)
top_hiring = hiring_ranked.tail(10)       # Most positive (increasing hiring)
hiring_combined = pd.concat([bottom_hiring, top_hiring])

fig, ax = plt.subplots(figsize=(12, 7))
hiring_colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in hiring_combined['hiring_trend_6m']]
bars = ax.barh(hiring_combined['Company'], hiring_combined['hiring_trend_6m'],
               color=hiring_colors, edgecolor='white')
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('Hiring Trend 6M (%)', fontsize=12)
ax.set_title('Hiring Momentum: Top 10 Increasing vs Bottom 10 Declining\n(% change in new hires rate, last month vs 6 months ago)',
             fontsize=14, pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.3)
for bar, (_, row) in zip(bars, hiring_combined.iterrows()):
    direction = '▲' if row['hiring_trend_6m'] > 0 else '▼'
    ax.text(bar.get_width() + (1.5 if bar.get_width() >= 0 else -8),
            bar.get_y() + bar.get_height() / 2,
            f'{direction} {row["hiring_trend_6m"]:+.1f}%  ★{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')
save_plot(plt, "80_hiring_trend_top_bottom.png")

# ── 10.81 ── Hiring Trend vs Employee Growth (Scatter) ──
ht_growth_data = company_growth.dropna(subset=['hiring_trend_6m', 'growth_6m'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(ht_growth_data['growth_6m'], ht_growth_data['hiring_trend_6m'],
                     s=ht_growth_data['total_reviews'] / 10 + 60,
                     c=ht_growth_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
ax.axvline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
ax.set_xlabel('Employee Count Growth 6M (%)', fontsize=12)
ax.set_ylabel('Hiring Trend 6M (%)', fontsize=12)
ax.set_title('Hiring Trend vs Employee Growth\n(size = reviews, color = rating)\n"Are companies that hire more also growing headcount?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.3)

# Quadrant labels
ax.text(0.98, 0.98, 'Growing HC\n↑ Hiring [HOT]', transform=ax.transAxes,
        fontsize=9, ha='right', va='top', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.25))
ax.text(0.02, 0.98, 'Shrinking HC\n↑ Hiring', transform=ax.transAxes,
        fontsize=9, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.25))
ax.text(0.98, 0.02, 'Growing HC\n↓ Hiring', transform=ax.transAxes,
        fontsize=9, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.25))
ax.text(0.02, 0.02, 'Shrinking HC\n↓ Hiring [COLD]', transform=ax.transAxes,
        fontsize=9, ha='left', va='bottom',
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.25))

for _, row in ht_growth_data.iterrows():
    ax.annotate(row['Company'], (row['growth_6m'], row['hiring_trend_6m']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
corr_val = ht_growth_data['growth_6m'].corr(ht_growth_data['hiring_trend_6m'])
ax.text(0.5, 0.01, f'Correlation: r={corr_val:.2f}',
        transform=ax.transAxes, fontsize=10, ha='center', fontstyle='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
save_plot(plt, "81_hiring_trend_vs_growth.png")

# ── 10.82 ── New Hires (6M): Distribution + Top Companies ──
new_hires_clean = company_growth['new_hires_6m'].dropna()

fig, axes = plt.subplots(1, 2, figsize=(17, 7))

# Left: Distribution
ax = axes[0]
sns.histplot(new_hires_clean, bins=20, kde=True, color='#1abc9c',
             edgecolor='#16a085', ax=ax)
ax.axvline(new_hires_clean.median(), color='#e74c3c', linestyle='--', linewidth=2,
           label=f'Median: {new_hires_clean.median():.0f}')
ax.axvline(new_hires_clean.mean(), color='#f39c12', linestyle='--', linewidth=2,
           label=f'Mean: {new_hires_clean.mean():.0f}')
ax.set_title('Distribution of New Hires (Past 6 Months)', fontsize=13)
ax.set_xlabel('Number of New Hires', fontsize=11)
ax.set_ylabel('Number of Companies', fontsize=11)
ax.legend(fontsize=9)

# Right: Top 15 by New Hires
ax = axes[1]
top_hires = company_growth.dropna(subset=['new_hires_6m']).nlargest(15, 'new_hires_6m').sort_values('new_hires_6m')
hire_colors = plt.cm.Blues(0.3 + 0.7 * np.linspace(0, 1, len(top_hires)))
bars = ax.barh(top_hires['Company'], top_hires['new_hires_6m'],
               color=hire_colors, edgecolor='white')
ax.set_xlabel('New Hires in Past 6 Months', fontsize=11)
ax.set_title('Top 15 Companies by New Hires (6M)', fontsize=13)
ax.grid(axis='x', linestyle='--', alpha=0.3)
for bar, (_, row) in zip(bars, top_hires.iterrows()):
    ax.text(bar.get_width() + bar.get_width() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{row["new_hires_6m"]:,.0f}  ★{row["avg_rating"]:.1f}',
            va='center', fontsize=9, fontweight='bold')

fig.suptitle('New Hires Analysis (Past 6 Months)', fontsize=15, y=1.02)
plt.tight_layout()
save_plot(plt, "82_new_hires_distribution_and_top.png")

# ── 10.83 ── New Hires vs Global Employee Count (Scatter) ──
nh_emp_data = company_growth.dropna(subset=['new_hires_6m', 'global_emp'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(nh_emp_data['global_emp'], nh_emp_data['new_hires_6m'],
                     s=nh_emp_data['avg_rating'] * 50 + 30,
                     c=nh_emp_data['company_age'].fillna(20), cmap='plasma',
                     alpha=0.8, edgecolors='white', linewidth=1)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Company Age (years)', fontsize=11)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Employee Count (log scale)', fontsize=12)
ax.set_ylabel('New Hires in Past 6 Months (log scale)', fontsize=12)
ax.set_title('New Hires vs Company Size\n(size = rating, color = company age)\n"Hiring volume vs headcount base"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.3)

# Trend line
mask = nh_emp_data['global_emp'].notna() & nh_emp_data['new_hires_6m'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(nh_emp_data.loc[mask, 'global_emp']),
                   np.log10(nh_emp_data.loc[mask, 'new_hires_6m']), 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(nh_emp_data['global_emp'].min()),
                         np.log10(nh_emp_data['global_emp'].max()), 100)
    ax.plot(10 ** x_line, 10 ** p(x_line), 'r--', linewidth=1.5, alpha=0.7,
            label=f'Slope: {z[0]:.2f}')

# Hiring-rate reference lines
emp_range_line = np.logspace(np.log10(nh_emp_data['global_emp'].min()),
                              np.log10(nh_emp_data['global_emp'].max()), 100)
for rate_pct, label, ls, col in [
    (0.50, '50% hiring rate', ':', '#95a5a6'),
    (0.20, '20% hiring rate', '--', '#7f8c8d'),
    (0.05, '5% hiring rate', '-.', '#555'),
]:
    ax.plot(emp_range_line, rate_pct * emp_range_line, ls, color=col,
            alpha=0.4, linewidth=1, label=label)

for _, row in nh_emp_data.iterrows():
    if row['new_hires_6m'] > 0:
        ax.annotate(row['Company'], (row['global_emp'], row['new_hires_6m']),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=6, ha='left')

ax.legend(fontsize=8, title='Hiring Rate = New Hires / Total Emp', title_fontsize=9,
          loc='lower right')
save_plot(plt, "83_new_hires_vs_company_size.png")

# ── 10.84 ── Growth + Hiring Dashboard Heatmap (Top 20 by 2Y Growth) ──
dashboard_cols = [
    'growth_6m', 'growth_1y', 'growth_2y',
    'hiring_trend_6m', 'new_hires_6m',
    'avg_rating', 'company_age', 'global_emp',
]
dashboard_labels = [
    'Growth 6M%', 'Growth 1Y%', 'Growth 2Y%',
    'Hiring Trend%', 'New Hires',
    'Rating', 'Age (yrs)', 'Global Emp',
]

top20_growth = company_growth.dropna(subset=['growth_2y']).nlargest(20, 'growth_2y').set_index('Company')
dashboard_raw = top20_growth[dashboard_cols].copy()
dashboard_raw.columns = dashboard_labels

# Normalize columns to 0-1 for colormap
dashboard_norm = (dashboard_raw - dashboard_raw.min()) / \
                 (dashboard_raw.max() - dashboard_raw.min() + 1e-10)

fig, ax = plt.subplots(figsize=(16, 10))
sns.heatmap(dashboard_norm, annot=dashboard_raw.round(1), fmt='.1f',
            cmap='RdYlGn', ax=ax, linewidths=1, linecolor='white',
            annot_kws={'fontsize': 8}, center=0.5,
            cbar_kws={'label': 'Normalized Score (0–1)'})
ax.set_title('Growth & Hiring Dashboard: Top 20 Companies by 2-Year Employee Growth\n(Green = high/better, Red = low/worse for each metric)',
             fontsize=14, pad=18)
ax.set_xlabel('')
ax.set_ylabel('')
ax.tick_params(axis='both', labelsize=9)
save_plot(plt, "84_growth_hiring_dashboard_heatmap.png")

# ── 10.85 ── Employee Growth vs Company Age (Small Multiples) ──
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
growth_age_map = [
    ('growth_6m', '6-Month Growth %', axes[0]),
    ('growth_1y', '1-Year Growth %', axes[1]),
    ('growth_2y', '2-Year Growth %', axes[2]),
]

for col, label, ax in growth_age_map:
    plot_data = company_growth.dropna(subset=[col, 'company_age'])
    scatter = ax.scatter(plot_data['company_age'], plot_data[col],
                         s=plot_data['global_emp'].fillna(1000) / 30 + 50,
                         c=plot_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_xlabel('Company Age (years)', fontsize=11)
    ax.set_ylabel(label, fontsize=11)
    ax.set_title(label, fontsize=13, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3)

    # Trend line
    mask = plot_data['company_age'].notna() & plot_data[col].notna()
    if mask.sum() > 2:
        z = np.polyfit(plot_data.loc[mask, 'company_age'], plot_data.loc[mask, col], 1)
        p = np.poly1d(z)
        x_line = np.linspace(plot_data['company_age'].min(), plot_data['company_age'].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7)
    corr_val = plot_data['company_age'].corr(plot_data[col])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    for _, row in plot_data.iterrows():
        if abs(row[col]) > plot_data[col].std() * 1.5:
            ax.annotate(row['Company'], (row['company_age'], row[col]),
                        textcoords="offset points", xytext=(5, 5),
                        fontsize=6, ha='left', alpha=0.85)

cbar = fig.colorbar(scatter, ax=axes, orientation='vertical', fraction=0.02, pad=0.04)
cbar.set_label('Average Rating', fontsize=11)

fig.suptitle('Employee Growth vs Company Age\n(size = global employees, color = rating)\n"Are younger companies growing faster?"',
             fontsize=16, y=1.03)
plt.tight_layout()
save_plot(plt, "85_growth_vs_company_age.png")

# ── 10.86 ── Employee Growth vs Revenue (Scatter, 2Y Growth) ──
growth_rev_data = company_growth.dropna(subset=['growth_2y', 'revenue_usd'])

fig, ax = plt.subplots(figsize=(12, 7))
scatter = ax.scatter(growth_rev_data['revenue_usd'], growth_rev_data['growth_2y'],
                     s=growth_rev_data['global_emp'].fillna(1000) / 30 + 80,
                     c=growth_rev_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='#2c3e50', linewidth=1.2, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.set_xscale('log')
ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
ax.set_xlabel('Annual Revenue (USD, log scale)', fontsize=12)
ax.set_ylabel('2-Year Employee Growth (%)', fontsize=12)
ax.set_title('Employee Growth vs Company Revenue\n(size = global employees, color = rating)\n"Big revenue = big growth, or the opposite?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.3)

mask = growth_rev_data['revenue_usd'].notna() & growth_rev_data['growth_2y'].notna()
if mask.sum() > 2:
    z = np.polyfit(np.log10(growth_rev_data.loc[mask, 'revenue_usd']),
                   growth_rev_data.loc[mask, 'growth_2y'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(np.log10(growth_rev_data['revenue_usd'].min()),
                         np.log10(growth_rev_data['revenue_usd'].max()), 100)
    ax.plot(10 ** x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in growth_rev_data.iterrows():
    ax.annotate(row['Company'], (row['revenue_usd'], row['growth_2y']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "86_growth_vs_revenue.png")

# ── 10.87 ── Employee Growth vs Sub-Ratings (Small Multiples, 2Y Growth) ──
growth_sub_map = {
    'avg_culture': 'Culture',
    'avg_salary_sub': 'Salary',
    'avg_wlb': 'Work-Life Balance',
    'avg_satisfaction': 'Work Satisfaction',
    'avg_skill': 'Skill Development',
    'avg_security': 'Job Security',
    'avg_promotions': 'Promotions',
}

fig, axes = plt.subplots(3, 3, figsize=(18, 16))
axes = axes.flatten()

for i, (col, label) in enumerate(growth_sub_map.items()):
    ax = axes[i]
    sub_clean = company_growth.dropna(subset=['growth_2y', col])
    scatter = ax.scatter(sub_clean[col], sub_clean['growth_2y'],
                         s=sub_clean['total_reviews'] / 15 + 50,
                         c=sub_clean['avg_rating'], cmap='RdYlGn', alpha=0.8,
                         edgecolors='#2c3e50', linewidth=0.8, vmin=2, vmax=5)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_xlabel(f'{label} Rating', fontsize=10)
    ax.set_ylabel('2Y Growth %', fontsize=10)
    ax.set_title(f'{label}', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xlim(sub_clean[col].min() - 0.3, sub_clean[col].max() + 0.4)

    # Regression
    mask = sub_clean[col].notna() & sub_clean['growth_2y'].notna()
    if mask.sum() > 2:
        z = np.polyfit(sub_clean.loc[mask, col], sub_clean.loc[mask, 'growth_2y'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sub_clean[col].min(), sub_clean[col].max(), 100)
        ax.plot(x_line, p(x_line), 'r--', linewidth=1.2, alpha=0.6)
    corr_val = sub_clean[col].corr(sub_clean['growth_2y'])
    ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    for _, row in sub_clean.iterrows():
        ax.annotate(row['Company'], (row[col], row['growth_2y']),
                    textcoords="offset points", xytext=(4, 3),
                    fontsize=6, ha='left', alpha=0.85)

for j in range(len(growth_sub_map), len(axes)):
    axes[j].set_visible(False)

fig.suptitle('2-Year Employee Growth vs Sub-Ratings\n(color = overall rating, size = total reviews)',
             fontsize=16, y=1.01)
plt.tight_layout()
save_plot(plt, "87_growth_vs_sub_ratings.png")

# ── 10.88 ── New Hires per Employee (Hiring Intensity) vs Rating ──
company_growth['hires_per_emp'] = (
    company_growth['new_hires_6m'] / company_growth['global_emp']
)
# Filter out extremes
hires_intensity = company_growth.dropna(subset=['hires_per_emp', 'avg_rating'])
hires_intensity = hires_intensity[hires_intensity['hires_per_emp'] < 5]  # Cap unrealistic ratios

hires_intensity['hires_rate_pct'] = hires_intensity['hires_per_emp'] * 100

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(hires_intensity['avg_rating'], hires_intensity['hires_rate_pct'],
                     s=hires_intensity['global_emp'].fillna(1000) / 30 + 60,
                     c=hires_intensity['growth_2y'], cmap='coolwarm', alpha=0.8,
                     edgecolors='#2c3e50', linewidth=1, vmin=-50, vmax=200)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('2-Year Growth %', fontsize=11)
ax.set_xlabel('Average Overall Rating', fontsize=12)
ax.set_ylabel('Hiring Rate: New Hires / Total Employees (%)', fontsize=12)
ax.set_title('Hiring Intensity vs Rating\n(size = global employees, color = 2Y growth)\n"Are high-growth companies hiring more aggressively?"',
             fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.3)

for _, row in hires_intensity.iterrows():
    ax.annotate(row['Company'], (row['avg_rating'], row['hires_rate_pct']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')

corr_val = hires_intensity['avg_rating'].corr(hires_intensity['hires_rate_pct'])
ax.text(0.95, 0.05, f'r={corr_val:.2f}', transform=ax.transAxes,
        fontsize=10, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
save_plot(plt, "88_hiring_intensity_vs_rating.png")

# ── 10.89 ── Growth Metrics Correlation Heatmap ──
growth_corr_cols = [
    'growth_6m', 'growth_1y', 'growth_2y',
    'hiring_trend_6m', 'new_hires_6m',
    'avg_rating', 'total_reviews', 'company_age',
    'global_emp', 'india_emp',
    'avg_culture', 'avg_salary_sub', 'avg_wlb',
    'avg_satisfaction', 'avg_skill', 'avg_security', 'avg_promotions',
    'median_tenure', 'avg_salary_lyr',
]
growth_corr_labels = [
    'Growth 6M%', 'Growth 1Y%', 'Growth 2Y%',
    'Hiring Trend%', 'New Hires',
    'Rating', 'Reviews', 'Age (yrs)',
    'Global Emp', 'India Emp',
    'Culture', 'Salary*', 'WLB',
    'Satisfaction', 'Skill', 'Security', 'Promotions',
    'Tenure (yrs)', 'Salary (L/Yr)',
]

growth_corr_df = company_growth[growth_corr_cols].copy()
# Log-transform scale variables
for col in ['global_emp', 'india_emp', 'total_reviews', 'new_hires_6m']:
    growth_corr_df[col] = np.log10(growth_corr_df[col].replace(0, np.nan))
growth_corr_df.columns = growth_corr_labels
growth_corr = growth_corr_df.corr()

fig, ax = plt.subplots(figsize=(18, 15))
mask = np.triu(np.ones_like(growth_corr, dtype=bool), k=1)
sns.heatmap(growth_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, ax=ax, mask=mask, vmin=-1, vmax=1,
            annot_kws={'fontsize': 7}, linewidths=0.5,
            cbar_kws={'label': 'Pearson r (log₁₀ for scale vars)'})
ax.set_title('Growth & Hiring: Comprehensive Correlation Matrix\n(First 5 rows/cols = growth metrics; log₁₀ for scale variables)',
             fontsize=15, pad=20)
ax.tick_params(axis='both', labelsize=9)
save_plot(plt, "89_growth_correlation_heatmap.png")

# ── 10.90 ── Growth by Revenue Tier (Box Plot, 2Y Growth) ──
growth_rev_tier = company_growth.dropna(subset=['growth_2y', 'revenue_usd']).copy()
growth_rev_tier['revenue_tier'] = pd.cut(
    growth_rev_tier['revenue_usd'],
    bins=[0, 1e9, 10e9, 50e9, 200e9, np.inf],
    labels=['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B'],
    right=False,
)

fig, ax = plt.subplots(figsize=(12, 7))
tier_order = ['<$1B', '$1B–$10B', '$10B–$50B', '$50B–$200B', '>$200B']
tier_palette_growth = sns.color_palette("RdYlGn", len(tier_order))
sns.boxplot(data=growth_rev_tier, x='revenue_tier', y='growth_2y',
            hue='revenue_tier', palette=tier_palette_growth, legend=False,
            order=tier_order, ax=ax)
sns.stripplot(data=growth_rev_tier, x='revenue_tier', y='growth_2y',
              color='black', alpha=0.3, size=5, jitter=True, ax=ax)
# Annotate company names
for _, row in growth_rev_tier.iterrows():
    tier_idx = tier_order.index(row['revenue_tier']) if row['revenue_tier'] in tier_order else -1
    if tier_idx >= 0:
        ax.annotate(row['Company'], (tier_idx, row['growth_2y']),
                    textcoords="offset points", xytext=(0, 8),
                    fontsize=6, ha='center', alpha=0.7)

ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
ax.set_title('2-Year Employee Growth by Revenue Tier\n"Which tier is expanding fastest?"', fontsize=14, pad=15)
ax.set_xlabel('Revenue Tier', fontsize=12)
ax.set_ylabel('2-Year Employee Growth (%)', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.3)
save_plot(plt, "90_growth_by_revenue_tier.png")

# ── 10.91 ── Growth vs India Workforce % ──
growth_india_data = company_growth.dropna(subset=['growth_2y'])
growth_india_data['india_pct'] = growth_india_data['india_emp'] / growth_india_data['global_emp'] * 100
growth_india_data = growth_india_data.dropna(subset=['india_pct'])

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(growth_india_data['india_pct'], growth_india_data['growth_2y'],
                     s=growth_india_data['total_reviews'] / 10 + 60,
                     c=growth_india_data['avg_rating'], cmap='RdYlGn', alpha=0.8,
                     edgecolors='white', linewidth=1, vmin=2, vmax=5)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Rating', fontsize=11)
ax.axhline(0, color='gray', linestyle='--', alpha=0.4, linewidth=1)
ax.axvline(50, color='#7f8c8d', linestyle='--', alpha=0.5, label='50% India workforce')
ax.set_xlabel('India Workforce as % of Global', fontsize=12)
ax.set_ylabel('2-Year Employee Growth (%)', fontsize=12)
ax.set_title('Employee Growth vs India Workforce Concentration\n(size = reviews, color = rating)', fontsize=14, pad=15)
ax.grid(True, linestyle='--', alpha=0.3)

mask = growth_india_data['india_pct'].notna() & growth_india_data['growth_2y'].notna()
if mask.sum() > 2:
    z = np.polyfit(growth_india_data.loc[mask, 'india_pct'],
                   growth_india_data.loc[mask, 'growth_2y'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(growth_india_data['india_pct'].min(),
                         growth_india_data['india_pct'].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=1.5, alpha=0.7, label='Trend')

for _, row in growth_india_data.iterrows():
    ax.annotate(row['Company'], (row['india_pct'], row['growth_2y']),
                textcoords="offset points", xytext=(5, 5),
                fontsize=7, ha='left')
ax.legend(fontsize=9)
save_plot(plt, "91_growth_vs_india_pct.png")

print(f"\nEmployee Growth & Hiring Trends section plots saved (75–91).")
print(f"  ✓ Section 10 complete — 17 plots saved.")

# ═══════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════
_total_elapsed = _time.time() - _script_start
print(f"\n{'='*70}")
print(f"  ✅ ALL DONE — 91 plots generated in {_total_elapsed:.1f}s")
print(f"  📁 Output directory: {OUTPUT_DIR}")
print(f"{'='*70}")
print("Done.")