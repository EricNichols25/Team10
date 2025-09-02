#include <IRemote.h>
const int RECV_PIN = 11;

IRrecv irrecv(RECV_PIN);

void setup() {

  Serial.begin(9600);
  irrecv.enableIRIn();
  Serial.println("IR Receiver Enabled");

}

void loop() {
  if (irrecv.decode()) {
    // Serial.println(IrReceiver.decodedIRData.decodedRawData);
    unsigned long sCommand = IrReceiver.decodedIRData.command;
    unsigned long sAddress = IrReceiver.decodedIRData.address;

    if ((IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT)) {
      IrReceiver.resume();
      return;
    }

    Serial.print("address = ");
    Serial.print(sAddress, HEX);
    Serial.print("    decoded command = ");
    Serial.print(sCommand, HEX);
    Serial.println();
  }
}