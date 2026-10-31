
-- DAY 6: E-COMMERCE SQL PRACTICE
-- PART 1: BASIC SQL QUERIES

-- Query 1: Retrieve all customers
SELECT *
FROM customers;

-- Query 2: Display product names and prices
SELECT
    product_name,
    price
FROM products;

-- Query 3: Find products priced above 10000
SELECT
    product_name,
    price
FROM products
WHERE price > 10000;

-- Query 4: Sort products by price (highest first)
SELECT
    product_name,
    price
FROM products
ORDER BY price DESC;

-- Query 5: Find the 5 cheapest products
SELECT
    product_name,
    price
FROM products
ORDER BY price ASC
LIMIT 5;

-- PART 2: AGGREGATION AND GROUP BY

-- Query 6: Count total customers
SELECT COUNT(*) AS total_customers
FROM customers;

-- Query 7: Calculate total inventory quantity
SELECT SUM(stock_quantity) AS total_stock
FROM products;

-- Query 8: Find average, minimum and maximum product price
SELECT
    ROUND(AVG(price), 2) AS average_price,
    MIN(price) AS cheapest_price,
    MAX(price) AS highest_price
FROM products;

-- Query 9: Count products in each category
SELECT
    category,
    COUNT(*) AS total_products
FROM products
GROUP BY category
ORDER BY total_products DESC, category;

-- Query 10: Find categories with average price above 5000
SELECT
    category,
    COUNT(*) AS total_products,
    ROUND(AVG(price), 2) AS average_price
FROM products
GROUP BY category
HAVING AVG(price) > 5000
ORDER BY average_price DESC;

-- PART 3: SQL JOINS

-- Query 11: Show orders with customer names
SELECT
    o.order_id,
    c.full_name,
    o.order_date,
    o.status
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
ORDER BY o.order_id;


-- Query 12: Show each order item with its product name
SELECT
    oi.order_id,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS line_total
FROM order_items AS oi
INNER JOIN products AS p
    ON oi.product_id = p.product_id
ORDER BY oi.order_id, p.product_name;


-- Query 13: Show all customers and their orders
-- Includes customers who have not placed any orders
SELECT
    c.customer_id,
    c.full_name,
    o.order_id,
    o.status
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_id;


-- Query 14: Display orders with payment information
SELECT
    o.order_id,
    c.full_name,
    o.status AS order_status,
    pay.amount,
    pay.payment_method,
    pay.payment_status
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
LEFT JOIN payments AS pay
    ON o.order_id = pay.order_id
ORDER BY o.order_id, pay.payment_id;


-- Query 15: Calculate total value of each order
SELECT
    o.order_id,
    c.full_name,
    SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id
INNER JOIN order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY o.order_id, c.full_name
ORDER BY order_total DESC;

-- PART 4: ADVANCED SQL
-- SUBQUERIES, CTES AND WINDOW FUNCTIONS

-- Query 16: Products priced above the overall average
SELECT
    product_name,
    category,
    price
FROM products
WHERE price > (
    SELECT AVG(price)
    FROM products
)
ORDER BY price DESC;


-- Query 17: Customers who have placed at least one order
SELECT
    c.customer_id,
    c.full_name,
    c.email
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;


-- Query 18: Use a CTE to calculate order totals
WITH order_totals AS (
    SELECT
        order_id,
        SUM(quantity * unit_price) AS total_amount
    FROM order_items
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.full_name,
    ot.total_amount
FROM order_totals AS ot
JOIN orders AS o
    ON ot.order_id = o.order_id
JOIN customers AS c
    ON o.customer_id = c.customer_id
ORDER BY ot.total_amount DESC;


-- Query 19: Rank products by price within each category
SELECT
    product_name,
    category,
    price,
    RANK() OVER (
        PARTITION BY category
        ORDER BY price DESC
    ) AS price_rank
FROM products
ORDER BY category, price_rank, product_name;


-- Query 20: Number each customer's orders from newest to oldest
SELECT
    c.full_name,
    o.order_id,
    o.order_date,
    ROW_NUMBER() OVER (
        PARTITION BY o.customer_id
        ORDER BY o.order_date DESC, o.order_id DESC
    ) AS order_number
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id
ORDER BY c.full_name, order_number;

-- PART 5: E-COMMERCE ANALYTICS
-- QUERIES 21–25

-- Query 21: Find customers who have never placed an order
SELECT
    c.customer_id,
    c.full_name,
    c.email
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.customer_id;


-- Query 22: Calculate total completed payment revenue
SELECT
    COUNT(*) AS completed_payments,
    COALESCE(SUM(amount), 0) AS total_revenue
FROM payments
WHERE payment_status = 'completed';


-- Query 23: Find the top 5 best-selling products
SELECT
    p.product_name,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS sales_value
FROM order_items AS oi
JOIN products AS p
    ON oi.product_id = p.product_id
JOIN orders AS o
    ON oi.order_id = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY p.product_id, p.product_name
ORDER BY units_sold DESC, sales_value DESC
LIMIT 5;


-- Query 24: Find products with low inventory
SELECT
    product_id,
    product_name,
    category,
    stock_quantity
FROM products
WHERE stock_quantity < 25
ORDER BY stock_quantity ASC;


-- Query 25: Calculate each customer's completed payment total
SELECT
    c.customer_id,
    c.full_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(
        SUM(
            CASE
                WHEN pay.payment_status = 'completed'
                THEN pay.amount
                ELSE 0
            END
        ), 0
    ) AS total_paid
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
LEFT JOIN payments AS pay
    ON o.order_id = pay.order_id
GROUP BY c.customer_id, c.full_name
ORDER BY total_paid DESC, c.customer_id;

