# Business Glossary and Query Examples

## Business Terms and Definitions

### Advanced Analytics Terms
- **Churn Risk**: Probability that a customer will stop purchasing (based on recency, frequency, monetary analysis)
- **Customer Lifetime Value (CLV)**: Total revenue expected from a customer over their entire relationship
- **Inventory Turnover**: How quickly products sell relative to stock levels (sales velocity)
- **Profit Margin**: Percentage of revenue that represents profit after costs
- **Market Penetration**: Percentage of potential customers who have made purchases
- **Revenue per Customer**: Average revenue generated per customer (CLV indicator)
- **Order Frequency**: How often customers place orders (loyalty indicator)
- **Price Tier**: Product categorization based on price points (Premium, Mid-Range, Standard, Budget)
- **Conversion Rate**: Percentage of registered customers who have placed orders
- **Customer Segmentation**: Grouping customers by behavior, value, or characteristics

### Churn Analysis Indicators
- **Never Ordered**: Registered customers who have never placed an order
- **High Risk**: No orders in 180+ days, likely to churn
- **Medium Risk**: No orders in 90-180 days, at risk of churning  
- **Low Risk**: No orders in 30-90 days, needs attention
- **Active**: Recent orders within 30 days
- **Orders per Month**: Purchase frequency since registration (engagement metric)

### Product Metrics
- **Trending Products**: Products with high order frequency or recent popularity
- **Best Selling Products**: Products with highest total quantity sold
- **Popular Products**: Products with most orders (by count)
- **High-Value Products**: Products with highest individual prices
- **Category Leaders**: Top products within each category
- **Low Stock Products**: Products with inventory below threshold (< 50 units)
- **Out of Stock**: Products with zero inventory

### Order Metrics
- **Revenue**: Total monetary value from orders (sum of total_amount)
- **Order Volume**: Total number of orders
- **Average Order Value (AOV)**: Average total_amount per order
- **Order Frequency**: How often orders are placed
- **Recent Orders**: Orders placed within last 7-30 days
- **High-Value Orders**: Orders above average order value

### Sales Performance
- **Sales by Category**: Revenue and order count grouped by product category
- **Sales Trends**: Order patterns over time periods
- **Regional Performance**: Sales performance by customer location (city, state)
- **Monthly/Quarterly Sales**: Revenue aggregated by time periods
- **Growth Rate**: Period-over-period sales increase/decrease

## Common Business Questions and SQL Patterns

### Customer Analysis Questions

**"Who are our top customers?"**
```sql
SELECT c.name, c.email, c.city, SUM(o.total_amount) as total_revenue, COUNT(o.order_id) as order_count
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 10;
```

**"Show me customers from a specific region"**
```sql
SELECT * FROM text_to_sql_demo.customers 
WHERE state = 'California' OR city = 'New York'
ORDER BY registration_date DESC;
```

