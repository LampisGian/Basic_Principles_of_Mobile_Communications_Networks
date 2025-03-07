import socket

from datetime import datetime

def run_server():

    server_address = ('', 8080)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(server_address)

    print("Server is listening on port 8080", flush=True)

    MAX_PACKET_SIZE = 65507  # Μέγιστο μέγεθος δεδομένων σε UDP

    while True:

        data, address = sock.recvfrom(MAX_PACKET_SIZE)

        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

        print(f"{timestamp} - Received {len(data)} bytes from {address}", flush=True)
        
        if data:

            sent = sock.sendto(data, address)

            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]

            print(f"{timestamp} - Sent {sent} bytes back to {address}", flush=True)

if __name__ == "__main__":

    run_server()
