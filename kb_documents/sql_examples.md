# SQL Query Examples for Text-to-SQL Agent

## Database Schema Reference
- **Database**: text_to_sql_demo
- **Tables**: customers, orders, products
- **Key Join**: customers.customer_id = orders.customer_id
- **Key Join**: products.product_name = orders.product_name

## Basic Query Examples

### Simple Selection Queries
```sql
-- Show all customers
SELECT * FROM text_to_sql_demo.customers LIMIT 10;

-- Show all products
SELECT * FROM text_to_sql_demo.products LIMIT 10;

-- Show all orders
SELECT * FROM text_to_sql_demo.orders LIMIT 10;

-- Products in specific category
SELECT * FROM text_to_sql_demo.products WHERE category = 'Electronics';

-- Orders with high value
SELECT * FROM text_to_sql_demo.orders WHERE total_amount > 1000;

-- Recent orders (last 30 days)
SELECT * FROM text_to_sql_demo.orders 
WHERE order_date >= CURRENT_DATE - INTERVAL '30' DAY
ORDER BY order_date DESC;
```

### Customer Analysis Queries

```sql
-- Top 5 customers by revenue
SELECT c.name, c.email, c.city, SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;

-- Customers with most orders
SELECT c.name, c.email, COUNT(o.order_id) as order_count, SUM(o.total_amount) as total_spent
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email
ORDER BY order_count DESC
LIMIT 10;

-- Customers from specific location
SELECT name, email, city, state, registration_date
FROM text_to_sql_demo.customers
WHERE state = 'California'
ORDER BY registration_date DESC;

-- Customer lifetime value analysis
SELECT c.name, c.email, c.city, c.registration_date,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as lifetime_value,
       AVG(o.total_amount) as avg_order_value,
       MAX(o.order_date) as last_order_date
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city, c.registration_date
ORDER BY lifetime_value DESC;

-- Customers at risk of churning (no orders in 90+ days)
SELECT c.name, c.email, c.city, c.registration_date,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as lifetime_value,
       MAX(o.order_date) as last_order_date,
       DATEDIFF(CURRENT_DATE, MAX(o.order_date)) as days_since_last_order,
       AVG(o.total_amount) as avg_order_value,
       CASE 
           WHEN MAX(o.order_date) IS NULL THEN 'Never Ordered'
           WHEN DATEDIFF(CURRENT_DATE, MAX(o.order_date)) > 180 THEN 'High Risk'
           WHEN DATEDIFF(CURRENT_DATE, MAX(o.order_date)) > 90 THEN 'Medium Risk'
           WHEN DATEDIFF(CURRENT_DATE, MAX(o.order_date)) > 30 THEN 'Low Risk'
           ELSE 'Active'
       END as churn_risk_level,
       ROUND(COUNT(o.order_id) * 30.0 / GREATEST(DATEDIFF(CURRENT_DATE, c.registration_date), 1), 2) as orders_per_month
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city, c.registration_date
HAVING churn_risk_level IN ('High Risk', 'Medium Risk', 'Never Ordered')
ORDER BY 
    CASE churn_risk_level 
        WHEN 'Never Ordered' THEN 1
        WHEN 'High Risk' THEN 2
        WHEN 'Medium Risk' THEN 3
    END,
    lifetime_value DESC;
```

### Product Performance Queries

