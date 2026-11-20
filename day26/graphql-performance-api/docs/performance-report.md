# Day 26 — GraphQL API Performance Report

**Project:** GraphQL Performance API  
**Date:** 20 November 2026  
**Technology:** Python 3.12, FastAPI, Strawberry GraphQL, DataLoader, Locust, Prometheus

## 1. Executive Summary

This report evaluates the performance of a Strawberry GraphQL API integrated with FastAPI.

The project implements GraphQL queries, authenticated mutations, nested project resolvers, DataLoader batching, automated testing, and Prometheus HTTP metrics.

Performance testing was conducted using Locust with 10 simulated users and a 60-second workload.

**Key findings:**

- Baseline: 382 requests, zero failures.
- Repeat run: 384 requests, zero failures.
- Average aggregated latency decreased from 7.60 ms to 6.90 ms between runs.
- P95 aggregated latency decreased from 14 ms to 13 ms.
- DataLoader combined three project lookup requests into one batch containing two unique IDs.
- Direct dictionary lookup was faster than DataLoader in the standalone in-memory benchmark.

The Locust runs used the same DataLoader-enabled implementation. Their differences represent observed run-to-run variation, not a verified optimization.

## 2. Performance Testing Objectives

The objectives were to:

1. Measure API response latency and throughput.
2. Check reliability under concurrent requests.
3. Verify DataLoader batching and caching.
4. Compare direct project lookup with batched lookup.
5. Expose HTTP metrics through Prometheus instrumentation.
6. Establish reproducible baseline measurements for future improvements.

## 3. Test Environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Python | 3.12 |
| API framework | FastAPI |
| GraphQL library | Strawberry GraphQL |
| Dependency manager | uv |
| Load-testing tool | Locust |
| Monitoring | Prometheus FastAPI Instrumentator |
| Application host | 127.0.0.1:8001 |
| Data storage | In-memory Python collections |

The benchmark was performed locally. No external database, production deployment, or distributed infrastructure was included.

## 4. Locust Workload

Both Locust runs used the following configuration:

| Parameter | Value |
|---|---|
| Simulated users | 10 |
| Spawn rate | 2 users/second |
| Duration | 60 seconds |
| GraphQL endpoint | POST /graphql |
| Health endpoint | GET /health |
| Task weighting | GraphQL 4, health 1 |
| Wait time | Random 1–2 seconds |

The GraphQL request retrieved tasks and their associated projects.

### Baseline command

```powershell
uv run locust -f .\performance\locustfile.py --headless --host http://127.0.0.1:8001 --users 10 --spawn-rate 2 --run-time 60s --csv .\performance\baseline
```

### Repeat command

```powershell
uv run locust -f .\performance\locustfile.py --headless --host http://127.0.0.1:8001 --users 10 --spawn-rate 2 --run-time 60s --csv .\performance\repeat
```

## 5. Baseline Performance Results

| Metric | GraphQL | Health | Aggregated |
|---|---:|---:|---:|
| Requests | 297 | 85 | 382 |
| Failures | 0 | 0 | 0 |
| Average latency | 8.49 ms | 4.49 ms | 7.60 ms |
| Median latency | 6 ms | 3 ms | 5 ms |
| P95 latency | 16 ms | 8 ms | 14 ms |
| P99 latency | 71 ms | 70 ms | 70 ms |
| Maximum latency | 99.91 ms | 69.94 ms | 99.91 ms |
| Throughput | 5.09 req/s | 1.46 req/s | 6.55 req/s |

All requests completed without recorded failures.

## 6. Repeat Performance Results

| Metric | GraphQL | Health | Aggregated |
|---|---:|---:|---:|
| Requests | 317 | 67 | 384 |
| Failures | 0 | 0 | 0 |
| Average latency | 7.73 ms | 2.95 ms | 6.90 ms |
| Median latency | 5 ms | 3 ms | 5 ms |
| P95 latency | 15 ms | 4 ms | 13 ms |
| P99 latency | 50 ms | 7 ms | 50 ms |
| Maximum latency | 167.02 ms | 7.19 ms | 167.02 ms |
| Throughput | 5.44 req/s | 1.15 req/s | 6.59 req/s |

