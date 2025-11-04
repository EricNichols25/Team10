import socket
import struct
from time import perf_counter
from subprocess import call

UDP_PORT = 6767
INTERFACE = "wpan0"
GROUPIP="ff03::2"

def initialize_udp():
    # First lets print out the state
    print('Initializing UDP')
    print('Checking otbr state')
    call('docker exec -it otbr ot-ctl state', shell=True)
    
    print('Enabling UDP')
    call('docker exec -it otbr ot-ctl udp open', shell=True)

    print('Binding port')
    call('docker exec -it otbr ot-ctl udp bind :: 6767', shell=True)


def start_listener():


    addrinfo = socket.getaddrinfo(GROUPIP, None)[0]
    # Create IPv6 UDP socket
    sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', UDP_PORT))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    mreq = group_bin + struct.pack('@I', 0)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)


    print("Listening on wpan0:", UDP_PORT)
    start = 0
    missed = []
    with open('test.tar.gz', 'wb') as f:
        once = False

        prev = 0
        
        while True:
            data, addr = sock.recvfrom(1028)
            
            # If EOF, just break out
            if data == b'EOF':
                break
            
            if not once:
                start = perf_counter()
                once = True

            idx = int.from_bytes(data[:4], 'little')
            parsed = data[4:]
            
            if idx - prev > 1 and prev != 0:
                for miss in range(prev + 1, idx):
                    missed.append(miss)
                    print(f"Missed packet {miss}")

            print(f"Received {idx}: {len(parsed)} bytes")

            f.write(parsed)
            prev = idx

        f.close()

    print(f"Finished in {perf_counter() - start} seconds")

if __name__ == '__main__':
    initialize_udp()
