# Day 26 — GraphQL API & Performance Engineering

A FastAPI application demonstrating GraphQL queries and mutations, API key authentication, Strawberry DataLoader batching, Prometheus metrics, and Locust performance testing.

Part of the **30 Days of Backend Development** roadmap.

## Project Overview

This project explores how GraphQL can be integrated with FastAPI and how backend API performance can be measured.

It implements a task management API using Strawberry GraphQL, with nested project information, authenticated mutations, and request-scoped DataLoader instances.

The project also includes automated tests, HTTP metrics, and load-testing reports.

**Note:** Tasks and projects are stored in memory for learning purposes. This is not a persistent, production-ready task management system.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| FastAPI | ASGI application framework |
| Strawberry GraphQL | GraphQL schema, queries, and mutations |
| Strawberry DataLoader | Batching and caching related data |
| API key authentication | Protecting mutations |
| pytest | Automated testing |
| HTTPX | API testing |
| Locust | Load and performance testing |
| Prometheus instrumentation | HTTP metrics |
| uv | Dependency and environment management |

## Features

### GraphQL API

- Public GraphQL queries
- Task creation and completion mutations
- API key protection for mutations
- Nested task-to-project relationships
- Request-scoped DataLoader
- In-memory task and project data

### Performance Engineering

- Locust load-testing scenarios
- Baseline and repeat performance measurements
- DataLoader versus direct lookup benchmark
- Prometheus-compatible metrics endpoint
- Health-check endpoint
- Performance analysis and documentation

### Testing

- GraphQL query testing
- Authorized and unauthorized mutation testing
- DataLoader batching verification
- DataLoader caching verification
- Missing project handling
- Health endpoint testing

## Project Structure

```text
day26/
└── graphql-performance-api/
    ├── .env.example
    ├── .gitignore
    ├── .python-version
    ├── README.md
    ├── pyproject.toml
    ├── uv.lock
    ├── docs/
    │   ├── REST-vs-GraphQL.md
    │   └── performance-report.md
    ├── performance/
    │   ├── compare_dataloaders.py
    │   ├── locustfile.py
    │   ├── baseline_*.csv
    │   └── repeat_*.csv
    ├── src/
    │   └── graphql_performance_api/
    │       ├── __init__.py
    │       ├── auth.py
    │       ├── dataloaders.py
    │       ├── main.py
    │       ├── models.py
    │       └── schema.py
    └── tests/
        ├── test_dataloaders.py
        └── test_graphql.py
```

## Getting Started

### Prerequisites

- Python 3.12
- uv
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YashKhadse01/30-days-backend.git
cd 30-days-backend/day26/graphql-performance-api
```

### 2. Install dependencies

```powershell
uv sync
```

### 3. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Set the API key using the variable names defined in `.env.example`.

Never commit real API keys or other secrets to GitHub.

### 4. Start the application

```powershell
uv run uvicorn graphql_performance_api.main:app --reload --port 8001
```

The application is available at:

- GraphQL interface: `http://127.0.0.1:8001/graphql`
- Health endpoint: `http://127.0.0.1:8001/health`
- Prometheus metrics: `http://127.0.0.1:8001/metrics`

## GraphQL Examples

### Query tasks and projects

```graphql
query {
  tasks {
    id
    title
    completed
    project {
      id
      name
    }
  }
}
```

### Create a task

```graphql
mutation {
  createTask(
    title: "Learn GraphQL"
    projectId: 1
  ) {
    id
    title
    completed
  }
}
```

### Complete a task

```graphql
mutation {
  completeTask(taskId: 1) {
    id
    title
    completed
  }
}
```

Mutations require a valid API key supplied through the `X-API-Key` HTTP header.

## DataLoader Implementation

GraphQL APIs may encounter the N+1 query problem when resolving related objects.

For example, retrieving 100 tasks and their projects can result in repeated project lookups when each task resolves its project independently.

This project uses Strawberry DataLoader to demonstrate:

- Collecting related project IDs
- Batching lookup requests
- Caching repeated project IDs
- Returning project information to nested GraphQL fields

### Example

For project IDs:

```text
[1, 1, 2]
```

The DataLoader processes the two unique IDs in a single batch.

Observed terminal output:

```text
DataLoader batch: [1, 2]
```

