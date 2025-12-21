# Simple Business Glossary for Text-to-SQL Agent

## Revenue Analysis Patterns

### Top Customers by Revenue
```sql
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```

### Sales Performance by Category
```sql
SELECT category,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as total_revenue,
       AVG(total_amount) as avg_order_value
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;
```

### Customer Activity Summary
```sql
SELECT c.name, c.email, c.city,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as lifetime_value
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY lifetime_value DESC;
```

### Product Performance
```sql
SELECT product_name, category,
       COUNT(order_id) as order_count,
       SUM(total_amount) as total_revenue,
       SUM(quantity) as total_units_sold
FROM text_to_sql_demo.orders
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;
```

## SIMPLE PATTERNS ONLY - NO COMPLEX CASE STATEMENTS OR HAVING CLAUSES