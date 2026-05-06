#ifndef _HANDLE_GYRO_H
#define _HANDLE_GYRO_H

#include <Wire.h>
const int FILTER_SIZE = 10; // number of samples for smoothing
static int bufIndex = 0;
void handle_gyro_init(int addr);
int16_t *Get_MPU_Data(int addr);
float *calc_values(int16_t *mpu_data);
void Send_gyro_values(float *values_to_send);
extern float accXBuf[FILTER_SIZE], accYBuf[FILTER_SIZE], accZBuf[FILTER_SIZE], temperature[FILTER_SIZE], gyroX[FILTER_SIZE], gyroY[FILTER_SIZE], gyroZ[FILTER_SIZE];

#endif