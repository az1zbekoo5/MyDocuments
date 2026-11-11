-- =============================================================
-- SavdoShop - SQL practice (Week 1). Run ONE query at a time:
-- select the query text in pgAdmin and press F5.
-- =============================================================

-- ---------- C R U D ----------
-- Q1 CREATE: add a new customer and return the generated id
INSERT INTO customers (full_name, email, city)
VALUES ('Student Test', 'student@example.uz', 'Tashkent')
RETURNING customer_id;

-- Q2 READ: products cheaper than 400 000 so'm, cheapest first
SELECT product_id, name, price
FROM products
WHERE price < 400000
ORDER BY price ASC;

-- Q3 UPDATE: 10% discount on all Shoes
UPDATE products
SET price = price * 0.9
WHERE category_id = (SELECT category_id FROM categories WHERE name = 'Shoes');

-- Q4 DELETE: remove the test customer
DELETE FROM customers WHERE email = 'student@example.uz';

-- ---------- J O I N S ----------
-- Q5 INNER JOIN: every product with its category name
SELECT p.name AS product, c.name AS category, p.price
FROM products p
JOIN categories c ON c.category_id = p.category_id
ORDER BY c.name, p.name;

-- Q6 Order details: who bought what (4 tables)
SELECT o.order_id, cu.full_name, p.name AS product, oi.quantity,
       oi.unit_price * oi.quantity AS line_total
FROM orders o
JOIN customers   cu ON cu.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id    = o.order_id
JOIN products    p  ON p.product_id   = oi.product_id
ORDER BY o.order_id;

-- Q7 LEFT JOIN: customers who have NEVER ordered
SELECT cu.full_name, cu.city
FROM customers cu
LEFT JOIN orders o ON o.customer_id = cu.customer_id
WHERE o.order_id IS NULL;

-- ---------- A G G R E G A T I O N ----------
-- Q8 Number of products and average price per category
SELECT c.name, COUNT(p.product_id) AS products, ROUND(AVG(p.price)) AS avg_price
FROM categories c
LEFT JOIN products p ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY products DESC;

-- Q9 Revenue per city (only cities with revenue > 500 000)
SELECT cu.city, SUM(o.total) AS revenue, COUNT(*) AS orders
FROM orders o
JOIN customers cu ON cu.customer_id = o.customer_id
WHERE o.status <> 'cancelled'
GROUP BY cu.city
HAVING SUM(o.total) > 500000
ORDER BY revenue DESC;

-- Q10 Best-selling products (by quantity)
SELECT p.name, SUM(oi.quantity) AS sold
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.name
ORDER BY sold DESC
LIMIT 5;

-- ---------- V I E W S  &  W I N D O W   F U N C T I O N S ----------
-- Q11 A view the website can reuse
CREATE OR REPLACE VIEW v_product_catalog AS
SELECT p.product_id, p.name, p.price, p.stock, p.image_url, c.name AS category
FROM products p
JOIN categories c ON c.category_id = p.category_id;

SELECT * FROM v_product_catalog WHERE category = 'Jewelry';

-- Q12 Rank products by price inside each category
SELECT category, name, price,
       RANK() OVER (PARTITION BY category ORDER BY price DESC) AS price_rank
FROM v_product_catalog;

-- ---------- T R A N S A C T I O N ----------
-- Q13 Place an order safely: all steps succeed or none do
BEGIN;
  INSERT INTO orders (customer_id) VALUES (3) RETURNING order_id;
  -- currval() = the order_id that was just generated in this session
  INSERT INTO order_items (order_id, product_id, quantity, unit_price)
  SELECT currval('orders_order_id_seq'), product_id, 1, price
  FROM products WHERE product_id = 4;
  UPDATE products SET stock = stock - 1 WHERE product_id = 4;
  UPDATE orders SET total = (SELECT SUM(quantity * unit_price) FROM order_items
                             WHERE order_id = currval('orders_order_id_seq'))
  WHERE order_id = currval('orders_order_id_seq');
COMMIT;   -- or ROLLBACK; to cancel everything
