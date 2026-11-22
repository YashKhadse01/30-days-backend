# Day 30 — Performance Testing Report

## Objective

Perform a controlled, low-volume HTTP smoke test against
the deployed FastAPI application.

## Target

Endpoint:

https://capstone-core-api.onrender.com/health

Hosting: Render Free, Singapore.

The Render instance was warmed before measurement.

## Test Configuration

| Parameter | Value |
|---|---|
| HTTP method | GET |
| Endpoint | /health |
| Total requests | 20 |
| Concurrency | 2 |
| Expected status | HTTP 200 |
| Test client | Python ThreadPoolExecutor |

## Measured Results

| Metric | Result |
|---|---|
| Successful requests | 20/20 |
| Failed requests | 0 |
| Average latency | 286.03 ms |
| P95 latency | 533.52 ms |
| Total elapsed time | 2.92 s |
| Throughput | 6.84 requests/second |

## Interpretation

All 20 requests completed successfully.

The results show that the warmed HTTPS health endpoint
handled the small concurrent request batch without
observed failures.

The measurements are specific to this test run and
should not be treated as stable service guarantees.

## Limitations

- Only 20 requests were sent.
- Concurrency was limited to two clients.
- Only the lightweight `/health` endpoint was tested.
- Authenticated API and database-intensive performance
  were not benchmarked.
- Cold-start behavior was not measured.
- No soak, stress, spike, or maximum-capacity test was run.
- Render Free performance may vary with shared resources.

## Conclusion

The controlled smoke test passed.

This establishes basic endpoint responsiveness during
the measurement window, not production capacity.
