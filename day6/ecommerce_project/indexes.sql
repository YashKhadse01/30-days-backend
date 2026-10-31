
-- DAY 6: PostgreSQL Index Optimization
-- Project: E-commerce Database
-- Purpose: Improve product searches, customer order history,
-- and completed payment reporting.

-- INDEX 1: Product search by category and price
-- Useful for: GET /products?category=Electronics&sort=price_desc

CREATE INDEX IF NOT EXISTS idx_products_category_price
ON products (category, price DESC);


-- INDEX 2: Customer order history
-- Useful for: GET /customers/1/orders

CREATE INDEX IF NOT EXISTS idx_orders_customer_date
ON orders (customer_id, order_date DESC);


-- INDEX 3: Completed payment revenue reporting
-- Partial covering index: stores only completed payments.
-- INCLUDE (amount) can enable index-only scans.

CREATE INDEX IF NOT EXISTS idx_payments_completed
ON payments (payment_status)
INCLUDE (amount)
WHERE payment_status = 'completed';


-- Update PostgreSQL statistics
ANALYZE products;
ANALYZE orders;
ANALYZE payments;
