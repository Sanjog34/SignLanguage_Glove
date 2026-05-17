import serial
import time
import os
import predict_dynamic_01

ESP32_MAC = "E4:65:B8:0F:73:66"

def connect_rfcomm():
    os.system("sudo rfcomm release 0")
    time.sleep(1)
    os.system(f"sudo rfcomm bind 0 {ESP32_MAC} 1")
    time.sleep(2)

def read_bluetooth(port="/dev/rfcomm0", baud=115200):

    while True:  # reconnect loop
        try:
            print("[*] Connecting Bluetooth...")
            connect_rfcomm()

            with serial.Serial(port, baud, timeout=2) as ser:
                print(f"[+] Connected to {port}")

                time.sleep(1)
                ser.reset_input_buffer()

                while True:
                    raw_bytes = ser.readline()

                    if not raw_bytes:
                        continue

                    raw = raw_bytes.decode(
                        "utf-8",
                        errors="ignore"
                    ).strip()

                    if not raw:
                        continue

                    # Remove prefix
                    if raw.startswith("D,") or raw.startswith("S,"):
                        raw = raw[2:]

                    if not raw.strip():
                        continue

                    # print(f"RAW: {raw}")

                    # Run prediction directly
                    predict_dynamic_01.print_return(raw)

        except serial.SerialException as e:
            print(f"[!] Connection lost: {e}")

        except KeyboardInterrupt:
            print("\n[!] Exiting...")
            break

        except Exception as e:
            print(f"[ERROR] {e}")

        print("[*] Reconnecting in 3 seconds...")
        time.sleep(3)
        

if __name__ == "__main__":
    read_bluetooth()