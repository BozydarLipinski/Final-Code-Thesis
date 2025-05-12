import pandas as pd
import numpy as np

# Load dataset
data = pd.read_csv('AIDS_Data.csv')

# Get all price columns (ending with '_p')
price_cols = [col for col in data.columns if col.endswith('_p')]

# Calculate log returns for each price column
for col in price_cols:
    # Create new column name (replace '_p' with '_lr' for log returns)
    new_col = col.replace('_p', '_lr')

    # Calculate log returns: ln(P_t/P_{t-1})
    data[new_col] = np.log(data[col] / data[col].shift(1)) * 100

    # Drop original price column if no longer needed
    data = data.drop(columns=[col])

# Drop rows with NaN values (created by shift operation)
data = data.dropna()

# Reorder columns to move portfolio_value to last position
if 'portfolio_value' in data.columns:
    other_columns = [col for col in data.columns if col != 'portfolio_value']
    data = data[other_columns + ['portfolio_value']]
    data['portfolio_value_ln'] = np.log(data['portfolio_value'])




data.to_csv("AIDS_Data_Final.csv", index=False)

