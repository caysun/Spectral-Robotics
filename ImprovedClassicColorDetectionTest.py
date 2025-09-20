import serial
import json
import time
import numpy as np
import json
import os

def cosineSimilarity(f1, f2):
    # Extract F1-F8 values as lists from each file (dictionary)
    keys = [f"F{i}" for i in range(1, 9)]  

    A = [f1[key] for key in keys]
    B = [f2[key] for key in keys]

    # Compute numerator: sum of A_i * B_i
    numerator = sum(a * b for a, b in zip(A, B))

    # Compute denominator: product of magnitudes
    magA = sum(a * a for a in A) ** 0.5
    magB = sum(b * b for b in B) ** 0.5

    if magA == 0 or magB == 0:
        return 0  # Avoid division by zero

    cosine_sim = numerator / (magA * magB)
    return cosine_sim

def softmax(scores):
    scores = np.array(scores)

    shifted_scores = scores - np.max(scores)  # Shift scores by subtracting the max for numerical stability

    exp_scores = np.exp(shifted_scores) # Exponentiate the shifted scores

     # Normalize by dividing by the sum of the exponents to get probabilities
    probabilities = exp_scores / np.sum(exp_scores)

    return probabilities 

def main():
    # Change COM6 (Port) if on a different computer or BAUD rate to match Arduino
    ser = serial.Serial('COM6', 115200, timeout=1)
    calibrated_file = "paperReadings/twentyCalibratedReadings.json"
    output_file = "classic_predictions.json"

    data = ""
    best_similarity_score = 0.0
    sim_score_list = []
    detected_object_name = ""
    # Ask user for expected object name
    expected_object = input("Enter the expected object name: ")

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)

                # Normalize calibrated values by dividing by the Clear value
                clear = max(data['spectral data']['Clear'], 1e-6)  # avoid division by zero
                for i in range(1, 9):
                    key = f"F{i}"
                    data['spectral data'][key] /= clear

                print("Latest data updated.")
            except json.JSONDecodeError:
                print("Error decoding due to invalid json input")
        else:
            continue
        # Now check for Enter press to record data
        try:
            if input("Press Enter to save current data (or Ctrl+C to quit)...") == "": # When Enter is pressed, the input is an empty string
                # Perform white reference normalization
                clear_value = max(data['spectral data']['Clear'], 1e-6)

                # Divide by Clear first
                for key in data['spectral data']:
                    if key not in ['Clear', 'Near IR']:  # Only normalize F1-F8
                        data['spectral data'][key] /= clear_value
                
                if data:
                    print("Saving current data:", data)
                else:
                    print("No valid data received yet.")
                break
        except KeyboardInterrupt:
            break
        
    # Load calibrated readings
    with open(calibrated_file, 'r') as f:
        readings_list = json.load(f)

    colors = ["blue", "green", "orange", "red", "yellow"]
    sim_score_list = []

    # Compute cosine similarities for all templates
    for reading in readings_list:
        template = reading['spectral reflectance']
        template_clear = max(template['Clear'], 1e-6)
        # Normalize template by its Clear
        keys = [f"F{i}" for i in range(1, 9)]
        template_norm = template.copy()
        for key in keys:
            template_norm[key] = template[key] / template_clear

        sim = cosineSimilarity(data['spectral data'], template_norm)
        sim_score_list.append(sim)
    
    # Softmax over all 20 templates
    probabilities_20 = softmax(sim_score_list)

# Combine 4 templates per color
    color_probs_sum = {}
    for i, color in enumerate(colors):
        color_probs_sum[color] = sum(probabilities_20[i*4:(i+1)*4])

    # Optional: normalize across colors so sum = 1
    total = sum(color_probs_sum.values())
    color_probs_normalized = {color: round(p/total, 2) for color, p in color_probs_sum.items()}

    # Determine best color
    detected_object_name = max(color_probs_normalized, key=color_probs_normalized.get)

    # Build new entry
    new_entry = {
        "prediction": detected_object_name,
        "probabilities": color_probs_normalized
    }

    # Save to JSON
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data_json = json.load(f)
            except json.JSONDecodeError:
                data_json = []
    else:
        data_json = []

    data_json.append(new_entry)
    with open(output_file, 'w') as f:
        json.dump(data_json, f, indent=4)

    print("Saved entry:", new_entry)

if __name__ == "__main__":
    main()
