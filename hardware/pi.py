import os
import serial
import time
import hashlib

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
CHUNK_SIZE = 2048
DELAY = 0.01 # Seconds

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


def send_header(ser, header):
    # print("\nSending header:", header, bytes(headers[header].encode("utf-8") + b"\n"))
    ser.write(bytes(headers[header].encode("utf-8") + b"\n"))

    # Wait for acknowledgment from the receiver
    wait_for_ack(ser)
    time.sleep(DELAY)
    

def wait_for_ack(ser, timeout=None):
    ack_wait = time.perf_counter()

    while True:
        if timeout and time.perf_counter() - ack_wait > timeout:
            print("Timeout waiting for ACK.")
            return False

        if ser.in_waiting > 0:
            ack = ser.readline()  # Wait for acknowledgment

            if ack.strip() != headers["ack"].encode("utf-8"):
                print("Did not receive proper ACK. Aborting transmission.")
                return False

            return True

        time.sleep(DELAY)


def handshake(ser):
    print("\nInitiating handshake...")
    
    while True:
        print("Sending handshake signal...")
        ser.write(b"SHAKE\n")
        
        # We wait for 2 seconds for an ACK
        if wait_for_ack(ser, timeout=2):
            print("Handshake successful!")
            return True
    

def send_packet(ser, packet):
    send_header(ser, "data")

    print(f"\nSending packet of size {len(packet)} bytes")
    ser.write(packet + b"|EOP|")

    time.sleep(DELAY)
    

def send_file_over_serial(ser, filename):
    with open(filename, "rb") as f:
        img_bytes = f.read()
        file_size = f.seek(0, 2)
        f.seek(0)

        
        file_hash = hash_value(img_bytes)
        
        send_header(ser, "meta")
        
        meta_pack = (
            f"{os.path.basename(filename)}|{file_size}|{file_hash.hex()}\n".encode(
                "utf-8"
            )
        )
        
        # Send metadata wait for a delay
        # Then wait for ACK
        # print()
        # print("Sending metadata:", meta_pack)
        ser.write(meta_pack)

        time.sleep(DELAY)
        wait_for_ack(ser)
        

        # Make the file into chunks
        chunks = [
            img_bytes[i : i + CHUNK_SIZE]
            for i in range(0, len(img_bytes), CHUNK_SIZE)
        ]

        start = time.perf_counter()

        print(f"\nSending file: {filename}")
        print(f"File size: {len(img_bytes)} bytes")
        print(f"Number of chunks: {len(chunks)}")
        print(f"MD5 Digest: {file_hash.hex()}")

        print("\nStarting transmission...")
        
        for i, chunk in enumerate(chunks):
            pack_hash = hash_value(chunk)

            while True:
                print(f"\nSending chunk {i + 1}/{len(chunks)}...")
                send_packet(ser, chunk)

                # Wait for ACK of packet receipt
                wait_for_ack(ser)
                    
                # Then we wait for verification of data integrity
                print("\nVerifying data integrity...")
                send_header(ser, "hash")
                ser.write(pack_hash.hex().encode("utf-8") + b"\n")
                
                ser.flush()
                ret = ser.readline() # Wait for integrity verification response
                
                # If it's not OK, we resend the chunk
                if ret != b"OK\n":
                    print("Data integrity check failed. Resending chunk...")
                    continue
                
                print(f"Sent chunk {i + 1}/{len(chunks)} successfully.")
                ser.flush()
                break # If it's successful, break the loop and go to next chunk
        
        ser.flush()
        end = time.perf_counter()

        send_header(ser, "eof")  # End of file

        print()
        print("File transmission completed.")
        print(f"Total time taken: {end - start:.2f} seconds")


def transmission():
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        time.sleep(2)  # Wait for the serial connection to initialize

        handshake(ser)

        filename = input("Enter the path to your file: ") or "detected-images.tar.gz"
        
        send_file_over_serial(ser, filename)


if __name__ == "__main__":
    transmission()