import json
import os
import pandas as pd

# Paths
excel_path = "/home/jain/Desktop/ws/public/company_and_job_market_research/ratings_and_reviews_at_ambitionbox.xlsx"
out_dir = "/home/jain/Desktop/ws/public/company_and_job_market_research/data engineering/3_linkedin metrics extraction using js and python/out"
out_path = os.path.join(out_dir, "linkedin_urls.json")

# Read the Excel file
df = pd.read_excel(excel_path)

print(df.columns)

# Extract unique non-null values from "LinkedIn URL" column
unique_urls = df["LinkedIn URL"].dropna().unique().tolist()

# Ensure output directory exists
os.makedirs(out_dir, exist_ok=True)

# Dump to JSON
with open(out_path, "w") as f:
    json.dump(unique_urls, f, indent=2)

print(f"Saved {len(unique_urls)} unique LinkedIn URLs to {out_path}")
