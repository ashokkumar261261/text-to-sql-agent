# Database Schema Documentation

## Table: customers
**Description**: Contains information about all customers in the system

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| customer_id | BIGINT | Unique identifier for each customer | PRIMARY KEY, NOT NULL |
| name | STRING | Full name of the customer | NOT NULL |
| email | STRING | Customer's email address | UNIQUE, NOT NULL |
| city | STRING | Customer's city | |
| state | STRING | Customer's state | |
| signup_date | DATE | Date when customer registered | NOT NULL |

**Sample Data**:
```
customer_id: 1, name: "John Smith", email: "john@email.com", city: "New York", signup_date: "2023-01-15"
customer_id: 2, name: "Jane Doe", email: "jane@email.com", city: "Los Angeles", signup_date: "2023-02-20"
```

## Table: orders
**Description**: Contains information about customer orders (denormalized with product info)

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| order_id | BIGINT | Unique identifier for each order | PRIMARY KEY, NOT NULL |
| customer_id | BIGINT | Reference to customer who placed the order | FOREIGN KEY REFERENCES customers(customer_id) |
| product_name | STRING | Name of the product ordered | NOT NULL |
| category | STRING | Product category | NOT NULL |
| quantity | INT | Number of units ordered | NOT NULL, CHECK (quantity > 0) |
| price | DECIMAL(10,2) | Unit price at time of order | NOT NULL, CHECK (price >= 0) |
| total_amount | DECIMAL(10,2) | Total value of the order | NOT NULL, CHECK (total_amount >= 0) |
| order_date | DATE | Date when the order was placed | NOT NULL |
| status | STRING | Order status (pending, shipped, delivered, cancelled) | DEFAULT 'pending' |

**Sample Data**:
```
order_id: 1001, customer_id: 1, product_name: "Laptop Pro", category: "Electronics", 
quantity: 1, price: 1299.99, total_amount: 1299.99, order_date: "2023-03-15", status: "delivered"
```

## IMPORTANT: Athena-Specific Limitations

### 1. HAVING Clause Restrictions
- **CANNOT** use column aliases in HAVING clause
- **CANNOT** use CASE expressions in HAVING clause
- Use subqueries instead when needed

### 2. Column References
- Use actual column names: `name` (not `customer_name`)
- Always qualify columns with table aliases: `c.name`, `o.total_amount`

### 3. NULL Handling
- Use `NULLS LAST` or `NULLS FIRST` in ORDER BY for consistent results
- Use `IS NULL` checks for LEFT JOIN scenarios

## Common Query Patterns

### Top Customers by Revenue (CORRECT)
```sql
SELECT 
    c.name,
    c.email,
    c.city,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered' OR o.status IS NULL
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC NULLS LAST
LIMIT 5;
```

### Customer Analysis with Risk Assessment (CORRECT)
```sql
SELECT 
    c.name,
    c.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as lifetime_value,
    MAX(o.order_date) as last_order_date
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
ORDER BY lifetime_value DESC NULLS LAST;
```

### AVOID: Complex HAVING with Aliases (INCORRECT)
```sql
-- THIS WILL FAIL IN ATHENA
SELECT c.name, 
       CASE WHEN MAX(o.order_date) IS NULL THEN 'Never Ordered' END as risk
FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING risk = 'Never Ordered';  -- ERROR: Cannot use alias in HAVING
```

## Relationships and Foreign Keys

### customers → orders
- One customer can have many orders
- orders.customer_id references customers.customer_id

### orders → order_items
- One order can have many order items
- order_items.order_id references orders.order_id

### products → order_items
- One product can appear in many order items
- order_items.product_id references products.product_id

### orders → sales
- One order can have one sale record
- sales.order_id references orders.order_id

### sales_reps → sales
- One sales rep can have many sales
- sales.rep_id references sales_reps.rep_id

## Indexes for Performance

### Primary Indexes (Automatically Created)
- customers(customer_id)
- products(product_id)
- orders(order_id)
- order_items(order_item_id)
- sales_reps(rep_id)
- sales(sale_id)

### Recommended Secondary Indexes
- customers(email) - for login lookups
- customers(signup_date) - for date-based queries
- orders(customer_id) - for customer order history
- orders(order_date) - for date-based reporting
- order_items(order_id) - for order detail lookups
- order_items(product_id) - for product sales analysis
- sales(rep_id) - for sales rep performance
- sales(sale_date) - for sales reporting

## Common Query Patterns

### Customer Analysis
- Find customers by signup date range
- Calculate customer lifetime value
- Identify top customers by order volume

### Product Analysis
- Find best-selling products
- Calculate product profitability
- Analyze product performance by category

### Sales Analysis
- Calculate sales rep performance
- Generate monthly/quarterly sales reports
- Analyze sales trends over time

### Order Analysis
- Track order status and fulfillment
- Calculate average order value
- Analyze order patterns by customer segment