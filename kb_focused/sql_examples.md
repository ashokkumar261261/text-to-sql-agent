# SQL Query Examples

## Top Customers by Revenue
**Question**: "Show me top 5 customers by revenue"
```sql
SELECT 
    c.name,
    c.email,
    c.city,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```

## Customers at Risk of Churning
**Question**: "Find customers at risk of churning"
```sql
SELECT 
    c.name,
    c.email,
    MAX(o.order_date) as last_order_date,
    date_diff('day', MAX(o.order_date), CURRENT_DATE) as days_since_last_order
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
ORDER BY days_since_last_order DESC NULLS FIRST
LIMIT 10;
```

## Recent Customer Activity
**Question**: "Show customers who ordered recently"
```sql
SELECT 
    c.name,
    c.email,
    o.order_date,
    o.total_amount
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= date_add('day', -30, CURRENT_DATE)
    AND o.status = 'Delivered'
ORDER BY o.order_date DESC
LIMIT 20;
```

## Product Performance
**Question**: "What are the best selling products"
```sql
SELECT 
    o.product_name,
    o.category,
    COUNT(o.order_id) as order_count,
    SUM(o.quantity) as total_quantity,
    SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.orders o
WHERE o.status = 'Delivered'
GROUP BY o.product_name, o.category
ORDER BY total_revenue DESC
LIMIT 10;
```

## Key Rules
1. Always use table prefix: text_to_sql_demo.table_name
2. Join customers and orders on customer_id
3. Include customer name and email in results when possible
4. Use 'Delivered' status for revenue calculations
5. Include all non-aggregate columns in GROUP BY clause