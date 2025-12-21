# CORRECT Database Schema - Text-to-SQL Demo

## Database: text_to_sql_demo

### Table: customers (VERIFIED SCHEMA)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| customer_id | bigint | Unique customer identifier (Primary Key) |
| name | string | Customer full name |
| email | string | Customer email address |
| city | string | Customer city |
| state | string | Customer state |
| signup_date | date | Account signup date |

### Table: orders (VERIFIED SCHEMA)
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| order_id | bigint | Unique order identifier (Primary Key) |
| customer_id | bigint | Customer who placed the order |
| product_name | string | Product name |
| category | string | Product category |
| quantity | int | Quantity ordered |
| price | decimal(10,2) | Unit price |
| total_amount | decimal(10,2) | Total order amount |
| order_date | date | Order date |

## SIMPLE WORKING QUERIES ONLY

### Top 5 customers by revenue
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

## CRITICAL RULES:
1. NEVER use HAVING with column aliases
2. NEVER use CASE statements in HAVING clauses
3. Use signup_date for customer date filtering (NOT registration_date)
4. Keep all queries simple with basic aggregations only