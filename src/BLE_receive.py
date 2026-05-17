import asyncio
from bleak import BleakClient

ADDRESS = "E4:65:B8:0F:73:66"

CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

buffer = ""

def handle_notify(sender, data):
    global buffer

    try:
        text = data.decode("utf-8", errors="ignore")
    except:
        return

    buffer += text

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()

        if not line:
            continue

        print("RX:", line)

        # 👉 send to your model here
        # predict_dynamic_01.print_return(line)

async def main():
    async with BleakClient(ADDRESS) as client:
        print("[+] Connected to ESP32 BLE")

        await client.start_notify(CHAR_UUID, handle_notify)

        while True:
            await asyncio.sleep(1)

asyncio.run(main())