#include "BluetoothSerial.h"
#include "Arduino.h"
BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);          // Optional: for USB debug
  Serial.println(SerialBT.begin("ESP32_BT"));    // Device name (what you'll see while pairing)
  Serial.println("Bluetooth started. Pair with ESP32_BT");
}

void loop() {
  SerialBT.println("Hello World");  // Send over Bluetooth
//   Serial.println("Hello World");    // Optional: also print to USB serial
  delay(1000);                     // 1 second delay
}