# Simple SQL Query Examples for Text-to-SQL Agent

## WORKING QUERY PATTERNS - USE THESE TEMPLATES

### 1. Top customers by revenue (SIMPLE - NO HAVING CLAUSES)
```sql
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```

### 2. Top products by sales
```sql
SELECT product_name, category,
       COUNT(order_id) as order_count,
       SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;
```

### 3. Sales by category
```sql
SELECT category,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;
```

### 4. Customer order counts
```sql
SELECT c.name, c.email, c.city,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as total_spent
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_spent DESC
LIMIT 10;
```

### 5. Recent orders
```sql
SELECT c.name, o.product_name, o.total_amount, o.order_date
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= date_add('day', -30, CURRENT_DATE)
ORDER BY o.order_date DESC
LIMIT 20;
```

## CRITICAL RULES FOR ATHENA:
1. NEVER use column aliases in HAVING clauses
2. NEVER use CASE expressions in HAVING clauses  
3. Keep queries simple - avoid complex nested logic
4. Use date_add('day', -N, CURRENT_DATE) for date filtering
5. Always use LIMIT for large result sets