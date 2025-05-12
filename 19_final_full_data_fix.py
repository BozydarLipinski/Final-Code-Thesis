import pandas as pd
import yfinance as yf
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PriceFetcher:
    def __init__(self):
        self.cache = {}  # Cache prices to reduce API calls

        # Original sector ticker mappings
        self.sector_tickers = {
            'Technology': '^SP500-45',
            'Real Estate': '^SP500-60',
            'Financial Services': '^SP500-40',
            'Healthcare': '^SP500-35',
            'Consumer Cyclical': '^SP500-25',
            'Energy': '^GSPE',
            'Utilities': '^SP500-55',
            'Industrials': '^SP500-20',
            'Communication Services': '^SP500-50',
            'Consumer Defensive': '^SP500-30',
            'Basic Materials': '^SP500-15'
        }

    def fetch_price(self, sector: str, date: pd.Timestamp) -> Optional[float]:
        """Fetch price for a sector index on a specific date."""
        # Ensure date is a pd.Timestamp
        if isinstance(date, str):
            date = pd.to_datetime(date)

        cache_key = f"{sector}_{date.date()}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            ticker = self.sector_tickers.get(sector)
            if not ticker:
                logging.warning(f"Unknown sector: {sector}")
                return None

            start_date = (date - pd.DateOffset(days=5)).strftime('%Y-%m-%d')
            end_date = (date + pd.DateOffset(days=5)).strftime('%Y-%m-%d')

            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                logging.warning(f"No data available for {sector} ({ticker})")
                return None

            data.index = data.index.date

            if date.date() in data.index:
                price = float(data.loc[date.date(), 'Close'])
                self.cache[cache_key] = price
                return price

            price = float(data['Close'].iloc[-1])
            logging.info(f"No exact match for {sector} ({ticker}) on {date}, using last available price: {price}")
            self.cache[cache_key] = price
            return price

        except Exception as e:
            logging.error(f"Error fetching price for {sector} ({ticker}): {str(e)}")
            return None


def fill_missing_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing weights with zeros."""
    df.loc[:, df.columns.str.endswith('_w')] = df.loc[:, df.columns.str.endswith('_w')].fillna(0)
    return df


def fill_missing_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing log prices using sector indexes."""
    price_fetcher = PriceFetcher()
    p_cols = df.columns[df.columns.str.endswith('_p')]

    for col in p_cols:
        sector = col.replace('_p', '')
        missing_rows = df[df[col].isna()]

        for _, row in missing_rows.iterrows():
            missing_period = row['filedFor']
            price = price_fetcher.fetch_price(sector, missing_period)

            if price is not None:
                df.at[_, col] = price

    return df


def main():
    """Main processing function."""
    logging.info("Starting data processing...")

    # Load datasets
    data = pd.read_csv('merged_sector_data_2002_2025.csv')

    # Process data
    final_data = fill_missing_weights(data)
    processed_data = fill_missing_prices(final_data)

    # Save results
    processed_data.to_csv("AIDS_Data.csv", index=False)
    logging.info("Processing completed successfully!")


if __name__ == "__main__":
    main()