import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

import os

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Create timestamped directory for saving plots
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"img_{timestamp}"
os.makedirs(output_dir, exist_ok=True)
print(f"Plots will be saved to directory: {output_dir}")

# -------------------------------
# 1. Load the Excel file
# -------------------------------
file_path = "20260611 - ratings_and_reviews_at_naukri_and_ambitionbox.xlsx"
try:
    df = pd.read_excel(file_path, sheet_name="ratings_and_reviews_at_naukri_a")
    print("Data loaded successfully. Shape:", df.shape)
    # Rename the long column to match what is expected in the script
    long_col = "Industry level insights (Percentage: -100 (below industry's average) to 100)"
    if long_col in df.columns:
        df = df.rename(columns={long_col: 'Industry level insights'})
except FileNotFoundError:
    print(f"File not found at {file_path}. Please update the path and try again.")
    exit()

# -------------------------------
# 2. Data Cleaning & Preparation
# -------------------------------

# Convert Date column to datetime (handles multiple formats)
def parse_custom_date(date_str):
    if pd.isna(date_str):
        return np.nan
    # Replace slashes and spaces
    date_str = str(date_str).replace('/', ' ').replace(',', ' ')
    # Try common formats
    for fmt in ["%b %d %Y", "%d %b %Y", "%b %d %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return np.nan

df['Date'] = df['Date'].astype(str).apply(parse_custom_date)

# Convert numeric columns
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['#Reviews'] = pd.to_numeric(df['#Reviews'], errors='coerce')
df['Industry level insights'] = pd.to_numeric(df['Industry level insights'], errors='coerce')

# Drop rows where Rating is missing (essential for analysis)
df = df.dropna(subset=['Rating'])
print(f"After dropping rows with missing Rating: {df.shape[0]} companies")

# Fill missing industry with 'Unknown'
df['Company Industry'] = df['Company Industry'].fillna('Unknown')

# -------------------------------
# 3. Basic Descriptive Statistics
# -------------------------------
print("\n--- Basic Statistics ---")
print(df[['Rating', '#Reviews', 'Industry level insights']].describe())

# -------------------------------
# 4. Visualizations
# -------------------------------

# 4.1 Bar Chart: Company Ratings (sorted descending)
plt.figure()
df_sorted = df.sort_values('Rating', ascending=False)
sns.barplot(data=df_sorted, x='Company', y='Rating', palette='viridis')
plt.title('Company Ratings (from AmbitionBox)', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Rating (out of 5)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'company_ratings.png'))
plt.show()

# 4.2 Scatter Plot: Rating vs Number of Reviews (log scale on y-axis)
plt.figure()
# Use log scale for #Reviews because values vary widely
plt.scatter(df['Rating'], df['#Reviews'], s=100, alpha=0.7, c='steelblue')
plt.yscale('log')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews (log scale)')
plt.title('Rating vs. Number of Reviews')
# Add company labels for points with many reviews or extreme ratings
for _, row in df.iterrows():
    if row['#Reviews'] > 10000 or row['Rating'] > 4.0 or row['Rating'] < 3.0:
        plt.annotate(row['Company'], (row['Rating'], row['#Reviews']),
                     xytext=(5, 5), textcoords='offset points', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'rating_vs_reviews.png'))
plt.show()

# 4.3 Histogram of Rating Distribution
plt.figure()
sns.histplot(df['Rating'], bins=10, kde=True, color='darkorange')
plt.xlabel('Rating')
plt.ylabel('Frequency')
plt.title('Distribution of Company Ratings')
plt.axvline(df['Rating'].mean(), color='red', linestyle='--', label=f"Mean: {df['Rating'].mean():.2f}")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'rating_distribution.png'))
plt.show()

# 4.4 Bar Chart: Industry Level Insights (deviation from industry average)
plt.figure()
# Sort by insights value
df_insights = df.dropna(subset=['Industry level insights']).sort_values('Industry level insights', ascending=False)
if not df_insights.empty:
    colors = ['green' if x > 0 else 'red' for x in df_insights['Industry level insights']]
    sns.barplot(data=df_insights, x='Company', y='Industry level insights', palette=colors)
    plt.title('Industry Level Insights\n(Positive = above industry average, Negative = below)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Percentage deviation from industry average')
    plt.axhline(0, color='black', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'industry_level_insights.png'))
    plt.show()
else:
    print("No valid 'Industry level insights' data available for plotting.")

# 4.5 Boxplot: Ratings by Industry (only industries with at least 2 companies)
plt.figure()
industries = df['Company Industry'].value_counts()
industries_to_plot = industries[industries >= 2].index
if len(industries_to_plot) > 0:
    df_box = df[df['Company Industry'].isin(industries_to_plot)]
    sns.boxplot(data=df_box, x='Company Industry', y='Rating', palette='Set2')
    plt.title('Rating Distribution by Industry')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ratings_by_industry.png'))
    plt.show()
else:
    print("Not enough companies per industry for boxplot (need at least 2).")

# 4.6 Additional: Top 5 and Bottom 5 Companies by Rating
print("\n--- Top 5 Companies by Rating ---")
print(df.nlargest(5, 'Rating')[['Company', 'Rating', '#Reviews', 'Company Industry']])
print("\n--- Bottom 5 Companies by Rating ---")
print(df.nsmallest(5, 'Rating')[['Company', 'Rating', '#Reviews', 'Company Industry']])

# 4.7 Correlation matrix (numerical columns)
plt.figure()
numeric_cols = ['Rating', '#Reviews', 'Industry level insights']
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'correlation_matrix.png'))
plt.show()
