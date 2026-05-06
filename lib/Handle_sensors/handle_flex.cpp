#include "handle_flex.h"
#include <Arduino.h>

void initFlex(FlexSensor &fs, int pin, int type ) {
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

float readFlex(FlexSensor &fs) {
  float angle;
  fs.total -= fs.buffer[fs.index];
  fs.buffer[fs.index] = analogRead(fs.pin);
  fs.total += fs.buffer[fs.index];

  fs.index = (fs.index + 1) % FLEX_SAMPLES;

  float avg = fs.total / (float)FLEX_SAMPLES;

  // Convert to bend angle (0–1000 scale)
  if(fs.type==0)
    angle = map(avg, fs.baseline, 4095, 0, 1000);
  else if(fs.type==1)
    angle = map(avg, fs.baseline, 4095, 0, 180);
  if (angle < 0) angle = 0;

  return angle;
}

