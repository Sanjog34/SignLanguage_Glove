import serial
import csv
import time
import os
from collections import deque

# === SETTINGS ===
PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
CSV_FILE = '../datasets/20K/sensor_data_8flex_new_char_20k.csv'

MAX_RECORDS = 500
WRITE_INTERVAL = 50

LABEL = "char"

# === SETUP ===
log_queue = deque(maxlen=MAX_RECORDS)
entry_count = 0

file_exists = os.path.exists(CSV_FILE)

# Open serial
def open_serial():
    while True:
        try:
            ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"\nSerial connected on {PORT}. Logging started...")
            return ser
        except serial.SerialException:
            print("Could not open port. Retrying...")
            time.sleep(2)

ser = open_serial()

# Open file in append mode (IMPORTANT)
file = open(CSV_FILE, 'a', newline='')
writer = csv.writer(file)

# Write header ONLY if file is new
if not file_exists:
    writer.writerow([
        'idxUp','idxLow','midUp','midLow',
        'ringUp','ringLow','thumb','pinky',
        'ax','ay','az','gx','gy','gz','label'
    ])
    file.flush()

print("Collecting 500 new samples...\n")

try:
    while entry_count < MAX_RECORDS:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line or ',' not in line:
                continue

            parts = line.split(',')

            if len(parts) != 17:
                continue

            parts = parts[:14]

            row = list(map(float, parts)) + [LABEL]

            log_queue.append(row)
            entry_count += 1

            print("{:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6.2f} {:<6}".format(*row))

            # periodic write
            if entry_count % WRITE_INTERVAL == 0:
                writer.writerows(log_queue)
                file.flush()
                log_queue.clear()

        except serial.SerialException:
            print("Serial disconnected. Reconnecting...")
            ser.close()
            ser = open_serial()

        except ValueError:
            continue

    # final flush
    if len(log_queue) > 0:
        writer.writerows(log_queue)

    file.flush()

    print("\n500 samples appended successfully.")

except KeyboardInterrupt:
    print("\nStopped manually. Saving remaining data...")

    if len(log_queue) > 0:
        writer.writerows(log_queue)

    file.flush()

finally:
    file.close()
    ser.close()
    print("File closed safely.")