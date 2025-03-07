import socket
import random
import time

def simulate_gaming():

    server_address = ("gaming_server_container", 8080)

    packet_size = 50 * 1024  # Μέγεθος πακέτου (10 KB)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:

            # Αποστολή δεδομένων

            sock.sendto(b'x' * packet_size, server_address)

            print(f"Sent {packet_size / 1024:.2f} KB to {server_address}", flush=True)

            # Καθυστέρηση πριν την επόμενη αποστολή (τυχαία, από 50ms έως 200ms)
            time.sleep(random.uniform(0.05, 0.2))

    finally:
        sock.close()

if __name__ == "__main__":
    simulate_gaming()
