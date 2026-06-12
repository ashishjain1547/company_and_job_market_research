# ROLE

Expert Data Analyst doing data visualization and dashboarding today

# TASK

Write Python code for plotting charts with incites drawn from some company reviews

# DATA DESCRIPTION

File format: .xlsx
Path: /home/jain/Desktop/ws/public/company_and_job_market_research/ratings_and_reviews_at_ambitionbox.xlsx

**Columns:**

- Date: 
    - Format: Jan / 16 / 2026
- Company: 
    - Example values: Amazon, Google, Genpact, TECHPINNACLE BIT SOLUTIONS, Lumen Technologies
- Rating:
    - Range: 0 to 5
- #Reviews:
    - Count of reviews
- Industry level insights (%: -100 (below industry's average) to 100)
    - Percentage of whether current row's company is above or below industry average and by what %

# SOME CHART / PLOT EXAMPLES

- BAR CHART: "Company Ratings": X-Axis -- Company and Y-Axis: Rating (out of 5)
- BAR CHART: "Industry Level Insights": X-Axis -- Company and Y-Axis: % Deviation
- DISTRUBUTION PLOT: "Distribution of Company Ratings": X-Axis -- Rating and Y-Axis -- Frequency
- SCATTER PLOT: "Rating vs Number of Reviews": X-Axis -- Rating and Y-Axis -- Number of Reviews (log scale)

**IMPORTANTLY: YOU HAVE TO ADD TO IT. MORE PLOTS. MORE CHARTS.**

# WHERE TO SAVE THE PLOTS

- In Python code: write the generated plots to disc to a folder: img_<timestamp> in: 
"/home/jain/Desktop/ws/public/company_and_job_market_research/analytics/imgs"

