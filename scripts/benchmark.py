from __future__ import annotations
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def simulated_io_job(duration_ms: int = 50) -> int:
    time.sleep(duration_ms / 1000)
    return duration_ms


def run_sequential(count: int, duration_ms: int) -> float:
    start = time.perf_counter()
    for _ in range(count):
        simulated_io_job(duration_ms)
    return time.perf_counter() - start


def run_concurrent(count: int, duration_ms: int, total_threads: int) -> tuple[float, list[float]]:
    start = time.perf_counter()
    latencies = []
    with ThreadPoolExecutor(max_workers=total_threads) as pool:
        futures = []
        for _ in range(count):
            submitted = time.perf_counter()
            future = pool.submit(simulated_io_job, duration_ms)
            futures.append((future, submitted))
        for future, submitted in futures:
            future.result()
            latencies.append((time.perf_counter() - submitted) * 1000)
    return time.perf_counter() - start, latencies


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * p))))
    return ordered[index]


def main() -> None:
    count = 60
    duration_ms = 50
    sequential = run_sequential(count, duration_ms)
    scenarios = []
    for nodes, threads_per_node in [(1, 2), (2, 2), (3, 4)]:
        total_threads = nodes * threads_per_node
        elapsed, latencies = run_concurrent(count, duration_ms, total_threads)
        scenarios.append({
            "nodes": nodes,
            "threads_per_node": threads_per_node,
            "total_threads": total_threads,
            "jobs": count,
            "elapsed_s": round(elapsed, 3),
            "throughput_jobs_s": round(count / elapsed, 2),
            "p50_latency_ms": round(statistics.median(latencies), 2),
            "p95_latency_ms": round(percentile(latencies, 0.95), 2),
            "speedup_vs_sequential": round(sequential / elapsed, 2),
        })
    output = {"sequential_elapsed_s": round(sequential, 3), "scenarios": scenarios}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
