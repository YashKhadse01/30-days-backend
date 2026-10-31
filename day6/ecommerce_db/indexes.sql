
-- DAY 6: POSTGRESQL INDEX OPTIMIZATION

-- Index 1: Product filtering and price sorting
CREATE INDEX IF NOT EXISTS idx_products_category_price
ON products (category, price DESC);

-- Index 2: Customer order history
CREATE INDEX IF NOT EXISTS idx_orders_customer_date
ON orders (customer_id, order_date DESC);

-- Index 3: Completed payment reporting
CREATE INDEX IF NOT EXISTS idx_payments_completed
ON payments (payment_status)
INCLUDE (amount)
WHERE payment_status = 'completed';
