# Text-to-SQL Simple Working Patterns

## Database Schema (VERIFIED)
- **Database**: text_to_sql_demo
- **customers**: customer_id, name, email, city, state, signup_date
- **orders**: order_id, customer_id, product_name, category, quantity, price, total_amount, order_date

## WORKING QUERY TEMPLATES

### Top customers by revenue
```sql
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```

### Sales by category
```sql
SELECT category,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;
```

### Customer order summary
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

### Top products by sales
```sql
SELECT product_name, category,
       COUNT(order_id) as order_count,
       SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;
```

## CRITICAL RULES
1. NEVER use HAVING with column aliases
2. NEVER use CASE statements in HAVING clauses
3. Use signup_date for customer dates (NOT registration_date)
4. Keep queries simple with basic aggregations only
5. Always use LIMIT for large result sets