#include <Wire.h>
#include <WiFi.h>
#include <Adafruit_MPU6050.h>
#include <IPAddress.h>
#include <Adafruit_Sensor.h>
#include <WebSocketsClient.h>

#define SDA_PIN 21
#define SCL_PIN 22
#define PI 3.14159265359  // More precise PI value

int smoothPitch = 0, smoothRoll = 0, smoothYaw = 0;
const float filterStrength = 0.08; 

// const char* ssid = "Robotics club";
// const char* password = "roboticsclub";
float angleX = 0, angleY = 0, angleZ = 0;

// IPAddress myIP = IPAddress(192, 168, 30, 125);
// const uint16_t websocketPort = 3000;
unsigned long lastTime;
// WebSocketsClient webSocket;

Adafruit_MPU6050 mpu;

// Calibration offsets
float accelOffsetX = 0, accelOffsetY = 0, accelOffsetZ = 0;
float gyroOffsetX = 0, gyroOffsetY = 0, gyroOffsetZ = 0;

// Complementary filter constants
const float alpha = 0.98;  // Gyro dominance factor
const float beta = 0.02;   // Accel dominance factor

void setup() {
    Serial.begin(115200);
    
//     WiFi.begin(ssid, password);
//     while (WiFi.status() != WL_CONNECTED) {
//         delay(1000);
//         Serial.println("Connecting to WiFi...");
//     }
//     Serial.println("Connected to WiFi!");

//    webSocket.begin(myIP, websocketPort, "/");

    Wire.begin(SDA_PIN, SCL_PIN);
    
    Serial.println("Initializing MPU6050...");
    if (!mpu.begin()) {
        Serial.println("MPU6050 not detected. Check connections!");
        while (1);
    }
    Serial.println("MPU6050 initialized successfully.");
    
    // Set sensor ranges for better precision
    mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
    mpu.setGyroRange(MPU6050_RANGE_250_DEG);
    
    calibrateMPU();
    lastTime = millis();
}

void loop() {
    // webSocket.loop();

    unsigned long currentTime = millis();
    float deltaTime = (currentTime - lastTime) / 1000.0; // Convert to seconds
    lastTime = currentTime;

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Apply calibration offsets (ONCE)
    float ax = a.acceleration.x - accelOffsetX;
    float ay = a.acceleration.y - accelOffsetY;
    float az = a.acceleration.z - accelOffsetZ;
    
    float gx = g.gyro.x - gyroOffsetX;
    float gy = g.gyro.y - gyroOffsetY;
    float gz = g.gyro.z - gyroOffsetZ;

    // Calculate angles from accelerometer (in degrees)
    float accelPitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
    float accelRoll = atan2(ay, az) * 180.0 / PI;
    
    // Integrate gyro data (in degrees)
    angleX += gx * deltaTime * (180.0 / PI);  // Roll
    angleY += gy * deltaTime * (180.0 / PI);  // Pitch
    angleZ += gz * deltaTime * (180.0 / PI);  // Yaw
    
    // Apply complementary filter
    angleX = alpha * angleX + beta * accelRoll;
    angleY = alpha * angleY + beta * accelPitch;

  smoothPitch = smoothPitch * (1 - filterStrength) + angleY * filterStrength;
  smoothRoll = smoothRoll * (1 - filterStrength) + angleX * filterStrength;
  smoothYaw = smoothYaw * (1 - filterStrength) + angleZ * filterStrength;
    
    // Yaw will still drift - consider adding magnetometer for yaw correction
    
    // Print the results
    Serial.print("Pitch: ");
    Serial.print(smoothPitch);
    Serial.print("°, Roll: ");
    Serial.print(smoothRoll);
    Serial.print("°, Yaw: ");
    Serial.print(smoothYaw);
    Serial.println("°");

    // Create JSON string
    // String json = "{\"roll\":" + String(smoothRoll) + ",\"pitch\":" + String(smoothPitch) + ",\"yaw\":" + String(smoothYaw) + "}";
    
    // Send data to the WebSocket server
    // webSocket.sendTXT(json);
    
    delay(20);  // ~50Hz update rate
}

void calibrateMPU() {
    Serial.println("Place MPU6050 flat and stable, then send 'c' to calibrate...");
    while (!Serial.available() || Serial.read() != 'c') delay(10);

    float accelXSum = 0, accelYSum = 0, accelZSum = 0;
    float gyroXSum = 0, gyroYSum = 0, gyroZSum = 0;
    const int samples = 1000;

    for (int i = 0; i < samples; i++) {
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        
        accelXSum += a.acceleration.x;
        accelYSum += a.acceleration.y;
        accelZSum += a.acceleration.z - 9.81; // Remove gravity for Z
        
        gyroXSum += g.gyro.x;
        gyroYSum += g.gyro.y;
        gyroZSum += g.gyro.z;
        
        delay(5);
    }

    // Compute averages
    accelOffsetX = accelXSum / samples;
    accelOffsetY = accelYSum / samples;
    accelOffsetZ = accelZSum / samples;
    
    gyroOffsetX = gyroXSum / samples;
    gyroOffsetY = gyroYSum / samples;
    gyroOffsetZ = gyroZSum / samples;

    Serial.println("Calibration complete!");
    Serial.print("Accel Offsets (X,Y,Z): ");
    Serial.print(accelOffsetX, 6); Serial.print(", ");
    Serial.print(accelOffsetY, 6); Serial.print(", ");
    Serial.println(accelOffsetZ, 6);
    
    Serial.print("Gyro Offsets (X,Y,Z): ");
    Serial.print(gyroOffsetX, 6); Serial.print(", ");
    Serial.print(gyroOffsetY, 6); Serial.print(", ");
    Serial.println(gyroOffsetZ, 6);
}