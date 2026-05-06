#include<Arduino.h>
void setup() {
  Serial.begin(9600);
 pinMode(14, INPUT);
 pinMode(27, INPUT);
 pinMode(26, INPUT);
 pinMode(25, INPUT);
 pinMode(33, INPUT);
 pinMode(32, INPUT);
 pinMode(13, INPUT);
 Serial.begin(115200);
}
void loop() {
  int indexUp = analogRead(32);
  int indexLow = analogRead(33);
  int middleUp = analogRead(25);
  int middleLow = analogRead(26);
  int ringUp = analogRead(27);
  int ringLow = analogRead(14);
  int thumbFlex = analogRead(35);
  int pinkyFlex = analogRead(13);

  // Serial.print(indexUp); Serial.print(",");
  // Serial.print(indexLow); Serial.print(",");
  // Serial.print(middleUp); Serial.print(",");
  // Serial.print(middleLow); Serial.print(",");
  // Serial.print(ringUp); Serial.print(",");
  // Serial.print(ringLow); Serial.print(",");
  Serial.print(thumbFlex); Serial.print(",");
  Serial.println(pinkyFlex);

  delay(500);
}