**"Find customers at risk of churning"** (no recent orders)
```sql
-- Advanced churn risk analysis with multiple indicators
SELECT c.name, c.email, c.city, c.registration_date,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as lifetime_value,
       MAX(o.order_date) as last_order_date,
       date_diff('day', MAX(o.order_date), CURRENT_DATE) as days_since_last_order,
       AVG(o.total_amount) as avg_order_value,
       CASE 
           WHEN MAX(o.order_date) IS NULL THEN 'Never Ordered'
           WHEN date_diff('day', MAX(o.order_date), CURRENT_DATE) > 180 THEN 'High Risk'
           WHEN date_diff('day', MAX(o.order_date), CURRENT_DATE) > 90 THEN 'Medium Risk'
           WHEN date_diff('day', MAX(o.order_date), CURRENT_DATE) > 30 THEN 'Low Risk'
           ELSE 'Active'
       END as churn_risk_level,
       -- Calculate order frequency (orders per month since registration)
       ROUND(COUNT(o.order_id) * 30.0 / GREATEST(date_diff('day', c.registration_date, CURRENT_DATE), 1), 2) as orders_per_month
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

### Product Analysis Questions

**"What are the trending products?"**
```sql
SELECT o.product_name, o.category, COUNT(o.order_id) as order_count, SUM(o.quantity) as total_sold
FROM text_to_sql_demo.orders o
GROUP BY o.product_name, o.category
ORDER BY order_count DESC
LIMIT 10;
```

**"Which products have the highest revenue?"**
```sql
SELECT o.product_name, o.category, SUM(o.total_amount) as total_revenue, COUNT(o.order_id) as order_count
FROM text_to_sql_demo.orders o
GROUP BY o.product_name, o.category
ORDER BY total_revenue DESC
LIMIT 10;
```

**"Which products have the highest profit margins?"**
```sql
-- Advanced product profitability analysis with margin calculations
SELECT p.product_name, p.category, p.price as current_price, p.stock,
       COUNT(o.order_id) as total_orders,
       SUM(o.quantity) as total_units_sold,
       SUM(o.total_amount) as total_revenue,
       AVG(o.price) as avg_selling_price,
       -- Profit margin analysis (assuming cost is 60% of current price)
       ROUND(p.price * 0.4, 2) as estimated_profit_per_unit,
       ROUND((p.price * 0.4) / p.price * 100, 2) as estimated_margin_percentage,
       ROUND(SUM(o.quantity) * p.price * 0.4, 2) as estimated_total_profit,
       -- Performance indicators
       ROUND(SUM(o.total_amount) / NULLIF(COUNT(o.order_id), 0), 2) as revenue_per_order,
       ROUND(SUM(o.quantity) / NULLIF(COUNT(o.order_id), 0), 2) as units_per_order,
       -- Inventory turnover
       CASE 
           WHEN p.stock > 0 THEN ROUND(SUM(o.quantity) / p.stock, 2)
           ELSE NULL 
       END as inventory_turnover_ratio,
       -- Profitability ranking
       RANK() OVER (ORDER BY p.price * 0.4 DESC) as profit_margin_rank,
       RANK() OVER (ORDER BY SUM(o.quantity) * p.price * 0.4 DESC) as total_profit_rank,
       -- Price positioning
       CASE 
           WHEN p.price > 1000 THEN 'Premium'
           WHEN p.price > 500 THEN 'Mid-Range'
           WHEN p.price > 100 THEN 'Standard'
           ELSE 'Budget'
       END as price_tier
FROM text_to_sql_demo.products p
LEFT JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name
GROUP BY p.product_id, p.product_name, p.category, p.price, p.stock
HAVING total_orders > 0  -- Only show products that have been sold
ORDER BY estimated_margin_percentage DESC, total_revenue DESC
LIMIT 15;
```

**"Which products are low in stock?"**
```sql
SELECT product_name, category, stock, price, (price * stock) as inventory_value
FROM text_to_sql_demo.products
WHERE stock < 50
ORDER BY stock ASC;
```

### Sales Analysis Questions

**"What's our sales performance by category?"**
```sql
SELECT category, COUNT(order_id) as total_orders, SUM(total_amount) as total_revenue, 
       AVG(total_amount) as avg_order_value, SUM(quantity) as total_units_sold
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;
```

**"Show me recent orders"**
```sql
SELECT o.order_id, c.name as customer_name, o.product_name, o.category, o.total_amount, o.order_date
FROM text_to_sql_demo.orders o
JOIN text_to_sql_demo.customers c ON o.customer_id = c.customer_id
ORDER BY o.order_date DESC
LIMIT 20;
```

**"Compare sales performance by region"**
```sql
-- Comprehensive regional sales performance comparison
SELECT c.state, c.country,
       COUNT(DISTINCT c.customer_id) as total_customers,
       COUNT(DISTINCT CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN c.customer_id END) as active_customers_30d,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as total_revenue,
       AVG(o.total_amount) as avg_order_value,
       SUM(o.quantity) as total_units_sold,
       -- Performance metrics
       ROUND(SUM(o.total_amount) / COUNT(DISTINCT c.customer_id), 2) as revenue_per_customer,
       ROUND(COUNT(o.order_id) * 1.0 / COUNT(DISTINCT c.customer_id), 2) as orders_per_customer,
       -- Market penetration
       ROUND(COUNT(DISTINCT CASE WHEN o.order_id IS NOT NULL THEN c.customer_id END) * 100.0 / COUNT(DISTINCT c.customer_id), 2) as customer_conversion_rate,
       -- Growth indicators
       COUNT(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN o.order_id END) as orders_last_30d,
       SUM(CASE WHEN o.order_date >= CURRENT_DATE - INTERVAL '30' DAY THEN o.total_amount ELSE 0 END) as revenue_last_30d,
       -- Regional ranking
       RANK() OVER (ORDER BY SUM(o.total_amount) DESC) as revenue_rank,
       RANK() OVER (ORDER BY COUNT(o.order_id) DESC) as order_volume_rank
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.state, c.country
HAVING total_customers >= 2  -- Only show regions with multiple customers
ORDER BY total_revenue DESC;
```

### Inventory and Stock Questions

**"Show me high-value inventory"**
```sql
SELECT product_name, category, price, stock, (price * stock) as inventory_value
FROM text_to_sql_demo.products
ORDER BY inventory_value DESC
LIMIT 10;
```

**"Which products need restocking?"**
```sql
SELECT p.product_name, p.category, p.stock, p.price,
       COALESCE(SUM(o.quantity), 0) as total_sold_last_30_days
