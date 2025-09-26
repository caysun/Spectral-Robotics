import json
import math

# Load JSON data from file
with open("classic_predictions.json", "r") as f:
    json_data = json.load(f)

# Filter only objects that have a 'prediction' key
valid_entries = [entry for entry in json_data if "prediction" in entry]

# Compute squared differences
squared_diffs = []
for entry in valid_entries:
    prediction = entry["prediction"]
    p = entry["probabilities"][prediction]  # probability of predicted color
    squared_diffs.append((1 - p) ** 2)

# Calculate RMS and print results
if squared_diffs:
    mean_square = sum(squared_diffs) / len(squared_diffs)
    rms = math.sqrt(mean_square)
    print(f"Used {len(squared_diffs)} predictions.")
    print(f"Root Mean Squared value: {rms:.6f}")
else:
    print("No valid prediction data found.")