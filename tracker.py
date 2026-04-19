import time
import requests
from datetime import datetime

URL = "https://fortrx-server.duckdns.org"
INTERVAL = 2

def main():
    start_time = time.time()
    print(f"Starting ping at: {datetime.now()}")
    print(f"Target: {URL}\n")

    attempt = 0

    while True:
        attempt += 1
        elapsed = time.time() - start_time

        try:
            response = requests.get(URL, timeout=5)

            # If we got ANY response, it's success
            print("\nServer responded!")
            print(f"Time elapsed: {elapsed:.2f} seconds")
            print(f"Attempts: {attempt}")
            print(f"Status code: {response.status_code}")
            print("Response preview:")
            print(response.text[:200])  # first 200 chars
            break

        except requests.exceptions.RequestException as e:
            print(f"[{attempt}] Still down: {e} | {elapsed:.2f}s")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()