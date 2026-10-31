
-- DAY 6: POSTGRESQL PERFORMANCE BENCHMARK
-- Three optimization experiments
-- Uses separate tables to protect the original e-commerce data.

-- ==========================================
-- BENCHMARK 1: CUSTOMER ORDER HISTORY
-- ==========================================

DROP TABLE IF EXISTS benchmark_orders;

CREATE TABLE benchmark_orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL
);

INSERT INTO benchmark_orders (
    customer_id, order_date, total_amount, status
)
SELECT
    (n % 1000) + 1,
    TIMESTAMP '2026-01-01' + n * INTERVAL '1 minute',
    ((n % 5000) + 100)::NUMERIC(10, 2),
    CASE n % 4
        WHEN 0 THEN 'completed'
        WHEN 1 THEN 'pending'
        WHEN 2 THEN 'shipped'
        ELSE 'cancelled'
    END
FROM generate_series(1, 100000) AS n;

ANALYZE benchmark_orders;

-- Before index
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM benchmark_orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;

CREATE INDEX idx_benchmark_customer_date
ON benchmark_orders (customer_id, order_date DESC);

ANALYZE benchmark_orders;

-- After index
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM benchmark_orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;


-- ==========================================
-- BENCHMARK 2: PRODUCT CATALOG SEARCH
-- ==========================================

DROP TABLE IF EXISTS benchmark_products;

CREATE TABLE benchmark_products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

INSERT INTO benchmark_products (
    product_name, category, price
)
SELECT
    'Product ' || n,
    CASE n % 4
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Furniture'
        WHEN 2 THEN 'Books'
        ELSE 'Accessories'
    END,
    ((n % 50000) + 100)::NUMERIC(10, 2)
FROM generate_series(1, 100000) AS n;

ANALYZE benchmark_products;

-- Before index
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, product_name, price
FROM benchmark_products
WHERE category = 'Electronics'
ORDER BY price DESC
LIMIT 20;

CREATE INDEX idx_benchmark_products_category_price
ON benchmark_products (category, price DESC);

ANALYZE benchmark_products;

-- After index
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, product_name, price
FROM benchmark_products
WHERE category = 'Electronics'
ORDER BY price DESC
LIMIT 20;


-- ==========================================
-- BENCHMARK 3: COMPLETED PAYMENT REVENUE
-- ==========================================

DROP TABLE IF EXISTS benchmark_payments;

CREATE TABLE benchmark_payments (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL
);

INSERT INTO benchmark_payments (
    order_id, amount, payment_status
)
SELECT
    n,
    ((n % 10000) + 100)::NUMERIC(12, 2),
    CASE
        WHEN n % 10 = 0 THEN 'completed'
        WHEN n % 10 = 1 THEN 'failed'
        ELSE 'pending'
    END
FROM generate_series(1, 100000) AS n;

ANALYZE benchmark_payments;

-- Before index
EXPLAIN (ANALYZE, BUFFERS)
SELECT SUM(amount) AS total_revenue
FROM benchmark_payments
WHERE payment_status = 'completed';

CREATE INDEX idx_benchmark_payments_completed
ON benchmark_payments (payment_status)
INCLUDE (amount)
WHERE payment_status = 'completed';

ANALYZE benchmark_payments;

-- After index
EXPLAIN (ANALYZE, BUFFERS)
SELECT SUM(amount) AS total_revenue
FROM benchmark_payments
WHERE payment_status = 'completed';
