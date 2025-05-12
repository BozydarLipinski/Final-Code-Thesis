import pandas as pd

# Sample dataset (replace with your actual dataset)
df = pd.read_csv("old_sector_holdings.csv")

# Step 1: Manual Industry Mapping (for known tickers)
manual_industry_mapping = {
    'SJR/BEUR': 'Communication Services',
    'SEE 2 04/01/18 A': 'Consumer Cyclical',
    'DUT': 'Financial Services',
    'PC6A': 'Energy',
    'LXKEUR': 'Technology',
    'A4S': 'Financial Services',
    'DYH': 'Consumer Defensive',
    'W3U': 'Financial Services',
    'WBC1EUR': 'Financial Services',
    'NRA': 'Utilities',
    'TRL': 'Healthcare',
    'VIAB': 'Communication Services',
    'ADT2': 'Industrials',
    'BUD1': 'Consumer Defensive',
    'CDCO': 'Industrials',
    'DFODQ': 'Consumer Defensive',
    'DJ': 'Communication Services',
    'DNB1': 'Industrials',
    'DTV1': 'Communication Services',
    'EDGW': 'Consumer Cyclical',
    'G1': 'Consumer Defensive',
    'GLK1': 'Industrials',
    'JNY': 'Consumer Cyclical',
    'LVLT': 'Technology',
    'NLC': 'Industrials',
    'OSI2': 'Consumer Cyclical',
    'STI1': 'Financial Services',
    'STRZA': 'Communication Services',
    'SVM1': 'Consumer Cyclical',
    'TT2': 'Industrials',
    'USG1': 'Basic Materials',
    'WHCI': 'Industrials',
    'WSC1': 'Financial Services',
    'WTEL': 'Communication Services',
    'ZNT': 'Financial Services',
    'KRFT': 'Consumer Defensive',
    'MEG1': 'Communication Services',
    'PCP': 'Industrials',
    'KATE': 'Consumer Cyclical',
    'CDSCY': 'Consumer Defensive',
    'CEG1': 'Utilities',
    'CBI': 'Basic Materials'
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

df.to_csv("old_sector_holdings2.csv", index=False)