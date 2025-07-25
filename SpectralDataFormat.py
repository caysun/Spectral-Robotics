import serial
import json
import time

# Change COM6 (Port) if on a different computer or BAUD rate to match Arduino
ser = serial.Serial('COM6', 115200, timeout=1)
output_file = "darkReference.json" # Change to specified file based on Light Source

data_list = []

try:
    print("Logging data...")
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)
                data_list.append(data)
                print(data)
            except json.JSONDecodeError:
                print("Invalid JSON:", line)

except KeyboardInterrupt:
    print("Stopped data collection.")

finally:
    # Save all collected data to a JSON file
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=2)
    print(f"Saved {len(data_list)} entries to {output_file}")
