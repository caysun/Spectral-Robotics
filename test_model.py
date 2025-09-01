import serial
import json
import time
import joblib

#Load trained model
model = joblib.load("random_forest_model.joblib")

# Change COM6 (Port) if on a different computer or BAUD rate to match Arduino
ser = serial.Serial("COM6", 115200, timeout=1)

output_file = "live_predictions.json"

print("Live testing started...")
try:
    while True:
        data_list = []

        # Collect 10 valid samples
        while len(data_list) < 10:
            line = ser.readline().decode("utf-8").strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    clear_val = data["spectral data"]["Clear"]
                    if clear_val == 0:
                        continue  # avoid divide by zero

                    # Normalize F1-F8
                    normalized = {}
                    for key in [f"F{i}" for i in range(1, 9)]:
                        normalized[key] = data["spectral data"][key] / clear_val

                    data_list.append(normalized)
                except json.JSONDecodeError:
                    continue

        # Average the 10 samples
        avg_features = {f"F{i}": 0 for i in range(1, 9)}
        # Sum all normalized values
        for sample in data_list:
            for key in avg_features:
                avg_features[key] += sample[key]
        
        # Divide by number of samples to get averages    
        num_entries = len(data_list)    
        for key in avg_features:
            avg_features[key] /= num_entries

        # Converts dictionary to 2D array format for model
        X_live = [[avg_features[f"F{i}"] for i in range(1, 9)]]

        # Predict+probabilites
        prediction = model.predict(X_live)[0]
        probs = model.predict_proba(X_live)[0]

        print(f"Prediction: {prediction}, Probabilities: {probs}")

except KeyboardInterrupt:
    print("Stopped live testing.")
finally:
    # Checks if X_live was defined and if it is nonempty
    if X_live in locals() and len(X_live) > 0:
        result = {
            "features": avg_features,
            "prediction": prediction,
            "probabilities": {label: prob for label, prob in zip(model.classes_, probs)}
        }
        # Load existing data if file exists
        with open(output_file, 'r') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

        # Append result data
        existing_data.append(result)

        # Save back to file
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        print(f"Saved result data to {output_file}")
    else:
        print("No prediction — nothing to save.")
    
    ser.close()