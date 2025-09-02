#include <IRremote.h>
const int RECV_PIN = 11;

IRsend irsend(IR_PIN);

void setup() {

  irsend.begin(IR_PIN);

}

void loop() {
  uint32_t tvPowerOffCode;
  irsend.sendNEC(0xE0E019E6, 32);
  irsend.sendNEC(0x02, 0x34, 3);

  delay(50);
}
