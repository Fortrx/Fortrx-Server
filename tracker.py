import argparse
import sys
import time
from datetime import datetime

import requests


DEFAULT_URL = "https://fortrx-server.duckdns.org/"
DEFAULT_INTERVAL = 2.0
DEFAULT_TIMEOUT = 5.0
EXPECTED_STATUS = "Fortrx is running"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Poll the Fortrx server until it reports healthy."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Endpoint to poll. Default: {DEFAULT_URL}",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"Seconds to wait between attempts. Default: {DEFAULT_INTERVAL}",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Per-request timeout in seconds. Default: {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="Stop after this many attempts. Use 0 to retry forever.",
    )
    parser.add_argument(
        "--allow-any-200",
        action="store_true",
        help="Treat any HTTP 200 response as success.",
    )
    return parser.parse_args()


def is_healthy(response: requests.Response, allow_any_200: bool) -> tuple[bool, str]:
    if response.status_code != 200:
        return False, f"HTTP {response.status_code}"

    if allow_any_200:
        return True, "received HTTP 200"

    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        preview = response.text.strip().replace("\n", " ")[:120]
        return False, f"unexpected content type {content_type!r}, preview={preview!r}"

    try:
        payload = response.json()
    except ValueError as exc:
        return False, f"invalid JSON body: {exc}"

    status = payload.get("status")
    if status != EXPECTED_STATUS:
        return False, f"unexpected status payload: {payload!r}"

    return True, f"status={status!r}"


def main() -> int:
    args = parse_args()
    start_time = time.time()

    print(f"Starting health tracker at: {datetime.now().isoformat(sep=' ', timespec='seconds')}")
    print(f"Target: {args.url}")
    print(
        f"Interval: {args.interval}s | Timeout: {args.timeout}s | "
        f"Max attempts: {'infinite' if args.max_attempts == 0 else args.max_attempts}"
    )
    print()

    session = requests.Session()
    attempt = 0

    while True:
        attempt += 1
        elapsed = time.time() - start_time

        try:
            response = session.get(args.url, timeout=args.timeout)
            healthy, reason = is_healthy(response, allow_any_200=args.allow_any_200)

            if healthy:
                print("Server is healthy.")
                print(f"Time elapsed: {elapsed:.2f} seconds")
                print(f"Attempts: {attempt}")
                print(f"Status code: {response.status_code}")
                print(f"Validation: {reason}")
                return 0

            print(
                f"[{attempt}] Not ready yet: {reason} | "
                f"{elapsed:.2f}s"
            )
        except requests.exceptions.RequestException as exc:
            print(f"[{attempt}] Request failed: {exc} | {elapsed:.2f}s")

        if args.max_attempts and attempt >= args.max_attempts:
            print(f"Giving up after {attempt} attempts.")
            return 1

        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
