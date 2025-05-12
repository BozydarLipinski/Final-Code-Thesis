import pandas as pd

# Load dataset
data = pd.read_csv('final_sector_portfolio.csv')

# Convert 'year_quarter' to string and ensure 'filedFor' is in datetime format
data['year_quarter'] = data['year_quarter'].astype(str)
data['filedFor'] = pd.to_datetime(data['filedFor'])


# Pivot for sector weights and prices
pivot_w = data.pivot(index=['filedFor', 'year_quarter'], columns='industry', values='sector_percentage')
pivot_p = data.pivot(index=['filedFor', 'year_quarter'], columns='industry', values='sector_price_index')

# Merge into a single dataframe
final_data = pivot_w.merge(pivot_p, left_index=True, right_index=True, suffixes=('_w', '_p'))

# Add portfolio value
portfolio_values = data[['filedFor', 'year_quarter', 'portfolio_value']].drop_duplicates().set_index(['filedFor', 'year_quarter'])
final_data = final_data.merge(portfolio_values, left_index=True, right_index=True)

# Save processed dataset
final_data.to_csv('processed_aids_data_1.csv')