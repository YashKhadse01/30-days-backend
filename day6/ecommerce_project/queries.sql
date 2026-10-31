-- DAY 6: E-COMMERCE DATABASE
-- 25 PostgreSQL practice queries
-- Run after schema.sql and seed.sql.

-- 01. View all products
SELECT * FROM products;

-- 02. Find products costing more than 10000
SELECT product_name, category, price
FROM products
WHERE price > 10000
ORDER BY price DESC;

-- 03. Five cheapest products
SELECT product_name, price
FROM products
ORDER BY price ASC
LIMIT 5;

-- 04. Electronics products
SELECT product_name, price
FROM products
WHERE category = 'Electronics';

-- 05. Products with low stock
SELECT product_name, stock_quantity
FROM products
WHERE stock_quantity < 20;

-- 06. Count products by category
SELECT category, COUNT(*) AS product_count
FROM products
GROUP BY category;

-- 07. Average product price by category
SELECT category, ROUND(AVG(price), 2) AS average_price
FROM products
GROUP BY category;

-- 08. Categories with average price above 5000
SELECT category, ROUND(AVG(price), 2) AS average_price
FROM products
GROUP BY category
HAVING AVG(price) > 5000;

-- 09. Total inventory value
SELECT SUM(price * stock_quantity) AS inventory_value
FROM products;

-- 10. List customers alphabetically
SELECT customer_id, full_name, email
FROM customers
ORDER BY full_name;

-- 11. Show orders with customer names
SELECT o.order_id, c.full_name, o.status
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY o.order_id;

-- 12. Show order totals
SELECT o.order_id, c.full_name,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
JOIN order_items AS oi
  ON oi.order_id = o.order_id
GROUP BY o.order_id, c.full_name
ORDER BY order_total DESC;

-- 13. Count orders per customer
SELECT c.customer_id, c.full_name,
       COUNT(o.order_id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY order_count DESC;

-- 14. Customers with no orders
SELECT c.customer_id, c.full_name
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- 15. Show purchased products and quantities
SELECT o.order_id, p.product_name, oi.quantity,
       oi.unit_price
FROM order_items AS oi
JOIN orders AS o
  ON o.order_id = oi.order_id
JOIN products AS p
  ON p.product_id = oi.product_id
ORDER BY o.order_id;

-- 16. Most frequently purchased products
SELECT p.product_name,
       SUM(oi.quantity) AS units_sold
FROM products AS p
JOIN order_items AS oi
  ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY units_sold DESC;

-- 17. Revenue from completed payments
SELECT COUNT(*) AS completed_payments,
       COALESCE(SUM(amount), 0) AS total_revenue
FROM payments
WHERE payment_status = 'completed';

-- 18. Payment totals by method
SELECT payment_method,
       COUNT(*) AS payment_count,
       SUM(amount) AS total_amount
FROM payments
GROUP BY payment_method
ORDER BY total_amount DESC;

-- 19. Payment totals by status
SELECT payment_status,
       COUNT(*) AS payment_count,
       SUM(amount) AS total_amount
FROM payments
GROUP BY payment_status;

-- 20. Orders without completed payments
SELECT o.order_id, o.status
FROM orders AS o
WHERE NOT EXISTS (
    SELECT 1
    FROM payments AS p
    WHERE p.order_id = o.order_id
      AND p.payment_status = 'completed'
);

-- 21. Products priced above their category average
SELECT p.product_name, p.category, p.price
FROM products AS p
WHERE p.price > (
    SELECT AVG(p2.price)
    FROM products AS p2
    WHERE p2.category = p.category
);

-- 22. Customer spending using a CTE
WITH customer_spending AS (
    SELECT o.customer_id,
           SUM(p.amount) AS total_spent
    FROM orders AS o
    JOIN payments AS p
      ON p.order_id = o.order_id
    WHERE p.payment_status = 'completed'
    GROUP BY o.customer_id
)
SELECT c.full_name,
       COALESCE(cs.total_spent, 0) AS total_spent
FROM customers AS c
LEFT JOIN customer_spending AS cs
  ON cs.customer_id = c.customer_id
ORDER BY total_spent DESC;

-- 23. Rank products by price within each category
SELECT product_name, category, price,
       DENSE_RANK() OVER (
           PARTITION BY category
           ORDER BY price DESC
       ) AS price_rank
FROM products
ORDER BY category, price_rank, product_name;

-- 24. Rank customers by completed payment value
SELECT c.full_name,
       COALESCE(SUM(p.amount), 0) AS total_spent,
       DENSE_RANK() OVER (
           ORDER BY COALESCE(SUM(p.amount), 0) DESC
       ) AS spending_rank
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
LEFT JOIN payments AS p
  ON p.order_id = o.order_id
 AND p.payment_status = 'completed'
GROUP BY c.customer_id, c.full_name
ORDER BY spending_rank;

-- 25. Monthly completed payment revenue
SELECT DATE_TRUNC('month', paid_at) AS revenue_month,
       COUNT(*) AS payment_count,
       SUM(amount) AS monthly_revenue
FROM payments
WHERE payment_status = 'completed'
  AND paid_at IS NOT NULL
GROUP BY DATE_TRUNC('month', paid_at)
ORDER BY revenue_month;