```sql
-- Trending products (most ordered)
SELECT o.product_name, o.category, COUNT(o.order_id) as order_count, SUM(o.quantity) as total_sold
FROM text_to_sql_demo.orders o
GROUP BY o.product_name, o.category
ORDER BY order_count DESC
LIMIT 10;

-- Products by revenue
SELECT o.product_name, o.category, SUM(o.total_amount) as total_revenue, COUNT(o.order_id) as order_count
FROM text_to_sql_demo.orders o
GROUP BY o.product_name, o.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Products with inventory details
SELECT p.product_name, p.category, p.price, p.stock, 
       COALESCE(SUM(o.quantity), 0) as total_sold,
       (p.price * p.stock) as inventory_value
FROM text_to_sql_demo.products p
LEFT JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name
GROUP BY p.product_id, p.product_name, p.category, p.price, p.stock
ORDER BY total_sold DESC;

-- Low stock products that need restocking
SELECT p.product_name, p.category, p.stock, p.price,
       COALESCE(SUM(o.quantity), 0) as total_sold_last_30_days
FROM text_to_sql_demo.products p
LEFT JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name 
    AND o.order_date >= CURRENT_DATE - INTERVAL '30' DAY
WHERE p.stock < 50
GROUP BY p.product_name, p.category, p.stock, p.price
ORDER BY p.stock ASC;

-- Products with highest profit margins (assuming cost analysis)
SELECT p.product_name, p.category, p.price as current_price, p.stock,
       COUNT(o.order_id) as total_orders,
       SUM(o.quantity) as total_units_sold,
       SUM(o.total_amount) as total_revenue,
       AVG(o.price) as avg_selling_price,
       ROUND(p.price * 0.4, 2) as estimated_profit_per_unit,
       ROUND((p.price * 0.4) / p.price * 100, 2) as estimated_margin_percentage,
       ROUND(SUM(o.quantity) * p.price * 0.4, 2) as estimated_total_profit,
       ROUND(SUM(o.total_amount) / NULLIF(COUNT(o.order_id), 0), 2) as revenue_per_order,
       CASE 
           WHEN p.stock > 0 THEN ROUND(SUM(o.quantity) / p.stock, 2)
           ELSE NULL 
       END as inventory_turnover_ratio,
       CASE 
           WHEN p.price > 1000 THEN 'Premium'
           WHEN p.price > 500 THEN 'Mid-Range'
           WHEN p.price > 100 THEN 'Standard'
           ELSE 'Budget'
       END as price_tier
FROM text_to_sql_demo.products p
LEFT JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name
GROUP BY p.product_id, p.product_name, p.category, p.price, p.stock
HAVING total_orders > 0
ORDER BY estimated_margin_percentage DESC, total_revenue DESC
LIMIT 15;
```

### Sales Analysis Queries

```sql
-- Sales by category
SELECT category, COUNT(order_id) as total_orders, SUM(total_amount) as total_revenue, 
       AVG(total_amount) as avg_order_value, SUM(quantity) as total_units_sold
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;

-- Monthly sales trend
SELECT EXTRACT(YEAR FROM order_date) as year, 
       EXTRACT(MONTH FROM order_date) as month,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as total_revenue,
       AVG(total_amount) as avg_order_value
FROM text_to_sql_demo.orders
GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
ORDER BY year DESC, month DESC;

-- Recent high-value orders
SELECT o.order_id, c.name as customer_name, o.product_name, o.category, o.total_amount, o.order_date
FROM text_to_sql_demo.orders o
JOIN text_to_sql_demo.customers c ON o.customer_id = c.customer_id
WHERE o.total_amount > 500
ORDER BY o.order_date DESC
LIMIT 20;

-- Regional sales performance with comprehensive metrics
SELECT c.state, c.country,
       COUNT(DISTINCT c.customer_id) as total_customers,
       COUNT(DISTINCT CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN c.customer_id END) as active_customers_30d,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as total_revenue,
       AVG(o.total_amount) as avg_order_value,
       SUM(o.quantity) as total_units_sold,
       ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) as revenue_per_customer,
       ROUND(COUNT(o.order_id) * 1.0 / COUNT(DISTINCT c.customer_id), 2) as orders_per_customer,
       ROUND(COUNT(DISTINCT CASE WHEN o.order_id IS NOT NULL THEN c.customer_id END) * 100.0 / COUNT(DISTINCT c.customer_id), 2) as customer_conversion_rate,
       COUNT(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN o.order_id END) as orders_last_30d,
       SUM(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN o.total_amount ELSE 0 END) as revenue_last_30d,
       RANK() OVER (ORDER BY SUM(o.total_amount) DESC) as revenue_rank
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.state, c.country
HAVING total_customers >= 2
ORDER BY total_revenue DESC;
```

### Complex Business Intelligence Queries

