#include <Wire.h>
#include <Arduino.h>


// FLEX SENSOR CONFIGURATION


const int PIN_INDEX_UP      = 14; 
const int PIN_INDEX_LOW     = 27;

const int PIN_MIDDLE_UP     = 25;
const int PIN_MIDDLE_LOW    = 26;

const int PIN_RING_UP       = 33;
const int PIN_RING_LOW      = 32;

const int PIN_THUMB         = 13;   
const int PIN_PINKY         = 35;   


// MOVING AVERAGE SETTINGS

const int FLEX_SAMPLES = 10;

// Structure for each flex sensor
struct FlexSensor {
  int pin;
  int buffer[FLEX_SAMPLES];
  int index = 0;
  int total = 0;
  int baseline = 0;
  int type;
};

// Createing objects for each sensor
FlexSensor indexUp, indexLow;
FlexSensor middleUp, middleLow;
FlexSensor ringUp, ringLow;
FlexSensor thumbFlex, pinkyFlex;



// FLEX SENSOR FUNCTIONS

// --- Initialize one sensor (calibration + buffer fill) ---
void initFlex(FlexSensor &fs, int pin,int type) {
  fs.pin = pin;
  fs.type = type;

  long sum = 0;
  for (int i = 0; i < 100; i++) {
    sum += analogRead(pin);
    delay(5);
  }
  fs.baseline = sum / 100;

  fs.total = 0;
  for (int i = 0; i < FLEX_SAMPLES; i++) {
    fs.buffer[i] = fs.baseline;
    fs.total += fs.baseline;
  }
}

// --- Read and smooth one sensor ---
float readFlex(FlexSensor &fs) {
  float angle;
  fs.total -= fs.buffer[fs.index];
  fs.buffer[fs.index] = analogRead(fs.pin);
  fs.total += fs.buffer[fs.index];

  fs.index = (fs.index + 1) % FLEX_SAMPLES;

  float avg = fs.total / (float)FLEX_SAMPLES;
  if(fs.type==1) {
   angle = map(avg, fs.baseline, 4095, 0, 180);
  }
  else if (fs.type==0) {
   angle = map(avg, fs.baseline, 4095, 0, 1000);
  }
   
  if (angle < 0) angle = 0;

  return angle;
}


void setup() {
  Serial.begin(115200);

  // Initialize all flex sensors
  initFlex(indexUp,    PIN_INDEX_UP,0);
  initFlex(indexLow,   PIN_INDEX_LOW,0);

  initFlex(middleUp,   PIN_MIDDLE_UP,1);
  initFlex(middleLow,  PIN_MIDDLE_LOW,1);

  initFlex(ringUp,     PIN_RING_UP,0);
  initFlex(ringLow,    PIN_RING_LOW,0);

  initFlex(thumbFlex,  PIN_THUMB,0);
  initFlex(pinkyFlex,  PIN_PINKY,0);

  Serial.println("Calibration complete.");
  Serial.println("Output: idxUp,idxLow,midUp,midLow,ringUp,ringLow,thumb,pinky");
}


void loop() {

  float idxUp   = readFlex(indexUp);
  float idxLow  = readFlex(indexLow);

  float midUp   = readFlex(middleUp);
  float midLow  = readFlex(middleLow);

  float RingUp  = readFlex(ringUp);
  float RingLow = readFlex(ringLow);

  float thumb   = readFlex(thumbFlex);
  float pinky   = readFlex(pinkyFlex);

  // Output CSV
  Serial.print(idxUp, 2);  Serial.print(",");
  Serial.print(idxLow, 2); Serial.print(",");

  Serial.print(midUp, 2);  Serial.print(",");
  Serial.print(midLow, 2); Serial.print(",");

  Serial.print(RingUp, 2); Serial.print(",");
  Serial.print(RingLow, 2); Serial.print(",");

  Serial.print(thumb, 2);  Serial.print(",");
  Serial.println(pinky, 2);

  delay(40);
}