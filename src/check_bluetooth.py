import serial
import time

def read_bluetooth(port, baud=115200):
    # Release any stale binding first:
    # sudo rfcomm release 0 && sudo rfcomm bind 0 XX:XX:XX:XX:XX:XX 1

    while True:  # auto-reconnect loop
        try:
            with serial.Serial(port, baud, timeout=2) as ser:
                print(f"[+] Connected to {port}")
                time.sleep(1)  # let ESP32 stabilize after connection
                ser.reset_input_buffer()  # flush garbage from buffer

                while True:
                    # Use read_until or readline — both need \n from ESP32
                    raw_bytes = ser.readline()

                    if not raw_bytes:
                        continue  # timeout, no data yet

                    raw = raw_bytes.decode("utf-8", errors="ignore").strip()

                    if not raw:
                        continue

                    # Strip your D, or S, prefix
                    if raw.startswith("D,") or raw.startswith("S,"):
                        raw = raw[2:]

                    if not raw.strip():
                        continue

                    print(f"Data: {raw}")
                    # your processing logic here

        except serial.SerialException as e:
            print(f"[!] Connection lost: {e}")
            print("[*] Retrying in 3 seconds...")
            time.sleep(3)
            # re-bind rfcomm before retry
            import os
            os.system("sudo rfcomm release 0")
            os.system("sudo rfcomm bind 0 E4:65:B8:0F:73:66 1")  # ← your ESP32 MAC

if __name__ == "__main__":
    read_bluetooth(port="/dev/rfcomm0", baud=115200)