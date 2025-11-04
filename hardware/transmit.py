import socket
import time
import struct

PEER = "fd01:340b:74aa:e9bc:0:ff:fe00:fc11"
PORT = 6767

addrinfo = socket.getaddrinfo(PEER, None)[0]
sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
ttl_bin = struct.pack("@i", 2)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)


def lots():
    with open("allimg.tar.gz", "rb") as pn:
        img_bytes = pn.read()
        arr = bytearray(img_bytes)

        chunk_size = 1024
        chunks = []

        for i in range(0, len(arr), chunk_size):
            chunks.append(arr[i : i + chunk_size])

        strt = time.perf_counter()
        idx = 1

        for ch in chunks:
            four_byte_index = struct.pack("<i", idx)
            ch = bytearray(four_byte_index) + ch

            # input("Send next..")
            sock.sendto(bytes(ch), (PEER, PORT))

            print(f"Data: |{ch}| sent to {PEER}")
            print(f"Sent chunk {idx}/{len(chunks)}, size {len(ch)} bytes")
            print()

            idx += 1
            time.sleep(0.2)

        time.sleep(0.5)
        sock.sendto(bytes(b"EOF"), (PEER, PORT))

        print(f"Finished in: {time.perf_counter() - strt} s")
        print(f"Sent {len(chunks)} chunks")
        print(f"Sent {len(chunks) * chunk_size} bytes")


def notmuch():
    while True:
        input("Press Enter...")
        sock.sendto(b"Hello Thread peer!", (PEER, PORT))
        print("Sent message to", PEER)


if __name__ == "__main__":
    running = input("Which?: ")
    # if running == "lots":
    lots()
    # else:
        # notmuch()
