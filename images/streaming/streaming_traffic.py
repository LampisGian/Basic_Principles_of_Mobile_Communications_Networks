import time
import random
import requests
import os

def simulate_streaming():

    # Παίρνουμε το URL του server από τη μεταβλητή περιβάλλοντος ή χρησιμοποιούμε προεπιλεγμένο

    server_hostname = os.getenv("SERVER_HOSTNAME", "streaming_server")

    server_port = os.getenv("SERVER_PORT", "5001")

    server_url = f"http://{server_hostname}:{server_port}/upload"

    print(f"Streaming server URL: {server_url}", flush=True)

    while True:

        # κάθε αποστολή δεδομένων έχει μέγεθος που κυμαίνεται από 10MB έως το μέγιστο επιτρεπτό
        
        sleep_time = 2

        data_size_mb = 10  # Χρήση του ορίου από το περιβάλλον

        data = b"x" * int(data_size_mb * 1024 * 1024)  # Δημιουργία δεδομένων με το αντίστοιχο μέγεθος

        start_time = time.time()

        try:

            # Αποστολή δεδομένων στον server μέσω HTTP POST

            response = requests.post(server_url, data=data)

            end_time = time.time()

            if response.status_code == 200:

                total_time = (end_time - start_time) + sleep_time

                actual_bandwidth = data_size_mb / total_time
                
                print(f"Streaming: Sent {data_size_mb:.2f}MB in {total_time:.2f}s ({actual_bandwidth:.2f} MB/s)", flush=True)
           
            else:
               
                print(f"Streaming: Server error {response.status_code}", flush=True)

        except Exception as e:
           
            print(f"Streaming: Error - {e}", flush=True)

        # Καθυστέρηση ανάλογα με το bandwidth

        time.sleep(sleep_time) 

if __name__ == "__main__":
    simulate_streaming()
