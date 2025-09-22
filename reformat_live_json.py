import json

# load the JSON file
with open("live_predictions.json") as f:
    json_data = json.load(f)

new_json = []
current_separator = None

for entry in json_data:
    # skip "*****" entries
    if "*****************************************************************************" in entry:
        continue

    # if it's a separator (==...), store it temporarily
    if "=====================================================" in entry:
        current_separator = entry
        continue

    # if it's a regular prediction entry
    if current_separator:
        # append the separator before the prediction
        new_json.append(current_separator)
        current_separator = None

    # append the prediction entry
    new_json.append(entry)

# save the cleaned JSON
with open("live_predictions_clean.json", "w") as f:
    json.dump(new_json, f, indent=2)