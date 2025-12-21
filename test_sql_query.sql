SELECT 
    c.customer_name,
    c.email,
    SUM(o.total_amount) as total_revenue,
    COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.customer_name, c.email
ORDER BY total_revenue DESC
LIMIT 5;