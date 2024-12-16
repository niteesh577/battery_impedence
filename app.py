import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

# Set renderer to work in Kaggle notebooks
pio.renderers.default = 'iframe_connected'

# Load data
metadata_df = pd.read_csv("metadata.csv")

# Filter for impedance rows and select necessary columns
impedance_df = metadata_df[metadata_df['type'] == 'impedance'][['start_time', 'Re', 'Rct', 'battery_id']]


# Function to parse start_time
def parse_start_time(value):
    try:
        if isinstance(value, str):
            value = value.strip("[]").replace(",", "")  # Remove brackets and commas
            components = [float(x) for x in value.split()]  # Split and convert to float
            if len(components) == 6:
                year, month, day, hour, minute = map(int, components[:5])
                second = int(components[5])  # Handle fractional seconds
                return datetime(year, month, day, hour, minute, second)
        elif isinstance(value, (list, np.ndarray)) and len(value) == 6:
            year, month, day, hour, minute = map(int, value[:5])
            second = int(float(value[5]))  # Handle fractional seconds
            return datetime(year, month, day, hour, minute, second)
    except (ValueError, SyntaxError, TypeError) as e:
        print(f"Failed to parse: {value}, Error: {e}")
    return pd.NaT


# Apply parsing function
impedance_df['start_time'] = impedance_df['start_time'].apply(parse_start_time)

# Drop rows with invalid start_time
impedance_df = impedance_df.dropna(subset=['start_time'])

# Sort data by start_time
impedance_df = impedance_df.sort_values(by='start_time')

# Create a figure for all batteries
fig = go.Figure()

# Plot for each battery_id
for battery_id in impedance_df['battery_id'].unique():
    # Filter data for the current battery_id
    battery_data = impedance_df[impedance_df['battery_id'] == battery_id]

    # Skip if no data for the current battery_id
    if battery_data.empty:
        print(f"No data available for battery_id {battery_id}")
        continue

    # Add Re trace
    fig.add_trace(go.Scatter(
        x=battery_data['start_time'],
        y=battery_data['Re'],
        mode='lines+markers',
        name=f'Battery {battery_id} - Re',
        line=dict(width=2)
    ))

    # Add Rct trace
    fig.add_trace(go.Scatter(
        x=battery_data['start_time'],
        y=battery_data['Rct'],
        mode='lines+markers',
        name=f'Battery {battery_id} - Rct',
        line=dict(width=2)
    ))

# Add layout details
fig.update_layout(
    title="Battery Parameters Over Time",
    xaxis_title="Start Time",
    yaxis_title="Resistance (Ohms)",
    xaxis=dict(tickangle=45),
    legend_title="Battery ID and Parameters",
    template="plotly"
)

# Show the plot
fig.show()