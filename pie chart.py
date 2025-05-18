import pandas as pd
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv("AIDS_Data_Final.csv")  # Update path if needed

# Extract weight columns and calculate average
weight_columns = [col for col in df.columns if col.endswith('_w')]
average_weights = df[weight_columns].mean()
average_weights.index = average_weights.index.str.replace('_w', '')

# Plot
colors = plt.cm.tab20.colors  # Optional: pick a colormap with distinct colors
plt.figure(figsize=(8, 8))
wedges, _ = plt.pie(average_weights, colors=colors, startangle=140)

# Add legend on the side
plt.legend(wedges, average_weights.index, title="Sectors", loc="center left", bbox_to_anchor=(1, 0.5))
plt.title("Average Sector Weights")
plt.axis('equal')  # Make it a circle
plt.tight_layout()
plt.show()
