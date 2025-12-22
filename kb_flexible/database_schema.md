# Database Schema

## customers table
- customer_id (bigint) - Primary key
- name (string) - Customer full name
- email (string) - Customer email
- city (string) - Customer city  
- state (string) - Customer state/region
- signup_date (date) - Registration date

## orders table
- order_id (bigint) - Primary key
- customer_id (bigint) - Links to customers.customer_id
- product_name (string) - Product ordered
- category (string) - Product category
- quantity (int) - Quantity ordered
- price (decimal) - Unit price at time of order
- total_amount (decimal) - Total order value
- order_date (date) - Order placement date
- status (string) - 'Delivered', 'Shipped', 'Processing'

## products table
- product_id (bigint) - Primary key
- product_name (string) - Product name
- category (string) - Product category
- price (decimal) - Current product price
- stock (int) - Available inventory
- supplier (string) - Supplier name

## Key Relationships
- customers.customer_id = orders.customer_id (one-to-many)
- products.product_name = orders.product_name (one-to-many)
- Note: orders table contains historical price, products table contains current price
- Database name: text_to_sql_demo