The second run also recorded zero failures.

## 7. Baseline vs Repeat Comparison

| Metric | Baseline | Repeat | Observation |
|---|---:|---:|---|
| Total requests | 382 | 384 | +2 requests |
| Average latency | 7.60 ms | 6.90 ms | Approximately 9.2% lower |
| P95 latency | 14 ms | 13 ms | Approximately 7.1% lower |
| Throughput | 6.55 req/s | 6.59 req/s | Approximately 0.7% higher |
| Failure rate | 0% | 0% | Unchanged |
| Maximum latency | 99.91 ms | 167.02 ms | Higher in repeat run |

### Interpretation

The average and P95 latencies were slightly lower during the repeat run, while the maximum latency increased.

Because no application optimization was introduced between runs, these differences cannot be attributed to a specific performance improvement.

The endpoint request mix also differed slightly between runs.

**Conclusion:** The measurements establish repeatability under a small local workload, not a demonstrated before/after optimization.

## 8. DataLoader Comparison

The standalone benchmark used project IDs:

```text
[1, 1, 2]
```

Three tasks requested project information, but only two unique project IDs were involved.

### Loading operations

| Metric | Direct lookup | DataLoader |
|---|---:|---:|
| Operations per iteration | 3 dictionary lookups | 1 batch invocation |
| Iterations | 1,000 | 1,000 |
| Total operations | 3,000 lookups | 1,000 batch invocations |
| Total benchmark time | 0.734 ms | 56.692 ms |

Both implementations returned equivalent project information.

### Interpretation

DataLoader successfully combined repeated project IDs into one batch and reused cached values.

However, direct dictionary access was faster because it avoids DataLoader's asynchronous scheduling and batching overhead.

The two operation counts represent different kinds of work and should not be interpreted as equivalent database-query counts.

For database-backed GraphQL applications, DataLoader may reduce repeated queries by loading multiple records in a single operation. That benefit has not been measured in this in-memory project.

## 9. Prometheus Monitoring

The application exposes:

```text
GET /health
GET /metrics
```

The health endpoint returns:

```json
{
  "status": "healthy"
}
```

The metrics endpoint exposes Prometheus-formatted information, including Python runtime metrics and FastAPI HTTP request counters.

The endpoint was verified in the browser. This project does not claim that a separate Prometheus server or Grafana dashboard was configured.

## 10. Automated Test Results

The GraphQL API test suite completed successfully:

**7 passed in 1.59 seconds**

Covered behavior includes:

- Health endpoint
- Public GraphQL queries
- Authorized mutations
- Unauthorized mutations
- DataLoader batching
- DataLoader caching
- Missing project handling

## 11. Limitations

This evaluation has several limitations:

1. The API uses in-memory data rather than PostgreSQL.
2. Only 10 simulated users were used.
3. Testing was performed on a local development environment.
4. The test duration was limited to 60 seconds per run.
5. No equivalent REST implementation was load-tested.
6. No production infrastructure or network conditions were simulated.
7. DataLoader was already enabled in both Locust runs.
8. The benchmark did not measure actual database-query reductions.
9. The health check confirms application availability, not database readiness.

## 12. Recommended Future Improvements

Potential follow-up work includes:

- Replacing in-memory collections with PostgreSQL.
- Measuring SQL query counts with and without DataLoader.
- Benchmarking equivalent REST and GraphQL endpoints.
- Testing additional concurrency levels.
- Repeating tests multiple times and analyzing variance.
- Implementing GraphQL query-depth and complexity limits.
- Adding persistent Prometheus scraping and visualization.
- Profiling resolver execution and database operations.

These are future improvements rather than completed Day 26 features.

## 13. Conclusion

Day 26 successfully demonstrated GraphQL API development, authenticated mutations, DataLoader batching, automated testing, local load testing, and HTTP metrics instrumentation.

The application handled both Locust workloads without recorded failures.

DataLoader reduced the number of project-loading invocations, but direct dictionary access remained faster in the standalone benchmark.

The measurements provide a reproducible baseline and a technically accurate foundation for future database-backed optimization experiments.

**Final assessment:** The Day 26 performance-engineering exercises are complete, with no unsupported claim of a production performance improvement.