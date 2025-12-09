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
  int indexUp = analogRead(14);
  int indexLow = analogRead(27);
  int middleUp = analogRead(26);
  int middleLow = analogRead(25);
  int ringUp = analogRead(33);
  int ringLow = analogRead(32);
  int thumbFlex = analogRead(13);
  int pinkyFlex = analogRead(35);

  Serial.print(indexUp); Serial.print(",");
  Serial.print(indexLow); Serial.print(",");
  Serial.print(middleUp); Serial.print(",");
  Serial.print(middleLow); Serial.print(",");
  Serial.print(ringUp); Serial.print(",");
  Serial.print(ringLow); Serial.print(",");
  Serial.print(thumbFlex); Serial.print(",");
  Serial.println(pinkyFlex);

  delay(1000);
}