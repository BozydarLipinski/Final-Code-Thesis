import pandas as pd

# Load your data
df = pd.read_csv('old_data.csv')

# Clean CIK column - strip whitespace and convert to string
df['cik'] = df['cik'].astype(str).str.strip()

# Rename for consistency
df = df.rename(columns={
    'valuation': 'value',
    'shares': 'no_shares'
})

# Convert 'value' to numeric and scale
df['value'] = pd.to_numeric(df['value'], errors='coerce') * 1000

# Manual mappings (with stripped strings)
manual_mappings = {
    '50485': 'IR',     # Ingersoll Rand
    '22301': 'CMCSA',  # Comcast Corporation
    '1020882': 'IRM',  # Iron Mountain
    '315066': 'FNF',   # Fidelity
    '31277': 'ETN',    # Eaton Corporation
    '311314': 'HCA',   # HCA Healthcare
    '30371': 'DUK'
}


# Apply mapping - convert both sides to strings without leading zeros
still_missing_mask = df['ticker'].isna()
df.loc[still_missing_mask, 'ticker'] = (
    df.loc[still_missing_mask, 'cik']
    .str.replace('^0+', '', regex=True)  # Remove all leading zeros
    .map(manual_mappings)
)

# Verify
remaining = df[df['ticker'].isna()]['cik'].unique()
if len(remaining) > 0:
    print(f"\nStill missing {len(remaining)} tickers. Please verify these CIKs:")
    for cik in remaining:
        print(f"CIK: '{cik}' (length: {len(cik)})")
else:
    print("\nSUCCESS! All tickers mapped successfully")

# Group and aggregate
df = df.groupby(["filedFor", "cik", "ticker"], as_index=False).agg({
    "no_shares": "sum",
    "value": "sum"
})

df.to_csv("old_data_V1.csv", index=False)
print("\nSaved to old_data_V1.csv")