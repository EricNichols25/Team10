#include <IRremote.h>
const int IR_PIN = 3;

IRsend irsend(IR_PIN);

void setup() {

  irsend.begin(IR_PIN);

  Serial.begin(115200);
  Serial.setTimeout(.5);

}

int x;

void loop() {

  while (!Serial.available());

  int value = Serial.read();


  irsend.sendNEC(0x0168, value, 0);
  Serial.println(value, HEX);

  delay(50);

  
}

// const char* message[] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x0A, 0x2F, 0xBA, 0xFF};

// for (int i = 0; i < 10; i++) {
//   irsend.sendNEC(0x0168, message[i], 0);
  
//   delay(50);
  
// }

// irsend.sendNEC(0x00, HEX);

// delay(1000);