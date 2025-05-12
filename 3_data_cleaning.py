import pandas as pd

# Load the dataset (replace 'your_file.csv' with actual filename)
df1 = pd.read_csv("berkshire_hathaway_portfolio_filings.csv")

df2 = pd.read_csv("berkshire_hathaway_portfolio_filings2.csv")

# Append the new data to the main dataset
df_combined = pd.concat([df1, df2], ignore_index=True)

# Sort the data chronologically
df_combined = df_combined.sort_values(by="filedFor")

# Save the final dataset
df_combined.to_csv("merged_holdings.csv", index=False)


# Group by period (filedFor), company name (nameOfIssuer), and ticker
df_cleaned = df_combined.groupby(["filedFor", "ticker"], as_index=False).agg({
    "value": "sum"
})

# Save the cleaned file (optional)
df_cleaned.to_csv("cleaned_holdings.csv", index=False)

print("Data cleaned and aggregated successfully!")