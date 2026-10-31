# Day 6 — PostgreSQL E-Commerce Database and Query Optimization

## 1. Project Overview

This project demonstrates how PostgreSQL can be used to design, manage, query, and optimize a relational database for an e-commerce backend.

It was developed as part of a 30-day Python Backend Development Roadmap.

**Technology:** PostgreSQL 18, SQL, psql, VS Code, Windows PowerShell

## 2. Purpose of the Project

The purpose is to understand how a real backend application stores and retrieves business data.

The database supports:

- Customer management
- Product catalog management
- Customer orders
- Order line items
- Payment records
- Sales and revenue reporting
- SQL query optimization

## 3. Role in Real Backend Development

In a production e-commerce application, the frontend communicates with a backend API, and the backend interacts with a database.

**Typical architecture:**

Frontend → Python Backend API → PostgreSQL → JSON API Response

For example, when a customer opens their order history, the backend can execute a SQL query to retrieve their orders from PostgreSQL.

The database is responsible for storing consistent records, enforcing relationships, and retrieving information efficiently.

## 4. Database Schema

The database contains five main tables:

| Table | Responsibility |
|---|---|
| customers | Stores customer information |
| products | Stores product details, categories, prices, and stock |
| orders | Stores customer orders and their status |
| order_items | Stores products and quantities for each order |
| payments | Stores payment methods, amounts, and statuses |

**Relationships:**

- One customer can place many orders.
- One order can contain many order items.
- Each order item references a product.
- Payments reference orders.

The schema uses primary keys, foreign keys, unique constraints, NOT NULL constraints, and CHECK constraints to protect data integrity.

## 5. SQL Query Practice

The project includes 25 SQL queries covering:

- SELECT, WHERE, ORDER BY, LIMIT
- Aggregate functions such as COUNT, SUM, AVG
- GROUP BY and HAVING
- INNER JOIN and LEFT JOIN
- Subqueries and common table expressions
- Window functions and ranking
- Customer, product, order, and payment reporting

These queries represent common operations used in backend applications and reporting systems.

## 6. Database Index Optimization

Three main indexes were created:

### Product Category and Price Index

`idx_products_category_price`

Supports category-based product searches ordered by price.

### Customer Order History Index

`idx_orders_customer_date`

Supports retrieving a customer's orders in descending date order.

### Completed Payment Index

`idx_payments_completed`

Supports filtering completed payments and can help payment reporting queries.

Index effectiveness depends on query selectivity, table size, PostgreSQL statistics, and execution conditions.

## 7. Performance Benchmarking

The project includes `benchmark.sql`, which generates sample data and compares execution plans before and after adding indexes.

Three experiments are included:

1. Customer order history lookup
2. Product catalog filtering and sorting
3. Completed payment revenue aggregation

The experiments use `EXPLAIN (ANALYZE, BUFFERS)` to inspect execution time, scan strategies, and buffer usage.

**Observed completed-payment benchmark:** The indexed query used a Bitmap Heap Scan with an execution time of approximately 3.558 ms.

This is an observed result, not a guaranteed speedup. Before-and-after timings should be compared to evaluate performance improvements.

## 8. Project Files

| File | Purpose |
|---|---|
| schema.sql | Creates the relational database tables |
| seed.sql | Inserts example e-commerce records |
| queries.sql | Contains 25 SQL practice queries |
| indexes.sql | Creates three database indexes |
| benchmark.sql | Tests performance before and after indexing |
| README.md | Explains project architecture and usage |

## 9. How to Run

Install PostgreSQL and ensure the database service is running.

Create a database named `ecommerce_db`, then execute the files in the following order from the project directory.

```powershell
psql -U postgres -h 127.0.0.1 -d ecommerce_db -W -v ON_ERROR_STOP=1 -f .\schema.sql
psql -U postgres -h 127.0.0.1 -d ecommerce_db -W -v ON_ERROR_STOP=1 -f .\seed.sql
psql -U postgres -h 127.0.0.1 -d ecommerce_db -W -v ON_ERROR_STOP=1 -f .\queries.sql
psql -U postgres -h 127.0.0.1 -d ecommerce_db -W -v ON_ERROR_STOP=1 -f .\indexes.sql
psql -U postgres -h 127.0.0.1 -d ecommerce_db -W -v ON_ERROR_STOP=1 -P pager=off -f .\benchmark.sql
```

The schema and seed scripts are intended for initial setup; review them before rerunning against an existing database to avoid duplicate records or object conflicts.

The benchmark script recreates its own benchmark tables.

## 10. Learning Outcomes

By completing this project, I practiced:

- Relational database design
- PostgreSQL administration basics
- SQL joins and analytical queries
- Database constraints and relationships
- Index creation and optimization
- Reading PostgreSQL execution plans
- Performance benchmarking
- Organizing database code for GitHub

## 11. Future Enhancements

- Connect PostgreSQL to a Python FastAPI backend
- Implement REST API endpoints for customers and orders
- Use SQLAlchemy or another database access library
- Add database migrations
- Implement transactions and inventory updates
- Add integration tests and authentication

## 12. Conclusion

This project provides the database foundation for building real-world Python backend applications. It demonstrates not only how to store and query data but also how to investigate and optimize database performance.