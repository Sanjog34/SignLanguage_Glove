# import serial
# import csv
# import time
# from datetime import datetime
# from collections import deque

# # === SETTINGS ===
# PORT = '/dev/ttyUSB0'      # Update with your ESP32 port
# BAUD_RATE = 115200
# CSV_FILE = 'sensor_data_alpha_"o"_250.csv'
# MAX_RECORDS = 250
# WRITE_INTERVAL = 80        # write CSV every 80 new entries

# # === SETUP ===
# log_queue = deque(maxlen=MAX_RECORDS)
# entry_count = 0

# # Load previous CSV if exists
# try:
#     with open(CSV_FILE, 'r') as file:
#         reader = csv.reader(file)
#         next(reader)  # skip header
#         for row in reader:
#             if len(row) == 3: #6
#                 log_queue.append(tuple(row))
# except FileNotFoundError:
#     pass

# def open_serial():
#     while True:
#         try:
#             ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
#             time.sleep(2)  # allow ESP32 to reset
#             print(f"\n Serial connected on {PORT}. Logging started...")
#             return ser
#         except serial.SerialException:
#             print(f" Could not open {PORT}. Retrying in 2s...")
#             time.sleep(2)

# ser = open_serial()

# print("Press Ctrl+C to stop.\n")
# # print("{:<20} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
# #     "Timestamp", "IndexFlex", "MidFlex", "AccX", "AccY", "AccZ"))
# print("{:<20} {:<10} {:<10}".format(
#     "Timestamp", "MidDown", "MidUp"))

# try:
#     while True:
        
#         try:
#             line = ser.readline().decode('utf-8').strip()
            
#             if not line or ',' not in line:
#                 continue  # skip empty or invalid lines

#             parts = line.split(',')
#             if len(parts) != 2:#5
#                 continue  # skip lines with wrong number of values

#             # index_flex, mid_flex, accX, accY, accZ = map(float, parts)
#             down_flex, up_flex = map(float, parts)
#             timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#             # log_queue.append((timestamp, index_flex, mid_flex, accX, accY, accZ))
#             log_queue.append((timestamp, down_flex, up_flex))
#             entry_count += 1

#             # Print
#             # print("{:<20} {:<10.2f} {:<10.2f} {:<10.2f} {:<10.2f} {:<10.2f}".format(
#             #     timestamp, index_flex, mid_flex, accX, accY, accZ))
#             print("{:<20} {:<10.2f} {:<10.2f}".format(
#                 timestamp, down_flex, up_flex))

#             # Write CSV every WRITE_INTERVAL entries
#             if entry_count >= WRITE_INTERVAL:
#                 with open(CSV_FILE, 'w', newline='') as file:
#                     writer = csv.writer(file)
#                     # writer.writerow(['Timestamp', 'IndexFlex', 'MidFlex', 'AccX', 'AccY', 'AccZ'])
#                     writer.writerow(['Timestamp', 'MidDown', 'MidUp'])
#                     writer.writerows(log_queue)
#                 entry_count = 0

#         except serial.SerialException:
#             print("  Serial disconnected. Pausing until device reconnects...")
#             ser.close()
#             ser = open_serial()
#         except ValueError:
#             continue  # skip lines that can't be converted to float

# except KeyboardInterrupt :
#     print("\n Logging stopped by user. Saving CSV...")
#     with open(CSV_FILE, 'w', newline='') as file:
#         writer = csv.writer(file)
#         # writer.writerow(['Timestamp', 'IndexFlex', 'MidFlex', 'AccX', 'AccY', 'AccZ'])
#         writer.writerow(['Timestamp', 'MidDown', 'MidUp'])
#         writer.writerows(log_queue)
# finally:
#     ser.close()


# import serial
# import csv
# import time
# from datetime import datetime
# from collections import deque


# PORT = '/dev/ttyUSB0'      # connected ESP32 port
# BAUD_RATE = 115200
# CSV_FILE = 'sensor_data_alpha_"C"_250_new_sensors.csv'
# MAX_RECORDS = 250
# WRITE_INTERVAL = 80        # write CSV every 80 new entries

# # === SETUP ===
# log_queue = deque(maxlen=MAX_RECORDS)
# entry_count = 0
# total_entries = 0  # total logged entries

# # Load previous CSV if exists
# try:
#     with open(CSV_FILE, 'r') as file:
#         reader = csv.reader(file)
#         next(reader)  # skip header
#         for row in reader:
#             if len(row) == 3:  # ['Timestamp', 'MidDown', 'MidUp']
#                 log_queue.append(tuple(row))
#                 total_entries += 1
# except FileNotFoundError:
#     pass