This demonstrates batching and caching. Because the current implementation uses an in-memory dictionary, it does not demonstrate an actual reduction in SQL queries.

## Automated Testing

Run the complete test suite:

```powershell
uv run pytest -v
```

### Verified result

```text
7 passed in 2.86s
```

The tests cover GraphQL functionality, authentication behavior, DataLoader batching, caching, and health checks.

## Performance Testing with Locust

Start the FastAPI application before running load tests.

### Baseline test

```powershell
uv run locust -f .\performance\locustfile.py --headless --host http://127.0.0.1:8001 --users 10 --spawn-rate 2 --run-time 60s --csv .\performance\baseline
```

### Repeat test

```powershell
uv run locust -f .\performance\locustfile.py --headless --host http://127.0.0.1:8001 --users 10 --spawn-rate 2 --run-time 60s --csv .\performance\repeat
```

### Performance results

| Metric | Baseline | Repeat |
|---|---:|---:|
| Total requests | 382 | 384 |
| Failed requests | 0 | 0 |
| Average response time | 7.60 ms | 6.90 ms |
| Median response time | 5 ms | 5 ms |
| P95 response time | 14 ms | 13 ms |
| Throughput | 6.55 req/s | 6.59 req/s |

Both runs used the DataLoader-enabled implementation.

The differences between runs are observational and do not establish a measured optimization.

For the complete methodology, results, and limitations, see `docs/performance-report.md`.

## Direct Lookup vs DataLoader Benchmark

Run:

```powershell
uv run python .\performance\compare_dataloaders.py
```

### Observed results

| Metric | Direct lookup | DataLoader |
|---|---:|---:|
| Iterations | 1,000 | 1,000 |
| Total time | 0.734 ms | 56.692 ms |
| Lookup operations | 3,000 | 1,000 batch invocations |

Direct dictionary lookup was faster in this benchmark.

DataLoader is primarily useful when batching reduces expensive operations, such as repeated database or network queries. Its performance benefits depend on the underlying data source.

## Monitoring

Prometheus-compatible metrics are exposed at:

```text
http://127.0.0.1:8001/metrics
```

The endpoint provides HTTP request instrumentation and Python runtime metrics.

This project demonstrates metrics exposure; it does not include a separately configured Prometheus server or Grafana dashboard.

## REST vs GraphQL

REST exposes resources through multiple endpoints, while GraphQL lets clients specify the fields required from a schema.

This project focuses on GraphQL flexibility, nested relationships, and performance considerations.

See `docs/REST-vs-GraphQL.md` for the comparison.

## Learning Outcomes

By completing Day 26, the following concepts were practiced:

1. Integrating Strawberry GraphQL with FastAPI.
2. Defining GraphQL types, queries, and mutations.
3. Protecting mutations using API key authentication.
4. Implementing DataLoader batching and caching.
5. Writing automated GraphQL and DataLoader tests.
6. Measuring API latency, throughput, and failure rates.
7. Exposing Prometheus-compatible metrics.
8. Interpreting benchmark results without overstating performance improvements.

## Real-World Applications

These concepts can be applied to:

- Enterprise dashboards that combine related data
- Task and project management systems
- Analytics APIs with nested relationships
- Applications requiring flexible client-side data selection
- Backend services that need performance monitoring
- APIs that benefit from batched database access

## Limitations and Future Improvements

The project is a learning implementation and currently has the following limitations:

- In-memory data does not persist across restarts.
- API key authentication is simpler than full user authentication.
- No database-backed DataLoader benchmark has been conducted.
- Load tests used a small local workload.
- A separate REST implementation was not benchmarked.
- No production deployment or distributed monitoring setup is included.

Future work could introduce PostgreSQL persistence, database-backed batching, additional concurrency testing, query complexity controls, and production monitoring.

## Roadmap Deliverables

| Requirement | Status |
|---|---|
| Strawberry GraphQL on FastAPI | Completed |
| Queries and mutations | Completed |
| Authentication | Completed |
| DataLoader | Completed |
| Locust load testing | Completed |
| Prometheus metrics | Completed |
| Health checks | Completed |
| REST vs GraphQL comparison | Completed |
| Performance report | Completed |
| Automated testing | 7 passed |

## Author

**YashKhadse01**

GitHub: https://github.com/YashKhadse01

Part of the **30 Days of Backend Development** learning journey.
