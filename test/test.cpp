#include <Arduino.h>
#include "handle_flex.h"

const int PIN_THUMB = 35;
const int PIN_INDEX_UP = 32;
const int PIN_INDEX_LOW = 33;
FlexSensor thumbFlex;
FlexSensor indexUp, indexLow;
void setup() {
  
  Serial.begin(115200);
    initFlex(thumbFlex, PIN_THUMB, 0);
    initFlex(indexUp, PIN_INDEX_UP, 0);
  initFlex(indexLow, PIN_INDEX_LOW, 0);
}
void loop() {
   float thumb = readFlex(thumbFlex);
  float idxUp = readFlex(indexUp);
  float idxLow = readFlex(indexLow);
  Serial.print(idxUp, 2);
  Serial.print(",");
  Serial.print(idxLow, 2);
  Serial.print(",");
   Serial.println(thumb, 2);
   delay(50);
}