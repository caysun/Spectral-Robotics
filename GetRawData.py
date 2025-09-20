import serial
import json
import time
import os


def main():
    # Change COM6 (Port) if on a different computer or BAUD rate to match Arduino
    ser = serial.Serial('COM6', 115200, timeout=1)
    output_file = "paperReadings/twentyCalibratedReadings.json" # Change to specified file based on Light Source

    data_list = []

    print("Logging data...")

    # Prompt for label
    label = input("Enter object label (color name): ")

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
            # When Enter is pressed, the input is an empty string
            if input("Press Enter to save current data (or Ctrl+C to quit)...") == "": 
                
                if data:
                    print("Saving current data:", data)
                else:
                    print("No valid data received yet.")
                break
        except KeyboardInterrupt:
            break

   # Build spectral reflectance entry with desired key order
    spectral_entry = {
        "spectral reflectance": {}
    }

    # 1. Clear first
    spectral_entry["spectral reflectance"]["Clear"] = data['spectral data']['Clear']

    # 2. F1-F8 in order
    for i in range(1, 9):
        key = f"F{i}"
        spectral_entry["spectral reflectance"][key] = data['spectral data'][key]

    # 3. Near IR
    spectral_entry["spectral reflectance"]["Near IR"] = data['spectral data']['Near IR']

    # 4. Label last
    spectral_entry["spectral reflectance"]["Label"] = label

    # Save to JSON
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data_json = json.load(f)
            except json.JSONDecodeError:
                data_json = []
    else:
        data_json = []

    data_json.append(spectral_entry)
    with open(output_file, 'w') as f:
        json.dump(data_json, f, indent=4)

if __name__ == "__main__":
    main()
