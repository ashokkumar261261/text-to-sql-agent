# Database Schema Documentation

## Table: customers
**Description**: Contains information about all customers in the system

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| customer_id | INTEGER | Unique identifier for each customer | PRIMARY KEY, NOT NULL |
| customer_name | VARCHAR(255) | Full name of the customer | NOT NULL |
| email | VARCHAR(255) | Customer's email address | UNIQUE, NOT NULL |
| phone | VARCHAR(20) | Customer's phone number | |
| address | TEXT | Customer's physical address | |
| signup_date | DATE | Date when customer registered | NOT NULL |
| status | VARCHAR(20) | Customer status (active, inactive) | DEFAULT 'active' |

**Sample Data**:
```
customer_id: 1, customer_name: "John Smith", email: "john@email.com", signup_date: "2023-01-15"
customer_id: 2, customer_name: "Jane Doe", email: "jane@email.com", signup_date: "2023-02-20"
```

## Table: products
**Description**: Contains information about all products available for sale

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| product_id | INTEGER | Unique identifier for each product | PRIMARY KEY, NOT NULL |
| product_name | VARCHAR(255) | Name of the product | NOT NULL |
| description | TEXT | Detailed product description | |
| category | VARCHAR(100) | Product category | NOT NULL |
| price | DECIMAL(10,2) | Current selling price | NOT NULL, CHECK (price >= 0) |
| cost | DECIMAL(10,2) | Cost to produce/acquire the product | CHECK (cost >= 0) |
| status | VARCHAR(20) | Product status (active, discontinued) | DEFAULT 'active' |

**Sample Data**:
```
product_id: 1, product_name: "Laptop Pro", category: "Electronics", price: 1299.99, cost: 800.00
product_id: 2, product_name: "Wireless Mouse", category: "Electronics", price: 29.99, cost: 15.00
```

## Table: orders
**Description**: Contains information about customer orders

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| order_id | INTEGER | Unique identifier for each order | PRIMARY KEY, NOT NULL |
| customer_id | INTEGER | Reference to customer who placed the order | FOREIGN KEY REFERENCES customers(customer_id) |
| order_date | DATE | Date when the order was placed | NOT NULL |
| total_amount | DECIMAL(10,2) | Total value of the order | NOT NULL, CHECK (total_amount >= 0) |
| status | VARCHAR(20) | Order status (pending, shipped, delivered, cancelled) | DEFAULT 'pending' |
| shipping_address | TEXT | Address where order should be delivered | |
| payment_method | VARCHAR(50) | Method used for payment | |

**Sample Data**:
```
order_id: 1001, customer_id: 1, order_date: "2023-03-15", total_amount: 1329.98, status: "delivered"
order_id: 1002, customer_id: 2, order_date: "2023-03-20", total_amount: 59.98, status: "shipped"
```

## Table: order_items
**Description**: Contains details about individual items within each order

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| order_item_id | INTEGER | Unique identifier for each order item | PRIMARY KEY, NOT NULL |
| order_id | INTEGER | Reference to the order | FOREIGN KEY REFERENCES orders(order_id) |
| product_id | INTEGER | Reference to the product | FOREIGN KEY REFERENCES products(product_id) |
| quantity | INTEGER | Number of units ordered | NOT NULL, CHECK (quantity > 0) |
| unit_price | DECIMAL(10,2) | Price per unit at time of order | NOT NULL, CHECK (unit_price >= 0) |
| line_total | DECIMAL(10,2) | Total for this line item (quantity * unit_price) | NOT NULL |

**Sample Data**:
```
order_item_id: 1, order_id: 1001, product_id: 1, quantity: 1, unit_price: 1299.99, line_total: 1299.99
order_item_id: 2, order_id: 1001, product_id: 2, quantity: 1, unit_price: 29.99, line_total: 29.99
```

## Table: sales_reps
**Description**: Contains information about sales representatives

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| rep_id | INTEGER | Unique identifier for each sales rep | PRIMARY KEY, NOT NULL |
| rep_name | VARCHAR(255) | Full name of the sales representative | NOT NULL |
| email | VARCHAR(255) | Sales rep's email address | UNIQUE, NOT NULL |
| territory | VARCHAR(100) | Geographic territory assigned | |
| hire_date | DATE | Date when rep was hired | NOT NULL |
| quota | DECIMAL(10,2) | Monthly sales quota | CHECK (quota >= 0) |
| commission_rate | DECIMAL(5,4) | Commission rate (as decimal, e.g., 0.05 for 5%) | CHECK (commission_rate >= 0 AND commission_rate <= 1) |

**Sample Data**:
```
rep_id: 1, rep_name: "Alice Johnson", territory: "North", quota: 50000.00, commission_rate: 0.05
rep_id: 2, rep_name: "Bob Wilson", territory: "South", quota: 45000.00, commission_rate: 0.04
```

## Table: sales
**Description**: Contains sales transaction records

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|-------------|
| sale_id | INTEGER | Unique identifier for each sale | PRIMARY KEY, NOT NULL |
| order_id | INTEGER | Reference to the order | FOREIGN KEY REFERENCES orders(order_id) |
| rep_id | INTEGER | Reference to sales representative | FOREIGN KEY REFERENCES sales_reps(rep_id) |
| sale_date | DATE | Date of the sale | NOT NULL |
| sale_amount | DECIMAL(10,2) | Total amount of the sale | NOT NULL, CHECK (sale_amount >= 0) |
| commission_amount | DECIMAL(10,2) | Commission earned by rep | CHECK (commission_amount >= 0) |

**Sample Data**:
```
sale_id: 1, order_id: 1001, rep_id: 1, sale_date: "2023-03-15", sale_amount: 1329.98, commission_amount: 66.50
sale_id: 2, order_id: 1002, rep_id: 2, sale_date: "2023-03-20", sale_amount: 59.98, commission_amount: 2.40
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