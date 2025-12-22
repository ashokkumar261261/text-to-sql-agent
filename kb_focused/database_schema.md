# Database Schema

## Table: customers
- customer_id (bigint) - Primary key
- name (string) - Customer full name
- email (string) - Customer email address
- city (string) - Customer city
- state (string) - Customer state
- signup_date (date) - When customer signed up

## Table: orders
- order_id (bigint) - Primary key
- customer_id (bigint) - Foreign key to customers.customer_id
- product_name (string) - Name of product ordered
- category (string) - Product category
- quantity (int) - Quantity ordered
- price (decimal) - Unit price
- total_amount (decimal) - Total order amount
- order_date (date) - When order was placed
- status (string) - Order status: 'Delivered', 'Shipped', 'Processing'

## Key Relationships
- customers.customer_id = orders.customer_id (one-to-many)

## Database Name
All tables are in database: text_to_sql_demo