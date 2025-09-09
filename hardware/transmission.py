import serial
import time

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)

cw = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0xFF]

def write_read(x):
    arduino.write(serial.to_bytes(cw))
    time.sleep(0.0005)

while True:
    num = input("Enter a hex value: ")
    write_read(bytes.fromhex(num))