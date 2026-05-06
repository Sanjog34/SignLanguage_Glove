#ifndef _HANDLE_FLEX_H
#define _HANDLE_FLEX_H
const int FLEX_SAMPLES = 10;
struct FlexSensor {
  int pin;
  int buffer[FLEX_SAMPLES];
  int index = 0;
  int total = 0;
  int baseline = 0;
  int type;
};
void initFlex(FlexSensor &fs, int pin, int type );
float readFlex(FlexSensor &fs);
#endif