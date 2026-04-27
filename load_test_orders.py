import asyncio
import statistics
import time

import httpx

TOTAL_REQUESTS = 1000
CONCURRENCY = 10
TIMEOUT = 60.0
BASE_URL = "http://127.0.0.1:8000"
ORDERS_URL = f"{BASE_URL}/orders"
HEALTH_URL = f"{BASE_URL}/health"

latencies: list[float] = []
failures = 0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return ordered[f]
    return ordered[f] + (ordered[c] - ordered[f]) * (k - f)


async def check_health(client: httpx.AsyncClient) -> None:
    response = await client.get(HEALTH_URL, timeout=TIMEOUT)
    response.raise_for_status()
    print(f"Health check OK: {response.status_code} - {response.text}")


async def create_order(
    client: httpx.AsyncClient,
    index: int,
    semaphore: asyncio.Semaphore,
) -> None:
    global failures

    payload = {
        "customer_name": f"Cliente {index}",
    }

    async with semaphore:
        start = time.perf_counter()
        try:
            response = await client.post(ORDERS_URL, json=payload, timeout=TIMEOUT)
            elapsed = (time.perf_counter() - start) * 1000

            if response.status_code in (200, 201):
                latencies.append(elapsed)
            else:
                failures += 1
                print(
                    f"Request {index} failed after {elapsed:.2f} ms: "
                    f"{response.status_code} - {response.text}"
                )
        except Exception as exc:
            failures += 1
            elapsed = (time.perf_counter() - start) * 1000
            print(
                f"Request {index} exception after {elapsed:.2f} ms: "
                f"{type(exc).__name__}: {exc!r}"
            )


async def main() -> None:
    limits = httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
    )
    timeout = httpx.Timeout(TIMEOUT)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        await check_health(client)

        semaphore = asyncio.Semaphore(CONCURRENCY)
        start_total = time.perf_counter()

        tasks = [
            create_order(client, index, semaphore)
            for index in range(TOTAL_REQUESTS)
        ]
        await asyncio.gather(*tasks)

        total_time = time.perf_counter() - start_total

    success_count = len(latencies)

    print("\n=== Load Test Result ===")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failures}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests/sec: {TOTAL_REQUESTS / total_time:.2f}")

    if latencies:
        print(f"Average latency: {statistics.mean(latencies):.2f} ms")
        print(f"Median latency: {statistics.median(latencies):.2f} ms")
        print(f"Min latency: {min(latencies):.2f} ms")
        print(f"Max latency: {max(latencies):.2f} ms")
        print(f"P95 latency: {percentile(latencies, 95):.2f} ms")
        print(f"P99 latency: {percentile(latencies, 99):.2f} ms")


if __name__ == "__main__":
    asyncio.run(main())
