import asyncio
import aiohttp
import time
import statistics
import uuid
import numpy as np
from dataclasses import dataclass

@dataclass
class Result:
    success: bool
    status_code: int | None
    queue_delay: float
    request_latency: float
    total_latency: float
    error: str | None = None


async def send_generate_request(session, url, prompt) -> tuple[bool, int | None, float, str | None]:
    start = time.perf_counter()
    try:
        async with session.post(url, json={"prompt": prompt}) as resp:
            await resp.read()
            latency = time.perf_counter() - start
            return True, resp.status, latency, None
    except Exception as e:
        latency = time.perf_counter() - start
        return False, None, latency, str(e)


async def benchmark_generate(
    num_requests: int,
    concurrency: int,
    base_url: str,
    warmup_requests: int = 10,
):
    url = f"{base_url}/generate"
    semaphore = asyncio.Semaphore(concurrency)

    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=concurrency)

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector
    ) as session:

        # -------- warm up --------
        print(f"Warming up with {warmup_requests} requests...")
        for _ in range(warmup_requests):
            await send_generate_request(session, url, "warmup")

        print("Warmup done.\n")

        async def limited_request(i: int) -> Result:
            created_at = time.perf_counter()

            async with semaphore:
                acquired_at = time.perf_counter()
                ok, status, req_latency, err = await send_generate_request(
                    session,
                    url,
                    f"benchmark-{uuid.uuid4()}-{i}"
                )
                finished_at = time.perf_counter()

            return Result(
                success=ok,
                status_code=status,
                queue_delay=acquired_at - created_at,
                request_latency=req_latency,
                total_latency=finished_at - created_at,
                error=err
            )

        tasks = [
            asyncio.create_task(limited_request(i))
            for i in range(num_requests)
        ]

        results: list[Result] = await asyncio.gather(*tasks)

    # -------- analysis --------
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    if not successes:
        print("❌ No successful requests")
        return

    def stats(values):
        return {
            "min": min(values),
            "avg": statistics.mean(values),
            "p50": np.percentile(values, 50),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99),
            "max": max(values),
        }

    queue_stats = stats([r.queue_delay for r in successes])
    req_stats = stats([r.request_latency for r in successes])
    total_stats = stats([r.total_latency for r in successes])

    print("========== Benchmark Result ==========")
    print(f"Total requests: {num_requests}")
    print(f"Concurrency: {concurrency}")
    print(f"Success: {len(successes)}")
    print(f"Failed: {len(failures)}\n")

    def print_stats(title, s):
        print(title)
        print(f"  min : {s['min']*1000:.2f} ms")
        print(f"  avg : {s['avg']*1000:.2f} ms")
        print(f"  p50 : {s['p50']*1000:.2f} ms")
        print(f"  p95 : {s['p95']*1000:.2f} ms")
        print(f"  p99 : {s['p99']*1000:.2f} ms")
        print(f"  max : {s['max']*1000:.2f} ms\n")

    print_stats("Queue delay (client-side semaphore):", queue_stats)
    print_stats("Request latency (network + server):", req_stats)
    print_stats("End-to-end latency:", total_stats)

    if failures:
        print("Sample failures:")
        for f in failures[:5]:
            print(f"  error={f.error}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python benchmark.py <num_requests> <concurrency> <base_url>")
        sys.exit(1)

    asyncio.run(
        benchmark_generate(
            num_requests=int(sys.argv[1]),
            concurrency=int(sys.argv[2]),
            base_url=sys.argv[3],
        )
    )
