#include "handle_gyro.h"
#include <Arduino.h>
#include <Wire.h>
#include "BluetoothSerial.h"

float values[7];
int16_t data[7];

float accXBuf[FILTER_SIZE] = {0};
float accYBuf[FILTER_SIZE] = {0};
float accZBuf[FILTER_SIZE] = {0};
float temperature[FILTER_SIZE] = {0};
float gyroX[FILTER_SIZE] = {0};
float gyroY[FILTER_SIZE] = {0};
float gyroZ[FILTER_SIZE] = {0};

void handle_gyro_init(int addr)
{
    Wire.begin();
    Wire.beginTransmission(addr);
    Wire.write(0x6B);
    Wire.write(0);
    Wire.endTransmission(true);
}

int16_t *Get_MPU_Data(int addr)
{
    
    Wire.beginTransmission(addr);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(addr, 14, 1);
    for (int i = 0; i < 7; i++)
    {
        // in sequence
        data[i] = Wire.read() << 8 | Wire.read(); // 0->acx, 1->acy, 2->acz,
                                                  // 3->Temp,
                                                  // 4->gyx, 5->gyy, 6->gyz
    }
    return data;
}
float *calc_values(int16_t *mpu_data)
{
    
    float AccX = mpu_data[0] / 16384.0;
    float AccY = mpu_data[1] / 16384.0;
    float AccZ = mpu_data[2] / 16384.0;
    float Temp = (mpu_data[3] / 340.0) + 36.53;
    float GyroX = mpu_data[4] / 131.0;
    float GyroY = mpu_data[5] / 131.0;
    float GyroZ = mpu_data[6] / 131.0;

    // Store readings in circular buffer
    accXBuf[bufIndex] = AccX;
    accYBuf[bufIndex] = AccY;
    accZBuf[bufIndex] = AccZ;
    temperature[bufIndex] = Temp;
    gyroX[bufIndex] = GyroX;
    gyroY[bufIndex] = GyroY;
    gyroZ[bufIndex] = GyroZ;

    bufIndex = (bufIndex + 1) % FILTER_SIZE;

    // Compute averages
    values[0] = 0; values[1] = 0; values[1] = 0; values[1] = 0; values[1] = 0; values[1] = 0; values[1] = 0;
    for (int i = 0; i < FILTER_SIZE; i++)
    {
        values[0] += accXBuf[i];
        values[1] += accYBuf[i];
        values[2] += accZBuf[i];
        values[3] += temperature[i];
        values[4] += gyroX[i];
        values[5] += gyroY[i];
        values[6] += gyroZ[i];
    }
    values[0] /= FILTER_SIZE;
    values[1] /= FILTER_SIZE;
    values[2] /= FILTER_SIZE;
    values[3] /= FILTER_SIZE;
    values[4] /= FILTER_SIZE;
    values[5] /= FILTER_SIZE;
    values[6] /= FILTER_SIZE;
 

    return values;
}
void Send_gyro_values(float *values_to_send)
{
    Serial.print(values_to_send[0], 2);
    Serial.print(",");
    Serial.print(values_to_send[1], 2);
    Serial.print(",");
    Serial.print(values_to_send[2], 2);
    Serial.print(",");
    Serial.print((values_to_send[4] < 0 && values_to_send[4] > -1) ? 0 : values_to_send[4], 0);
    Serial.print(",");
    Serial.print((values_to_send[5] < 0 && values_to_send[5] > -1) ? 0 : values_to_send[5], 0);
    Serial.print(",");
    Serial.println((values_to_send[6] < 0 && values_to_send[6] > -1) ? 0 : values_to_send[6], 0);
}
