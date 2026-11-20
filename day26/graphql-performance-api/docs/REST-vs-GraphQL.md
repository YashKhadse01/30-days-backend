# REST vs GraphQL — Day 26

## 1. Overview

REST and GraphQL are two approaches to designing APIs.

REST typically exposes multiple resource-oriented endpoints, while GraphQL provides a typed schema through which clients can request specific fields and relationships.

This comparison accompanies the Day 26 **GraphQL + Performance** project, developed using Strawberry GraphQL and FastAPI.

## 2. REST vs GraphQL Comparison

| Feature | REST | GraphQL |
|---|---|---|
| Architecture | Resource-oriented API design | Schema-driven API query language |
| Endpoints | Typically multiple resource endpoints | Commonly one GraphQL endpoint |
| Data fetching | Server-defined response structures | Client selects required fields |
| Over-fetching | May return unnecessary fields | Can request only needed fields |
| Under-fetching | May require multiple requests | Can fetch related data in one query |
| Versioning | Often uses explicit API versions | Often evolves through schema changes and deprecations |
| Caching | Works naturally with HTTP caching | Often requires GraphQL-aware caching |
| Error handling | Uses HTTP status codes and response bodies | Uses GraphQL `data` and `errors`, alongside HTTP status codes |
| Performance | Depends on endpoint and implementation | Depends on query complexity and resolver implementation |
| Security | Authentication, authorization, rate limiting | Authentication, authorization, rate limiting, query-depth and complexity controls |

## 3. Example: Fetching Tasks and Their Projects

### REST approach

A typical REST API might expose:

```http
GET /tasks
GET /projects/1
GET /projects/2
```

The client can fetch tasks and then retrieve their associated projects. A well-designed REST endpoint could also return the project details directly, avoiding additional requests.

### GraphQL approach

Our Day 26 application exposes `/graphql`.

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

The client requests task information and related project details in one GraphQL operation.

## 4. Strawberry GraphQL and FastAPI

Our project uses:

- **FastAPI:** Hosts the application and exposes HTTP endpoints.
- **Strawberry GraphQL:** Defines the GraphQL schema, queries, mutations, and resolvers.
- **API-key authentication:** Protects task-creation and task-completion mutations.
- **DataLoader:** Batches and caches repeated project lookups within a request.
- **pytest and HTTPX:** Test GraphQL functionality and API behavior.
- **Locust:** Measures application performance under simulated traffic.
- **Prometheus instrumentation:** Exposes HTTP metrics through `/metrics`.

## 5. DataLoader and the N+1 Problem

The N+1 query problem occurs when an application first retrieves a collection and then performs an additional database query for every item in that collection.

DataLoader can reduce this problem by collecting multiple related IDs and loading their data in batches.

In our Day 26 in-memory demonstration:

- Three tasks reference project IDs `[1, 1, 2]`.
- Direct lookup performs three individual dictionary lookups.
- DataLoader combines the requests into one batch containing IDs `[1, 2]`.
- Repeated project IDs are cached within the DataLoader instance.

Our benchmark showed fewer loading operations, but DataLoader took longer to execute than direct dictionary lookup. This is because dictionary access is inexpensive and DataLoader introduces additional overhead.

A database-backed implementation would be needed to measure actual database-query reductions and their impact on latency.

## 6. Performance Considerations

REST is not inherently faster than GraphQL, and GraphQL is not inherently faster than REST.

Performance depends on factors such as:

- Database queries and indexing
- Payload size
- Network latency
- Resolver efficiency
- Caching
- Query complexity
- Server resources
- Concurrent workload

GraphQL can be particularly useful when clients need flexible combinations of related data. REST can be especially effective for predictable resource operations and straightforward HTTP caching.

## 7. Security Considerations

Both approaches require strong security controls.

For GraphQL, important considerations include field-level authorization, query complexity limits, depth limits, rate limiting, and preventing sensitive data exposure.

Our Day 26 project demonstrates API-key-protected mutations. It is a learning application, not a complete production authentication or authorization system.

## 8. When to Choose Each Approach

**Choose REST when:**

- Resource operations are straightforward.
- Response structures are predictable.
- HTTP caching is important.
- Simplicity and conventional tooling are priorities.

**Choose GraphQL when:**

- Clients need flexible field selection.
- Multiple related resources are frequently requested together.
- Different clients require different response shapes.
- A strongly typed API schema and introspection are valuable.

## 9. Conclusion

REST and GraphQL solve overlapping API-design problems using different approaches.

For Day 26, Strawberry GraphQL demonstrates flexible queries, mutations, authentication, nested relationships, and DataLoader batching.

Our Locust results measure the GraphQL application only. They do **not** establish that GraphQL is faster than REST because we have not benchmarked an equivalent REST implementation under identical conditions.

The detailed measurements are documented separately in the Day 26 performance report.