```sql
-- Product performance by category with rankings
SELECT p.category,
       COUNT(DISTINCT p.product_name) as products_in_category,
       COUNT(o.order_id) as total_orders,
       SUM(o.quantity) as total_quantity_sold,
       SUM(o.total_amount) as total_revenue,
       AVG(o.total_amount) as avg_order_value,
       RANK() OVER (ORDER BY SUM(o.total_amount) DESC) as revenue_rank
FROM text_to_sql_demo.products p
LEFT JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Customer segmentation by purchase behavior
SELECT 
    CASE 
        WHEN SUM(o.total_amount) > 5000 THEN 'VIP Customer'
        WHEN SUM(o.total_amount) > 2000 THEN 'High-Value Customer'
        WHEN SUM(o.total_amount) > 500 THEN 'Regular Customer'
        ELSE 'Low-Value Customer'
    END as customer_segment,
    COUNT(DISTINCT c.customer_id) as customer_count,
    AVG(SUM(o.total_amount)) as avg_lifetime_value
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
GROUP BY customer_segment
ORDER BY avg_lifetime_value DESC;

-- Top performing products with growth analysis
SELECT o.product_name, o.category,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as total_revenue,
       COUNT(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN 1 END) as recent_orders,
       SUM(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN o.total_amount ELSE 0 END) as recent_revenue
FROM text_to_sql_demo.orders o
GROUP BY o.product_name, o.category
HAVING total_orders >= 5
ORDER BY total_revenue DESC
LIMIT 15;
```

## Query Pattern Guidelines

### For "Top N" Questions
- Always use ORDER BY with DESC for highest values
- Include LIMIT clause
- Use appropriate aggregation (SUM for revenue, COUNT for frequency)

### For "Trending" Questions
- Focus on order frequency: COUNT(order_id)
- Group by product_name and category
- Order by count DESC
- Consider time-based filtering for recent trends

### For "Customer" Questions
- Join customers and orders tables on customer_id
- Aggregate by customer attributes
- Include customer details (name, email, location)
- Consider customer lifetime value calculations

### For "Product" Questions
- Use orders table for sales data
- Join with products table for inventory info
- Group by product_name and category
- Include stock levels and pricing information

### For "Revenue" Questions
- Use SUM(total_amount) for revenue calculations
- Group by relevant dimensions (customer, product, category, time)
- Include COUNT for order volume context
- Consider time-based comparisons

## Common Query Transformations

### Natural Language → SQL Mapping

| Natural Language | SQL Pattern |
|------------------|-------------|
| "Show me all customers" | `SELECT * FROM text_to_sql_demo.customers LIMIT 10;` |
| "Top 5 customers by revenue" | `SELECT c.*, SUM(o.total_amount) as revenue FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY revenue DESC LIMIT 5;` |
| "Trending products" | `SELECT product_name, COUNT(order_id) as orders FROM text_to_sql_demo.orders GROUP BY product_name ORDER BY orders DESC LIMIT 10;` |
| "Electronics products" | `SELECT * FROM text_to_sql_demo.products WHERE category = 'Electronics';` |
| "Recent orders" | `SELECT * FROM text_to_sql_demo.orders ORDER BY order_date DESC LIMIT 20;` |
| "Sales by category" | `SELECT category, SUM(total_amount) as revenue FROM text_to_sql_demo.orders GROUP BY category ORDER BY revenue DESC;` |
| "Customers at risk" | `SELECT c.name, MAX(o.order_date) as last_order FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id HAVING DATEDIFF(CURRENT_DATE, MAX(o.order_date)) > 90;` |
| "Low stock products" | `SELECT * FROM text_to_sql_demo.products WHERE stock < 50 ORDER BY stock ASC;` |

## Performance Optimization Tips

1. **Always use LIMIT**: Prevent large result sets (default: LIMIT 10)
2. **Specific columns**: Use SELECT column_list instead of SELECT *
3. **Efficient JOINs**: Use appropriate join conditions
4. **WHERE clauses**: Filter data early in the query
5. **Proper GROUP BY**: Include all non-aggregated columns
6. **Meaningful ORDER BY**: Sort results logically
7. **Index usage**: Leverage customer_id, product_name, order_date indexes
8. **Date filtering**: Use proper date functions and intervals