# def open_serial():
#     while True:
#         try:
#             ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
#             time.sleep(2)  # allow ESP32 to reset
#             print(f"\n Serial connected on {PORT}. Logging started...")
#             return ser
#         except serial.SerialException:
#             print(f" Could not open {PORT}. Retrying in 2s...")
#             time.sleep(2)

# ser = open_serial()

# print("Press Ctrl+C to stop.\n")
# print("{:<10} {:<10}".format("MidDown", "MidUp"))

# try:
#     while total_entries < MAX_RECORDS:
#         try:
#             line = ser.readline().decode('utf-8').strip()
#             if not line or ',' not in line:
#                 continue  # skip empty or invalid lines

#             parts = line.split(',')
#             if len(parts) != 2:
#                 continue  # skip invalid line

#             down_flex, up_flex = map(float, parts)
#             # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#             log_queue.append((down_flex, up_flex))
#             entry_count += 1
#             total_entries += 1

#             print(" {:<10.2f} {:<10.2f}".format( down_flex, up_flex))

#             # Write CSV every WRITE_INTERVAL entries
#             if entry_count >= WRITE_INTERVAL or total_entries == MAX_RECORDS:
#                 with open(CSV_FILE, 'w', newline='') as file:
#                     writer = csv.writer(file)
#                     writer.writerow(['MidDown', 'MidUp'])
#                     writer.writerows(log_queue)
#                 entry_count = 0

#         except serial.SerialException:
#             print(" Serial disconnected. Pausing until device reconnects...")
#             ser.close()
#             ser = open_serial()
#         except ValueError:
#             continue  # skip conversion errors

#     print(f"\n Logging complete. {MAX_RECORDS} entries saved to '{CSV_FILE}'.")

# except KeyboardInterrupt:
#     print("\n Logging stopped by user.")

# finally:
#     # Always save before exit
#     with open(CSV_FILE, 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([ 'MidDown', 'MidUp'])
#         writer.writerows(log_queue)
#     ser.close()
#     print("CSV file saved and serial closed.")



import serial
import csv
import time
from collections import deque

# === SETTINGS ===
PORT = '/dev/ttyUSB0'       # ESP32 port
BAUD_RATE = 115200
CSV_FILE = '../datasets/20K/sensor_data_8flex_new_kha_20k.csv'
MAX_RECORDS = 500            # total samples to record
WRITE_INTERVAL = 50          # write to CSV every 50 entries

# === SETUP ===
log_queue = deque(maxlen=MAX_RECORDS)
entry_count = 0
total_entries = 0
LABEL = "kha"  # Change label as needed
# Load previous CSV if exists
try:
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        for row in reader:
            if len(row) == 8:  # 8 flex sensors
                log_queue.append(tuple(map(float, row)))
                total_entries += 1
except FileNotFoundError:
    pass

# Open serial connection
def open_serial():
    while True:
        try:
            ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # allow ESP32 to reset
            print(f"\nSerial connected on {PORT}. Logging started...")
            return ser
        except serial.SerialException:
            print(f"Could not open {PORT}. Retrying in 2s...")
            time.sleep(2)

ser = open_serial()

print("Press Ctrl+C to stop.\n")
print("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8} {:<8}".format(
    "idxUp", "idxLow", "midUp", "midLow", "ringUp", "ringLow", "thumb", "pinky","ax","ay","az","gx","gy","gz", "label"))

try:
    while total_entries < MAX_RECORDS:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line or ',' not in line:
                continue

            parts = line.split(',')
            if len(parts) != 17:
                continue  # skip invalid lines
            parts = parts[:14]

            # Convert to float
            flex_values = list(map(float, parts)) +[LABEL]

            # Append to queue
            log_queue.append(flex_values)
            entry_count += 1
            total_entries += 1

            # Print nicely
            print("{:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8.2f} {:<8}".format(*flex_values))

            # Write CSV periodically
            if entry_count >= WRITE_INTERVAL or total_entries == MAX_RECORDS:
                with open(CSV_FILE, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['idxUp','idxLow','midUp','midLow','ringUp','ringLow','thumb','pinky','ax','ay','az','gx','gy','gz','label'])
                    writer.writerows(log_queue)
                entry_count = 0

        except serial.SerialException:
            print("Serial disconnected. Reconnecting...")
            ser.close()
            ser = open_serial()
        except ValueError:
            continue  # skip invalid float conversions

    print(f"\nLogging complete. {MAX_RECORDS} entries saved to '{CSV_FILE}'.")

except KeyboardInterrupt:
    print("\nLogging stopped by user.")

finally:
    # Save CSV on exit
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['idxUp','idxLow','midUp','midLow','ringUp','ringLow','thumb','pinky','ax','ay','az','gx','gy','gz','label'])
        writer.writerows(log_queue)
    ser.close()
    print("CSV file saved and serial connection closed.")
