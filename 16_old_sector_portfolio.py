import pandas as pd
import yfinance as yf
from datetime import timedelta

# Load data
df = pd.read_csv("old_sector_holdings2.csv")

# Ensure 'filedFor' is datetime
df['filedFor'] = pd.to_datetime(df['filedFor'], errors='coerce')

# Sector ticker mapping (using correct symbols)
sector_tickers = {
    'Technology': '^SP500-45',
    'Basic Materials': '^SP500-15',
    'Energy': '^GSPE',
    'Utilities': '^SP500-55',
    'Communication Services': '^SP500-50',
    'Industrials': '^SP500-20',
    'Healthcare': '^SP500-35',
    'Consumer Defensive': '^SP500-30',
    'Consumer Cyclical': '^SP500-25',
    'Real Estate': '^SP500-60',
    'Financial Services': '^SP500-40'
}


def validate_sector_name(sector):
    """Validate sector name against known mappings"""
    return sector in sector_tickers


def get_sector_price_index(row):
    """
    Fetch price index data for a specific sector on a given date

    Args:
        row (Series): DataFrame row containing 'industry' and 'filedFor'

    Returns:
        float: Price value if successful, None otherwise
    """
    sector = row['industry']

    # Validate inputs
    if not validate_sector_name(sector):
        print(f"Warning: Unknown sector '{sector}'")
        return None

    if pd.isna(row['filedFor']):
        print(f"Warning: Invalid date for sector '{sector}'")
        return None

    ticker = sector_tickers[sector]

    try:
        filed_date = pd.to_datetime(row['filedFor'])
        start = (filed_date - timedelta(days=3)).strftime('%Y-%m-%d')
        end = (filed_date + timedelta(days=3)).strftime('%Y-%m-%d')

        data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)

        if data.empty:
            print(f"Warning: No price data found for {sector} ({ticker}) around {filed_date}")
            return None

        index_pos = data.index.get_indexer([filed_date], method='nearest')[0]
        closest = data.index[index_pos]

        # Return single scalar value
        return float(data.loc[closest, 'Close'])

    except Exception as e:
        print(f"Error fetching {sector} ({ticker}) index on {filed_date}: {str(e)}")
        return None


# Step 1: Aggregate portfolio values
sector_value = df.groupby(['filedFor', 'industry']).agg(
    total_value=('value', 'sum')
).reset_index()

total_portfolio_value = df.groupby('filedFor').agg(
    portfolio_value=('value', 'sum')
).reset_index()

sector_value = sector_value.merge(total_portfolio_value, on='filedFor')
sector_value['sector_percentage'] = (sector_value['total_value'] / sector_value['portfolio_value']) * 100

# Step 2: Add price index column (using vectorized operation)
sector_value['sector_price_index'] = sector_value.apply(get_sector_price_index, axis=1)

# Step 3: Add year_quarter
sector_value['year_quarter'] = sector_value['filedFor'].dt.to_period('Q')

# Save and preview
sector_value.to_csv("final_old_sector_portfolio.csv", index=False)
print(sector_value.head())