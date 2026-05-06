#include <Arduino.h>
#include "handle_gyro.h"
const int MPU_ADDR = 0x68;
void setup(){
handle_gyro_init(MPU_ADDR);
Serial.begin(115200);
}
void loop(){
Send_gyro_values(calc_values(Get_MPU_Data(MPU_ADDR)));
delay(40);
}