# Query Structure Examples

## Customer Revenue Pattern
```sql
SELECT 
    c.name,
    c.email,
    SUM(o.total_amount) as revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name, c.email
ORDER BY revenue DESC;
```

## Product Performance Pattern
```sql
SELECT 
    o.product_name,
    o.category,
    COUNT(o.order_id) as sales_count
FROM text_to_sql_demo.orders o
WHERE o.status = 'Delivered'
GROUP BY o.product_name, o.category
ORDER BY sales_count DESC;
```

## Regional Analysis Pattern
```sql
SELECT 
    c.state,
    SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY c.state
ORDER BY total_revenue DESC;
```

## Recent Activity Pattern
```sql
SELECT 
    o.product_name,
    COUNT(o.order_id) as recent_orders
FROM text_to_sql_demo.orders o
WHERE o.status = 'Delivered'
    AND o.order_date >= date_add('day', -30, CURRENT_DATE)
GROUP BY o.product_name
ORDER BY recent_orders DESC;
```

## Customer Activity Pattern
```sql
SELECT 
    c.name,
    c.email,
    MAX(o.order_date) as last_order,
    date_diff('day', MAX(o.order_date), CURRENT_DATE) as days_ago
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
ORDER BY days_ago DESC NULLS FIRST;
```

## Essential Rules
- Always use text_to_sql_demo.table_name prefix
- Use 'Delivered' status for revenue calculations
- Include all non-aggregate columns in GROUP BY
- Use date_add('day', -30, CURRENT_DATE) for recent periods
- Use date_diff('day', date1, date2) for time differences