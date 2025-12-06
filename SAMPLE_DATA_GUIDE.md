# Sample Data Guide

This guide describes the sample data created by `setup_glue_sample.py`.

## Database Schema

**Database Name:** `text_to_sql_demo`

### Tables

#### 1. customers
Customer information table

| Column | Type | Description |
|--------|------|-------------|
| customer_id | bigint | Unique customer identifier |
| name | string | Customer full name |
| email | string | Customer email address |
| city | string | Customer city |
| state | string | Customer state (US) |
| signup_date | date | Account signup date |

**Sample Data:** 10 customers from various US cities

#### 2. orders
Order transactions table

| Column | Type | Description |
|--------|------|-------------|
| order_id | bigint | Unique order identifier |
| customer_id | bigint | Customer who placed the order |
| product_name | string | Product name |
| category | string | Product category (Electronics/Furniture) |
| quantity | int | Quantity ordered |
| price | decimal(10,2) | Unit price |
| total_amount | decimal(10,2) | Total order amount |
| order_date | date | Order date |
| status | string | Order status (Delivered/Shipped/Processing) |

**Sample Data:** 15 orders from Jan-Feb 2024

#### 3. products
Product catalog table

| Column | Type | Description |
|--------|------|-------------|
| product_id | bigint | Unique product identifier |
| product_name | string | Product name |
| category | string | Product category |
| price | decimal(10,2) | Product price |
| stock | int | Available stock quantity |
| supplier | string | Supplier name |

**Sample Data:** 15 products (Electronics and Furniture)

## Sample Queries to Test

### Basic Queries

```sql
-- Get all customers
SELECT * FROM customers LIMIT 10;

-- Get all orders
SELECT * FROM orders LIMIT 10;

-- Get all products
SELECT * FROM products LIMIT 10;
```

### Natural Language Examples

Try these with your Text-to-SQL agent:

1. **"Show me all customers from Texas"**
   - Expected: Returns customers where state = 'TX'

2. **"What are the top 5 products by price?"**
   - Expected: Products ordered by price DESC, limited to 5

3. **"Count total orders by status"**
   - Expected: GROUP BY status with COUNT

4. **"List all orders with total amount over $500"**
   - Expected: Orders WHERE total_amount > 500

5. **"Show me customers who ordered Electronics"**
   - Expected: JOIN customers and orders WHERE category = 'Electronics'

6. **"What is the total revenue from all orders?"**
   - Expected: SUM of total_amount from orders

7. **"Which products are low in stock?"**
   - Expected: Products WHERE stock < 50

8. **"Show me orders placed in February 2024"**
   - Expected: Orders WHERE order_date BETWEEN '2024-02-01' AND '2024-02-28'

9. **"List customers by signup date"**
   - Expected: Customers ORDER BY signup_date

10. **"What are the most popular product categories?"**
    - Expected: GROUP BY category with COUNT from orders

### Advanced Queries

```sql
-- Customer order summary
SELECT 
    c.name,
    c.city,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.name, c.city
ORDER BY total_spent DESC;

-- Product performance
SELECT 
    p.product_name,
    p.category,
    p.price,
    COUNT(o.order_id) as times_ordered,
    SUM(o.quantity) as total_quantity_sold
FROM products p
LEFT JOIN orders o ON p.product_name = o.product_name
GROUP BY p.product_name, p.category, p.price
ORDER BY times_ordered DESC;

-- Revenue by category
SELECT 
    category,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM orders
GROUP BY category
ORDER BY total_revenue DESC;
```

## Data Statistics

- **Customers:** 10 records
- **Orders:** 15 records  
- **Products:** 15 records
- **Date Range:** January - February 2024
- **Categories:** Electronics, Furniture
- **States:** NY, CA, IL, TX, AZ, PA
- **Order Statuses:** Delivered, Shipped, Processing

## Testing Tips

1. **Start Simple:** Begin with basic SELECT queries
2. **Test Filters:** Try WHERE clauses with different conditions
3. **Test Aggregations:** Use COUNT, SUM, AVG functions
4. **Test Joins:** Query across multiple tables
5. **Test Date Filters:** Use date ranges in queries
6. **Test Sorting:** Try ORDER BY with different columns
7. **Test Grouping:** Use GROUP BY for analytics

## Troubleshooting

### No results returned
- Check if data was uploaded to S3
- Verify Glue table locations point to correct S3 paths
- Run a simple `SELECT * FROM table_name LIMIT 1` to test

### Schema errors
- Verify column names match the schema
- Check data types in queries
- Use `DESCRIBE table_name` to see schema

### Permission errors
- Ensure IAM role has S3 read permissions
- Check Athena workgroup permissions
- Verify Glue database access

## Next Steps

After testing with sample data:

1. **Add Your Own Data:** Upload CSV files to S3
2. **Create Custom Tables:** Define your own Glue tables
3. **Use Partitions:** For large datasets, partition by date
4. **Optimize Queries:** Use partition pruning for better performance
