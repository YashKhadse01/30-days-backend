
-- Day 6: E-commerce sample data
-- Run once on a fresh, empty schema.

BEGIN;

-- 1. Customers
INSERT INTO customers (full_name, email, phone)
VALUES
('Alice Sharma', 'alice@example.com', '9876543210'),
('Bob Patil', 'bob@example.com', '9876543211'),
('Charlie Singh', 'charlie@example.com', '9876543212'),
('Diana Gupta', 'diana@example.com', '9876543213'),
('Ethan Rao', 'ethan@example.com', '9876543214'),
('Fatima Khan', 'fatima@example.com', '9876543215'),
('Gaurav Deshmukh', 'gaurav@example.com', '9876543216'),
('Heena Joshi', 'heena@example.com', '9876543217');

-- 2. Products
INSERT INTO products
(product_name, category, price, stock_quantity)
VALUES
('Laptop', 'Electronics', 65000.00, 15),
('Smartphone', 'Electronics', 25000.00, 30),
('Headphones', 'Electronics', 2500.00, 60),
('Keyboard', 'Electronics', 1500.00, 40),
('Mouse', 'Electronics', 800.00, 80),
('Office Chair', 'Furniture', 7500.00, 20),
('Study Table', 'Furniture', 12000.00, 10),
('Python Book', 'Books', 900.00, 100),
('SQL Book', 'Books', 750.00, 90),
('Backpack', 'Accessories', 1800.00, 50),
('Monitor', 'Electronics', 15000.00, 25),
('Water Bottle', 'Accessories', 500.00, 100);

-- 3. Orders
INSERT INTO orders (customer_id, status, order_date)
VALUES
(1, 'delivered', NOW() - INTERVAL '30 days'),
(2, 'delivered', NOW() - INTERVAL '25 days'),
(1, 'shipped', NOW() - INTERVAL '12 days'),
(3, 'confirmed', NOW() - INTERVAL '8 days'),
(4, 'pending', NOW() - INTERVAL '4 days'),
(5, 'delivered', NOW() - INTERVAL '20 days'),
(6, 'cancelled', NOW() - INTERVAL '15 days'),
(2, 'confirmed', NOW() - INTERVAL '2 days'),
(7, 'pending', NOW() - INTERVAL '1 day'),
(3, 'delivered', NOW() - INTERVAL '18 days');

-- 4. Order items
INSERT INTO order_items
(order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 1, 65000.00),
(1, 3, 2, 2500.00),
(2, 2, 1, 25000.00),
(2, 10, 1, 1800.00),
(3, 11, 1, 15000.00),
(3, 4, 1, 1500.00),
(4, 8, 2, 900.00),
(4, 9, 1, 750.00),
(5, 6, 1, 7500.00),
(6, 7, 1, 12000.00),
(6, 5, 2, 800.00),
(7, 3, 1, 2500.00),
(8, 2, 2, 25000.00),
(8, 5, 1, 800.00),
(9, 10, 2, 1800.00),
(10, 11, 1, 15000.00),
(10, 8, 1, 900.00);

-- 5. Payments
INSERT INTO payments
(order_id, amount, payment_method, payment_status, paid_at)
VALUES
(1, 70000.00, 'upi', 'completed', NOW() - INTERVAL '30 days'),
(2, 26800.00, 'card', 'completed', NOW() - INTERVAL '25 days'),
(3, 16500.00, 'upi', 'completed', NOW() - INTERVAL '12 days'),
(4, 2550.00, 'net_banking', 'pending', NULL),
(5, 7500.00, 'cod', 'pending', NULL),
(6, 13600.00, 'card', 'completed', NOW() - INTERVAL '20 days'),
(7, 2500.00, 'upi', 'failed', NULL),
(8, 50800.00, 'upi', 'completed', NOW() - INTERVAL '2 days'),
(9, 3600.00, 'cod', 'pending', NULL),
(10, 15900.00, 'card', 'completed', NOW() - INTERVAL '18 days');

COMMIT;
