import pandas as pd

# Sample dataset (replace with your actual dataset)
df = pd.read_csv("sector_holdings.csv")

# Step 1: Manual Industry Mapping (for known tickers)
manual_industry_mapping = {
    'CBI': 'Industrials',
    'DTV1': 'Communication Services',
    'DISH': 'Communication Services',
    'KRFT': 'Consumer Defensive',
    'MEG1': 'Communication Services',
    'PCP': 'Industrials',
    'STRZA': 'Communication Services',
    'USG': 'Basic Materials',
    'VIAB': 'Communication Services',
    'WBC': 'Industrials',
    'ESRX': 'Healthcare',
    'TFCFA': 'Communication Services',
    'LSXMA': 'Communication Services',
    'LSXMK': 'Communication Services',
    'MON2': 'Basic Materials',
    'STOR': 'Real Estate',
    'RHT': 'Technology',
    'SPY': 'Financial Services',
    'VOO': 'Financial Services',
    'ATVI': 'Communication Services',
    'LEN.B': 'Consumer Cyclical',
    'HEI.A': 'Industrials'
}

# Step 3: Map industries to dataset
for ticker, industry in manual_industry_mapping.items():
    df.loc[df['ticker'] == ticker, 'industry'] = industry

# Step 4: Get unique industries
unique_industries = set(df['industry'])
print("\nUnique Industries Found:\n", unique_industries)

# Step 5: Show tickers with "Unknown" industry
unknown_tickers = df[df['industry'] == 'Unknown']['ticker'].unique()
print("\nTickers with Unknown Industry:\n", unknown_tickers)

print(len(set(df['ticker'])))

print(len(set(df['industry'])))

# Check for missing values in the entire DataFrame
missing_values = df.isnull().sum()

# Print the result
print("Missing values per column:")
print(missing_values)



df.to_csv("sector_holdings2.csv", index=False)