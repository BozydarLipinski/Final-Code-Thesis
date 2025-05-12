import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import YearLocator, DateFormatter

# Load dataset and ensure datetime index
data = pd.read_csv('AIDS_Data_Final.csv')
data['filedFor'] = pd.to_datetime(data['filedFor'])  # Convert to datetime
data.set_index('filedFor', inplace=True)

# 1. Basic Statistics for Sector Weights
weight_cols = [col for col in data.columns if col.endswith('_w')]
weight_stats = data[weight_cols].describe().T
print("Sector Weight Statistics:")
print(weight_stats)
weight_stats.to_csv("weight_stats.csv")


# Create a function to format x-axis with years every 2 years
def format_years(ax):
    ax.xaxis.set_major_locator(YearLocator(2))  # Every 2 years
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.grid(True, which='major', linestyle='--', alpha=0.6)


# 2. Time Series Plot of Sector Weights
plt.figure(figsize=(14, 6))
for col in weight_cols:
    plt.plot(data.index, data[col], label=col.replace('_w', ''), linewidth=2)

plt.title('Sector Weight Composition Over Time', pad=20, fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Weight Proportion', fontsize=12)
plt.legend(bbox_to_anchor=(1.15, 1), loc='upper left', framealpha=1)
format_years(plt.gca())
plt.tight_layout()
plt.show()

# 3. Stacked Area Chart of Portfolio Composition
plt.figure(figsize=(14, 6))
plt.stackplot(data.index,
              *[data[col] for col in weight_cols],
              labels=[col.replace('_w', '') for col in weight_cols],
              alpha=0.85,
              edgecolor='white', linewidth=0.3)

plt.title('Portfolio Composition Over Time', pad=20, fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Weight Proportion', fontsize=12)
plt.legend(bbox_to_anchor=(1.15, 1), loc='upper left', framealpha=1)
format_years(plt.gca())
plt.tight_layout()
plt.show()

# 4. Portfolio Value Over Time
if 'portfolio_value' in data.columns:
    fig, ax = plt.subplots(figsize=(14, 6))  # Single plot with adjusted height

    # Portfolio Value Plot
    ax.plot(data.index, data['portfolio_value'], color='black', linewidth=2.5)
    ax.set_title('Total Portfolio Value Over Time', pad=15, fontsize=13)
    ax.set_ylabel('Portfolio Value', fontsize=12)
    ax.set_xlabel('Year', fontsize=12)
    ax.grid(True)

    # Format as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    # Get unique years from the index and set ticks
    years = sorted(list({x.year for x in data.index}))
    ax.set_xticks([pd.Timestamp(year=y, month=1, day=1) for y in years])
    ax.set_xticklabels(years, rotation=45, ha='right')

    plt.tight_layout()
    plt.show()