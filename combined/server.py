# This is the receiver script for serial data transmission. It listens on a specified serial port,
# waits for incoming data packets, verifies their integrity using MD

import os
import serial
import time
import hashlib

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
CHUNK_SIZE = 250
DELAY = 0.05 # Seconds
MAX_RETRIES = 5

hasher = hashlib.md5()
headers = {
    "meta": "META".encode("utf-8").hex(),
    "data": "DATA".encode("utf-8").hex(),
    "hash": "HASH".encode("utf-8").hex(),
    "eof": "EOF".encode("utf-8").hex(),
    "ack": "ACK".encode("utf-8").hex(),
}


def hash_value(data):
    hasher = hashlib.md5()
    hasher.update(data)

    return hasher.digest()



def check_header(recv, expected):
    return recv == bytes(headers[expected].encode() + b'\n')


def wait_for_header(ser):
    # print()
    # print("Waiting for header...")

    while True:
        if ser.in_waiting > 0:
            recv = ser.readline()
            # print("Received header:", recv)

            for key, value in headers.items():
                if check_header(recv, key):
                    # print("Header matched:", key)
                    # print("Sending acknowledgment for header...")

                    # Send acknowledgment
                    send_ack(ser)

                    print()
                    return key

        time.sleep(DELAY)


def send_ack(ser):
    print()
    print("Sending ACK")
    ser.write(bytes(headers["ack"].encode("utf-8") + b"\n"))

    # Just hold until ack
    # ser.readline()
    
    
    time.sleep(DELAY)

# Handshake for receiver
def handshake(ser):
    print()
    print("Initiating handshake...")
    print("Waiting for handshake signal...")
    
    while True:
        if ser.in_waiting > 0:
            signal = ser.readline()  # Wait for handshake signal
            ser.flush()
            print("Received handshake signal:", signal)
            print()

            if signal.strip() == b"SHAKE":
                print("Handshake signal received. Sending ACK...")
                send_ack(ser)  # Send acknowledgment

                ack = ser.readline()

                print('Verifying ack')
                print('DEBUG', ack)
                if ack.strip() != headers["ack"].encode("utf-8"):
                    print("Did not receive proper handshake ack. Retrying...")
                    continue

                print("Handshake complete.")
                print()
                return
            
            else:
                print("Invalid handshake signal. Ignoring...")

        time.sleep(0.1)
        

def wait_for_metadata(ser):
    print()
    print("Waiting for metadata...")

    metadata = {}

    while True:
        if ser.in_waiting > 0:
            recv = ser.readline()

            meta = bytes(recv).split(b"|")

            metadata["filename"] = meta[0].decode()
            metadata["filesize"] = int(meta[1].decode())
            metadata["hash"] = meta[2].decode()

            print(f"Filename: {metadata['filename']}, Filesize: {metadata['filesize']} bytes")
            print(f"Hash: {metadata['hash']}")

            send_ack(ser)

            break

    return metadata


def verify_integrity(data, expected_hash):
    computed_hash = hash_value(data).hex()

    print()
    # print(f"Verifying data integrity...")
    # print(f"Expected Hash: {expected_hash}")
    # print(f"Computed Hash: {computed_hash}")

    return computed_hash == expected_hash

def recv_packet(ser):
    print()
    ser.flush()
    data = bytearray(b"")
    
    while True:
        if ser.in_waiting > 0:
            chunk = ser.read_until(b"|EOP|") # Read until end of packet marker

            # print(f"Received data chunk fragment of size {len(chunk)} bytes")
            # data.extend(chunk.rstrip(b"\n"))  # Remove newline character

            # if check_header(chunk, "eop"):
            #     print("End of packet received. Sending ACK...")
            #     send_ack(ser)

            #     ser.flush()
            #     return data
            
            return chunk[:-5] # Remove end of packet marker

        time.sleep(DELAY)
    

def transmission():
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        print(f"Listening on {PORT} at {BAUDRATE} baud...")
        
        # Perform handshake
        handshake(ser)
        
        # Variables
        metadata = {}
        constructed = bytearray(b"")
        filename = ""

        chunk = b""
        num = 1

        # Start main loop
        print()
        print("Starting main loop...")
        while True:
            header = wait_for_header(ser)

            if header == "meta":
                metadata = wait_for_metadata(ser)

            elif header == "data":
                chunk = recv_packet(ser)
                print(f"Received data chunk of size {len(chunk)} bytes. Num {num}")
                num += 1

                send_ack(ser)
            
            elif header == "hash":
                expected_hash = ser.readline().decode().strip()

                if verify_integrity(bytes(chunk), expected_hash):
                    print("Data integrity verified successfully.")

                    ser.write(b"OK\n")
                    ser.flush()

                    # Append chunk to constructed data
                    constructed += chunk
                else:
                    print("Data integrity verification failed.")
                    
                    ser.write(b"FAIL\n")
                    ser.flush()

                # Clear chunk after checking hash regardless
                chunk = b""

            elif header == "eof":
                print("End of file received. Transmission complete.")
                break
    

        ser.flush()

        print()
        print("Final Data Received:")
        print(constructed)
        print()
        print(f"Total Data Length: {len(constructed)} bytes")
        
        print("Expected Hash:", metadata['hash'])
        computed_hash = hash_value(constructed).hex()
        print("Computed Hash:", computed_hash)
        
        with open(metadata['filename'], "wb") as f:
            f.write(constructed)
            f.flush()

        print(f"Data written to file: {metadata['filename']}")