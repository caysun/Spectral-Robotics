import serial
import json
import time

# Wait for user to enter label
label = input("Enter label for this data (e.g., 'dark', 'white', 'sample1'): ")
# Change COM6 (Port) if on a different computer or BAUD rate to match Arduino
ser = serial.Serial('COM6', 115200, timeout=1)
output_file = "MLpaperReadings/green.json" # Change to specified file based on Light Source

data_list = []

try:
    print("Logging data...")
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)

                # Extract clear value
                clear_val = data["spectral data"]["Clear"]

                # Avoid divide-by-zero
                if clear_val != 0:
                    for key in [f"F{i}" for i in range(1, 9)]:
                        data["spectral data"][key] = data["spectral data"][key] / clear_val
                data["spectral data"]["label"] = label

                data_list.append(data)
                print(data)
            except json.JSONDecodeError:
                print("Invalid JSON:", line)
            if len(data_list) >= 10:
                break

except KeyboardInterrupt:
    print("Stopped data collection.")

finally:
    if data_list:
        # Initialize accumulator for normalized F1-F8
        avg_data = {f"F{i}": 0 for i in range(1, 9)}

        # Sum all normalized values
        for entry in data_list:
            for key in avg_data.keys():
                avg_data[key] += entry["spectral data"][key]

        # Divide by number of samples to get averages
        num_entries = len(data_list)
        for key in avg_data.keys():
            avg_data[key] /= num_entries

        # Add label at the top level
        averaged_entry = {"label": label}
        averaged_entry.update(avg_data)

        # Load existing data if file exists
        with open(output_file, 'r') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
            except json.JSONDecodeError:
                existing_data = []

        # Append averaged data
        existing_data.append(averaged_entry)

        # Save back to file
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=2)

        print(f"Saved averaged data to {output_file}")
    else:
        print("No data collected — nothing to save.")