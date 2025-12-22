# SQL Query Examples

## 1. Top Customers by Revenue
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

## 2. Trending Products This Month
**Question**: "What are the trending products this month?"
```sql
SELECT 
    o.product_name,
    o.category,
    COUNT(o.order_id) as order_count,
    SUM(o.quantity) as total_quantity,
    SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.orders o
WHERE o.status = 'Delivered'
    AND o.order_date >= date_add('day', -30, CURRENT_DATE)
GROUP BY o.product_name, o.category
ORDER BY order_count DESC
LIMIT 10;
```

## 3. Customers at Risk of Churning
**Question**: "Find customers at risk of churning"
```sql
SELECT 
    c.name,
    c.email,
    c.city,
    MAX(o.order_date) as last_order_date,
    date_diff('day', MAX(o.order_date), CURRENT_DATE) as days_since_last_order
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY days_since_last_order DESC NULLS FIRST
LIMIT 10;
```

## 4. Sales Performance by Region
**Question**: "Compare sales performance by region"
```sql
SELECT 
    c.state as region,
    COUNT(DISTINCT c.customer_id) as customer_count,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY c.state
ORDER BY total_revenue DESC
LIMIT 10;
```

## 5. Products with Highest Profit Margins
**Question**: "Which products have the highest profit margins?"
```sql
SELECT 
    o.product_name,
    o.category,
    AVG(o.price) as avg_price,
    SUM(o.total_amount) as total_revenue,
    COUNT(o.order_id) as order_count,
    SUM(o.quantity) as total_sold
FROM text_to_sql_demo.orders o
WHERE o.status = 'Delivered'
GROUP BY o.product_name, o.category
ORDER BY avg_price DESC
LIMIT 10;
```

## Key Rules
1. Always use table prefix: text_to_sql_demo.table_name
2. Join customers and orders on customer_id
3. Include customer name and email in results when possible
4. Use 'Delivered' status for revenue calculations
5. Include all non-aggregate columns in GROUP BY clause
6. Use date_add('day', -30, CURRENT_DATE) for "this month" queries
7. Use date_diff('day', date1, date2) for date differences