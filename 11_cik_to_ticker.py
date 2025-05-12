import pandas as pd
from tqdm import tqdm
from sec_api import MappingApi
import time

# Initialize SEC API
mappingApi = MappingApi(api_key='d01020bfed5b65c71c80346970c851dc31249dc5bc1c953f61821054ad5e3b2c')

# Load your data
df = pd.read_csv('all_data.csv')
df['cik'] = df['cik'].astype(str).str.zfill(10)  # Ensure 10-digit CIK format

# Ticker lookup function
def get_ticker(cik):
    try:
        clean_cik = cik.lstrip('0')
        result = mappingApi.resolve('cik', clean_cik)
        return result[0]['ticker'] if result and len(result) > 0 else None
    except Exception as e:
        print(f"Error looking up CIK {cik}: {str(e)}")
        return None

# Identify only CIKs with missing tickers
missing_mask = df['ticker'].isna()
missing_ciks = df.loc[missing_mask, 'cik'].unique()
print(f"Found {len(missing_ciks)} CIKs with missing tickers")

# Create ticker mapping only for missing CIKs
print("Fetching missing tickers from SEC API...")
ticker_map = {}
for cik in tqdm(missing_ciks):
    ticker_map[cik] = get_ticker(cik)
    time.sleep(0.2)  # Rate limiting

# Apply ticker mapping only to missing values
df.loc[missing_mask, 'ticker'] = df.loc[missing_mask, 'cik'].map(ticker_map)

# Results summary
filled = missing_mask.sum() - df['ticker'].isna().sum()
print(f"\nFilled {filled} missing tickers")
print(f"Remaining missing: {df['ticker'].isna().sum()}")



# Save result
df.to_csv("old_data.csv", index=False)
print("Saved to old_data.csv")