
import time
import requests
import random

def simulate_browsing():
    print("Starting realistic browsing simulation...", flush=True)

    urls = [
        "https://jsonplaceholder.typicode.com/posts",
        "https://jsonplaceholder.typicode.com/comments",
        "https://jsonplaceholder.typicode.com/albums",
        "https://jsonplaceholder.typicode.com/photos",
        "https://jsonplaceholder.typicode.com/users"
    ]

    while True:
        try:

            url = random.choice(urls)

            print(f"Browsing: Sending request to {url}...", flush=True)

            response = requests.get(url, timeout=5)  # Προσθέστε timeout

            latency = response.elapsed.total_seconds() * 1000

            content_size = len(response.content)

            print(f"Browsing: Received {content_size} bytes with latency {latency:.2f}ms", flush=True)

        except requests.exceptions.Timeout:
            print("Browsing: Request timed out. Retrying...", flush=True)
        except requests.exceptions.ConnectionError:
            print("Browsing: Connection error. Retrying after 1 second...", flush=True)
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Browsing: General error - {e}. Retrying...", flush=True)
        time.sleep(random.uniform(0.5, 2))

if __name__ == "__main__":
    
    simulate_browsing()
