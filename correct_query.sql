-- Correct SQL for "Show me top 5 customers by revenue"
-- Based on actual schema: customers(customer_id, name, email, city, state, signup_date)
-- and orders(order_id, customer_id, product_name, category, quantity, price, total_amount, order_date, status)

SELECT 
    c.name,
    c.email,
    c.city,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered' OR o.status IS NULL
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC NULLS LAST
LIMIT 5;