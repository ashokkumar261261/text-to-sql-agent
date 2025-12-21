# Text-to-SQL Database Schema Documentation

## Database: text_to_sql_demo

### Table: customers
**Purpose**: Store customer information and contact details

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| customer_id | bigint | Unique identifier for each customer (Primary Key) |
| name | string | Customer full name |
| email | string | Customer email address |
| phone | string | Customer phone number |
| city | string | Customer city |
| state | string | Customer state/province |
| country | string | Customer country |

**Sample Query**: `SELECT * FROM text_to_sql_demo.customers LIMIT 10;`

### Table: orders
**Purpose**: Store order transactions and purchase details

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| order_id | bigint | Unique identifier for each order (Primary Key) |
| customer_id | bigint | Foreign key referencing customers.customer_id |
| product_name | string | Name of the product ordered |
| category | string | Product category (Electronics, Furniture, Appliances, etc.) |
| quantity | int | Number of items ordered |
| price | decimal(10,2) | Unit price of the product |
| total_amount | decimal(10,2) | Total amount for this order line |
| order_date | date | Date when order was placed |
| status | string | Order status (completed, pending, cancelled) |

**Important**: This table uses `product_name` (string) to identify products, not `product_id`.

**Sample Queries**:
- `SELECT * FROM text_to_sql_demo.orders LIMIT 10;`
- `SELECT * FROM text_to_sql_demo.orders WHERE category = 'Electronics';`

### Table: products
**Purpose**: Store product catalog information

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| product_id | bigint | Unique identifier for each product (Primary Key) |
| product_name | string | Product name |
| category | string | Product category |
| price | decimal(10,2) | Current product price |
| stock | int | Available stock quantity |
| supplier | string | Product supplier name |

**Sample Queries**:
- `SELECT * FROM text_to_sql_demo.products LIMIT 10;`
- `SELECT * FROM text_to_sql_demo.products WHERE category = 'Electronics';`

## Table Relationships

### Customer-Orders Relationship
- **Join Condition**: `customers.customer_id = orders.customer_id`
- **Example**: Find customer order history
```sql
SELECT c.name, c.email, o.product_name, o.total_amount, o.order_date
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC;
```

### Products-Orders Relationship
- **Join Condition**: `products.product_name = orders.product_name`
- **Example**: Find product sales data
```sql
SELECT p.product_name, p.category, COUNT(o.order_id) as order_count, SUM(o.quantity) as total_sold
FROM text_to_sql_demo.products p
JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name
GROUP BY p.product_name, p.category
ORDER BY order_count DESC;
```

## Common Query Patterns

### Revenue Analysis
```sql
-- Top customers by revenue
SELECT c.name, c.email, SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
ORDER BY total_revenue DESC
LIMIT 10;
```

### Product Trending Analysis
```sql
-- Trending products by order count
SELECT o.product_name, o.category, COUNT(o.order_id) as order_count, SUM(o.quantity) as total_quantity
FROM text_to_sql_demo.orders o
GROUP BY o.product_name, o.category
ORDER BY order_count DESC
LIMIT 10;
```

### Category Performance
```sql
-- Sales by category
SELECT category, COUNT(order_id) as total_orders, SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;
```

## Important Notes for SQL Generation

1. **Always use database prefix**: `text_to_sql_demo.table_name`
2. **Product relationships**: Use `product_name` for joins between products and orders tables
3. **Customer relationships**: Use `customer_id` for joins between customers and orders tables
4. **Date filtering**: Use proper date format for `order_date`
5. **Aggregations**: Use appropriate GROUP BY clauses when using COUNT, SUM, AVG functions
6. **Performance**: Always include LIMIT clause for large result sets
7. **Column aliases**: Use meaningful aliases for calculated fields (e.g., `total_revenue`, `order_count`)
8. **NULL handling**: Consider NULL values in joins and calculations

## CRITICAL ATHENA RULES - MUST FOLLOW:
1. **NEVER use column aliases in HAVING clauses** - Athena doesn't support this
2. **NEVER use CASE expressions in HAVING clauses** - Use WHERE or subqueries instead
3. **Keep queries simple** - Avoid complex nested CASE statements in GROUP BY/HAVING
4. **Use date_diff('day', date1, date2)** - Not DATEDIFF
5. **For revenue queries, use simple SUM and ORDER BY** - Don't add complex filtering