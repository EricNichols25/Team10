#include <IRremote.h>
const int RECV_PIN = 11;

IRrecv irrecv(RECV_PIN);

void setup() {

  Serial.begin(115200);
  irrecv.enableIRIn();
  Serial.println("IR Receiver Enabled");

}

unsigned long data[] = {};
int i = 0;

void loop() {
  
  if (irrecv.decode()) {
    // Serial.println(IrReceiver.decodedIRData.decodedRawData);
    // unsigned long sCommand = IrReceiver.decodedIRData.command;
    // unsigned long sAddress = IrReceiver.decodedIRData.address;

    // if ((IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT)) {
    //   IrReceiver.resume();
    //   return;
    // }
    // Serial.print(irrecv.decodedIRData.command, HEX);
    // Serial.print(" - ");
    // Serial.println(irrecv.decodedIRData.decodedRawData, HEX);

    // unsigned long command = irrecv.decodedIRData.command;
    // char receivedChar = (char)(irrecv.decodedIRData.command);

    // Serial.print("Received char: ");
    // Serial.print(command);
    // Serial.print(" - ");
    // Serial.println(receivedChar);
    data[i++] = irrecv.decodedIRData.command;
    Serial.println(irrecv.decodedIRData.command, HEX);
    Serial.println(irrecv.decodedIRData.decodedRawData, HEX);
    IrReceiver.resume();

  }

  delay(50);

  // if (i == 3) {
  //   Serial.println(data[0], HEX);
  //   Serial.println(data[1], HEX);
  //   Serial.println(data[2], HEX);
  //   Serial.println(data[3], HEX);
  //   Serial.println(data[4], HEX);
  //   i = 0;
  // }
}