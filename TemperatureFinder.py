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

def softmax(scores, Tempearature=1):
    scores = np.array(scores)

    shifted_scores = (scores - np.max(scores))/Tempearature  # Shift scores by subtracting the max for numerical stability and add temperature scaling

    exp_scores = np.exp(shifted_scores) # Exponentiate the shifted scores

     # Normalize by dividing by the sum of the exponents to get probabilities
    probabilities = exp_scores / np.sum(exp_scores)

    return probabilities 

def main():
    # Change COM6 (Port) if on a different computer or BAUD rate to match Arduino
    ser = serial.Serial('COM6', 115200, timeout=1)
    calibrated_file = "paperReadings/calibratedReadings.json"
    output_file = "temperatureReadings/probabilityTest.json"

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
                print("Latest data updated.")
            except json.JSONDecodeError:
                print("Error decoding due to invalid json input")
        else:
            continue
        # Now check for Enter press to record data
        try:
            if input("Press Enter to save current data (or Ctrl+C to quit)...") == "": # When Enter is pressed, the input is an empty string
                # Perform white reference normalization
                clear_value = data['spectral data']['Clear']

                # Avoid division by zero
                if clear_value != 0:
                    for key in data['spectral data']:
                        if key not in ['Clear', 'Near IR']:  # Only normalize F1-F8
                            data['spectral data'][key] = data['spectral data'][key] / clear_value

                if data:
                    print("Saving current data:", data)
                else:
                    print("No valid data received yet.")
                break
        except KeyboardInterrupt:
            break
        
    # Open calibrated readings file and run cosineSimilarity to detect object
    with open(calibrated_file, 'r') as f:
        readings_list = json.load(f)
        for reading in readings_list:
            # Test cosineSimilarity for each calibrated face
            current_similarity_score = cosineSimilarity(data['spectral data'], reading['spectral reflectance'])
            sim_score_list.append(current_similarity_score)
            if(current_similarity_score > best_similarity_score):
                best_similarity_score = current_similarity_score
                detected_object_name = reading["spectral reflectance"]["Label"]
                detected_object_name = detected_object_name[:-5]
    # Write detected face and score to the output text file
    colors = ["blue", "green", "orange", "red", "yellow"]
    probabilities = softmax(sim_score_list)
    
    with open(output_file, 'a') as f:
        f.write("expected: " + expected_object + "\n")
        f.write("found: " + detected_object_name + "\n")
        
        for sim_score, color in zip(sim_score_list, colors):
            f.write(f"{color} {str(sim_score)}\n")
        f.write("\n")
    

    """ # Build the new entry
    new_entry = {
        "detected": detected_object_name,
        "expected": expected_object,
        "probabilities": {
            color : round(prob,2)
            for prob, color in zip(probabilities, colors)
        }
    }

    
    # If the file exists, load existing data; otherwise, start with an empty list
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append the new entry
    data.append(new_entry)

    # Save everything back to the JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4) """
    

if __name__ == "__main__":
    main()
