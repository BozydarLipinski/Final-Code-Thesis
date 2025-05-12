import pandas as pd

# Load your dataset
data = pd.read_csv('AIDS_Data_Final.csv', parse_dates=['filedFor'])

# Get all sector weight columns (ending with '_w')
sector_cols = [col for col in data.columns if col.endswith('_w')]

# Convert dates to quarters
data['quarter'] = data['filedFor'].dt.to_period('Q')

# Count quarters where each sector was present (weight > 0)
sector_presence = {}
for col in sector_cols:
    sector_name = col.replace('_w', '')
    sector_presence[sector_name] = len(data[data[col] > 0]['quarter'].unique())

# Convert to DataFrame for nice display
presence_df = pd.DataFrame.from_dict(sector_presence,
                                   orient='index',
                                   columns=['Quarters Present'])
presence_df.index.name = 'Sector'

# Sort by most frequently present sectors
presence_df = presence_df.sort_values('Quarters Present', ascending=False)

print("Number of quarters each sector was present:")
print(presence_df/91)

# Optional: Visualize the results
import matplotlib.pyplot as plt

presence_df.plot(kind='bar', figsize=(10, 6))
plt.title('Sector Presence by Number of Quarters')
plt.ylabel('Number of Quarters')
plt.xlabel('Sector')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()