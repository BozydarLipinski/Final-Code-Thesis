import pandas as pd

df = pd.read_csv("old_sector_holdings.csv")

# Step 4: Get unique industries
unique_industries = set(df['industry'])
print("\nUnique Industries Found:\n", unique_industries)

# Step 5: Show tickers with "Unknown" industry
unknown_tickers = df[df['industry'] == 'Unknown']['ticker'].unique()
print("\nTickers with Unknown Industry:\n", unknown_tickers)

print(len(set(df['ticker'])))

print(len(set(df['industry'])))