import pandas as pd
import yfinance as yf


# Sample dataset with tickers
df = pd.read_csv("old_data_V1.csv")

# Step 1: Extract unique tickers
unique_tickers = df['ticker'].unique()

# Step 2: Fetch industry information using yfinance
industry_mapping = {}
for ticker in unique_tickers:
    try:
        stock = yf.Ticker(ticker)
        industry_mapping[ticker] = stock.info.get('sector', 'Unknown')  # Default to 'Unknown' if not found
    except Exception as e:
        print(f"Error fetching industry for {ticker}: {e}")
        industry_mapping[ticker] = 'Unknown'

# Step 3: Map industries efficiently
df['industry'] = df['ticker'].map(industry_mapping)


# Save the cleaned file (optional)
df.to_csv("old_sector_holdings.csv", index=False)

print(df)