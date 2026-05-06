#include <Wire.h>
#include <Arduino.h>
// #include "BluetoothSerial.h"
#include "handle_gyro.h"
#include "handle_flex.h"

const int MPU_ADDR = 0x68;

const int PIN_INDEX_UP = 32;
const int PIN_INDEX_LOW = 33;

const int PIN_MIDDLE_UP = 25;
const int PIN_MIDDLE_LOW = 26;

const int PIN_RING_UP = 27;
const int PIN_RING_LOW = 14;

const int PIN_THUMB = 35;
const int PIN_PINKY = 13;

// BluetoothSerial SerialBT;

// Create objects for each sensor
FlexSensor indexUp, indexLow;
FlexSensor middleUp, middleLow;
FlexSensor ringUp, ringLow;
FlexSensor thumbFlex, pinkyFlex;

void setup()
{
  handle_gyro_init(MPU_ADDR);
  Serial.begin(115200);
  // SerialBT.begin("ESP32_BT");
  // Initialize all flex sensors
  initFlex(indexUp, PIN_INDEX_UP, 0);
  initFlex(indexLow, PIN_INDEX_LOW, 0);

  initFlex(middleUp, PIN_MIDDLE_UP, 1);
  initFlex(middleLow, PIN_MIDDLE_LOW, 1);

  initFlex(ringUp, PIN_RING_UP, 0);
  initFlex(ringLow, PIN_RING_LOW, 0);

  initFlex(thumbFlex, PIN_THUMB, 0);
  initFlex(pinkyFlex, PIN_PINKY, 0);

  Serial.println("Calibration complete.");
  Serial.println("Output: idxUp,idxLow,midUp,midLow,ringUp,ringLow,thumb,pinky,ax,ay,az,gx,gy,gz");
}

void loop()
{

  float idxUp = readFlex(indexUp);
  float idxLow = readFlex(indexLow);

  float midUp = readFlex(middleUp);
  float midLow = readFlex(middleLow);

  float RingUp = readFlex(ringUp);
  float RingLow = readFlex(ringLow);

  float thumb = readFlex(thumbFlex);
  float pinky = readFlex(pinkyFlex);

  // Output CSV
  Serial.print(idxUp, 2);
  Serial.print(",");
  Serial.print(idxLow, 2);
  Serial.print(",");
  Serial.print(midUp, 2);
  Serial.print(",");
  Serial.print(midLow, 2);
  Serial.print(",");
  Serial.print(RingUp, 2);
  Serial.print(",");
  Serial.print(RingLow, 2);
  Serial.print(",");
  Serial.print(thumb, 2);
  Serial.print(",");
  Serial.print(pinky, 2);
  Serial.print(",");
  Send_gyro_values(calc_values(Get_MPU_Data(MPU_ADDR)));

  delay(40);
}