FROM text_to_sql_demo.products p
LEFT JOIN text_to_sql_demo.orders o ON p.product_name = o.product_name 
    AND o.order_date >= CURRENT_DATE - INTERVAL '30' DAY
WHERE p.stock < 20
GROUP BY p.product_name, p.category, p.stock, p.price
ORDER BY p.stock ASC;
```

## Query Optimization Guidelines

### Performance Best Practices
1. Always use LIMIT for large result sets (default: LIMIT 10)
2. Use appropriate indexes (customer_id, product_name, order_date)
3. Filter early with WHERE clauses
4. Use specific column names instead of SELECT *
5. Consider using EXPLAIN to analyze query performance

### Common Aggregation Patterns
- **COUNT()**: For counting orders, customers, products
- **SUM()**: For total revenue, quantities, amounts
- **AVG()**: For average order values, prices
- **MAX()/MIN()**: For date ranges, price ranges
- **GROUP BY**: Always group by non-aggregated columns
- **ORDER BY**: Sort results meaningfully (DESC for top results)

### Date and Time Queries
```sql
-- Orders from last 30 days
SELECT * FROM text_to_sql_demo.orders 
WHERE order_date >= CURRENT_DATE - INTERVAL '30' DAY;

-- Orders from specific month
SELECT * FROM text_to_sql_demo.orders 
WHERE EXTRACT(MONTH FROM order_date) = 12 
AND EXTRACT(YEAR FROM order_date) = 2024;

-- Monthly sales trend
SELECT EXTRACT(YEAR FROM order_date) as year,
       EXTRACT(MONTH FROM order_date) as month,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
ORDER BY year DESC, month DESC;
```

## Business Intelligence Insights

### Key Performance Indicators (KPIs)
- Total Revenue: `SUM(total_amount) FROM orders`
- Total Orders: `COUNT(order_id) FROM orders`
- Average Order Value: `AVG(total_amount) FROM orders`
- Customer Count: `COUNT(DISTINCT customer_id) FROM orders`
- Product Diversity: `COUNT(DISTINCT product_name) FROM orders`
- Active Customers: `COUNT(DISTINCT customer_id) FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL '30' DAY`

### Segmentation Strategies
- **Geographic**: Group by city, state, country
- **Product Category**: Group by category
- **Customer Value**: Segment by total_amount ranges (High: >$1000, Medium: $500-1000, Low: <$500)
- **Order Frequency**: Segment by order count per customer
- **Temporal**: Group by order_date periods (daily, weekly, monthly, quarterly)
- **Product Performance**: Segment by sales volume (Top 20%, Middle 60%, Bottom 20%)

### Advanced Analytics Patterns
```sql
-- Customer Lifetime Value Analysis
SELECT c.name, c.email, c.registration_date,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as lifetime_value,
       AVG(o.total_amount) as avg_order_value,
       MAX(o.order_date) as last_order_date,
       DATEDIFF(CURRENT_DATE, MAX(o.order_date)) as days_since_last_order
FROM text_to_sql_demo.customers c
LEFT JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.registration_date
ORDER BY lifetime_value DESC;
```