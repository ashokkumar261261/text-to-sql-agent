# SQL Query Examples and Patterns

## Customer Queries

### Find Top Customers by Revenue
```sql
SELECT 
    c.customer_name,
    c.email,
    SUM(o.total_amount) as total_revenue,
    COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.customer_name, c.email
ORDER BY total_revenue DESC
LIMIT 10;
```

### Find New Customers This Month
```sql
SELECT 
    customer_name,
    email,
    signup_date
FROM customers
WHERE signup_date >= DATE_TRUNC('month', CURRENT_DATE)
ORDER BY signup_date DESC;
```

### Customer Order History
```sql
SELECT 
    c.customer_name,
    o.order_id,
    o.order_date,
    o.total_amount,
    o.status
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_name LIKE '%Smith%'
ORDER BY o.order_date DESC;
```

### Customers with No Orders
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL
ORDER BY c.signup_date DESC;
```

## Product Queries

### Best Selling Products
```sql
SELECT 
    p.product_name,
    p.category,
    SUM(oi.quantity) as total_sold,
    SUM(oi.line_total) as total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_sold DESC
LIMIT 20;
```

### Product Profitability Analysis
```sql
SELECT 
    p.product_name,
    p.category,
    p.price,
    p.cost,
    (p.price - p.cost) as profit_per_unit,
    ROUND(((p.price - p.cost) / p.price) * 100, 2) as profit_margin_percent,
    SUM(oi.quantity) as units_sold,
    SUM(oi.line_total) as total_revenue,
    SUM(oi.quantity * p.cost) as total_cost,
    SUM(oi.line_total) - SUM(oi.quantity * p.cost) as total_profit
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p.product_id, p.product_name, p.category, p.price, p.cost
ORDER BY total_profit DESC;
```

### Products by Category Performance
```sql
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) as product_count,
    SUM(oi.quantity) as total_units_sold,
    SUM(oi.line_total) as total_revenue,
    AVG(oi.unit_price) as avg_selling_price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p.category
ORDER BY total_revenue DESC;
```

## Sales and Revenue Queries

### Monthly Sales Report
```sql
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
WHERE o.status = 'delivered'
    AND o.order_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;
```

### Sales Rep Performance
```sql
SELECT 
    sr.rep_name,
    sr.territory,
    sr.quota,
    COUNT(s.sale_id) as sales_count,
    SUM(s.sale_amount) as total_sales,
    SUM(s.commission_amount) as total_commission,
    ROUND((SUM(s.sale_amount) / sr.quota) * 100, 2) as quota_achievement_percent
FROM sales_reps sr
LEFT JOIN sales s ON sr.rep_id = s.rep_id
    AND s.sale_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY sr.rep_id, sr.rep_name, sr.territory, sr.quota
ORDER BY total_sales DESC;
```

### Daily Sales Trend
```sql
SELECT 
    o.order_date,
    COUNT(o.order_id) as orders,
    SUM(o.total_amount) as revenue,
    AVG(o.total_amount) as avg_order_value
FROM orders o
WHERE o.status = 'delivered'
    AND o.order_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY o.order_date
ORDER BY o.order_date;
```

### Year-over-Year Growth
```sql
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    SUM(CASE WHEN EXTRACT(year FROM o.order_date) = EXTRACT(year FROM CURRENT_DATE) 
        THEN o.total_amount ELSE 0 END) as current_year_revenue,
    SUM(CASE WHEN EXTRACT(year FROM o.order_date) = EXTRACT(year FROM CURRENT_DATE) - 1 
        THEN o.total_amount ELSE 0 END) as previous_year_revenue
FROM orders o
WHERE o.status = 'delivered'
    AND o.order_date >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1' YEAR
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;
```

## Order Analysis Queries

### Average Order Value by Customer Segment
```sql
SELECT 
    CASE 
        WHEN total_orders >= 10 THEN 'High Frequency'
        WHEN total_orders >= 5 THEN 'Medium Frequency'
        ELSE 'Low Frequency'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(avg_order_value) as segment_avg_order_value,
    SUM(total_revenue) as segment_total_revenue
FROM (
    SELECT 
        c.customer_id,
        c.customer_name,
        COUNT(o.order_id) as total_orders,
        AVG(o.total_amount) as avg_order_value,
        SUM(o.total_amount) as total_revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'delivered'
    GROUP BY c.customer_id, c.customer_name
) customer_stats
GROUP BY customer_segment
ORDER BY segment_total_revenue DESC;
```

### Order Status Distribution
```sql
SELECT 
    status,
    COUNT(*) as order_count,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()), 2) as percentage
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY status
ORDER BY order_count DESC;
```

### Large Orders Analysis
```sql
SELECT 
    o.order_id,
    c.customer_name,
    o.order_date,
    o.total_amount,
    COUNT(oi.order_item_id) as item_count,
    STRING_AGG(p.product_name, ', ') as products
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.total_amount > 1000
GROUP BY o.order_id, c.customer_name, o.order_date, o.total_amount
ORDER BY o.total_amount DESC
LIMIT 20;
```

## Time-Based Analysis

### Seasonal Sales Patterns
```sql
SELECT 
    EXTRACT(month FROM o.order_date) as month,
    EXTRACT(quarter FROM o.order_date) as quarter,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM orders o
WHERE o.status = 'delivered'
    AND o.order_date >= CURRENT_DATE - INTERVAL '2' YEAR
GROUP BY EXTRACT(month FROM o.order_date), EXTRACT(quarter FROM o.order_date)
ORDER BY month;
```

### Weekly Sales Performance
```sql
SELECT 
    DATE_TRUNC('week', o.order_date) as week_start,
    COUNT(o.order_id) as orders,
    SUM(o.total_amount) as revenue,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
WHERE o.status = 'delivered'
    AND o.order_date >= CURRENT_DATE - INTERVAL '12' WEEK
GROUP BY DATE_TRUNC('week', o.order_date)
ORDER BY week_start;
```

## Complex Business Intelligence Queries

### Customer Lifetime Value
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    c.signup_date,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as lifetime_value,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    CURRENT_DATE - MAX(o.order_date) as days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'delivered'
GROUP BY c.customer_id, c.customer_name, c.signup_date
ORDER BY lifetime_value DESC NULLS LAST;
```

### Product Cross-Sell Analysis
```sql
SELECT 
    p1.product_name as product_1,
    p2.product_name as product_2,
    COUNT(*) as times_bought_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
JOIN orders o ON oi1.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p1.product_id, p1.product_name, p2.product_id, p2.product_name
ORDER BY times_bought_together DESC
LIMIT 20;
```

### Customer Retention Analysis
```sql
SELECT 
    signup_month,
    customer_count,
    customers_with_orders,
    ROUND((customers_with_orders * 100.0 / customer_count), 2) as retention_rate
FROM (
    SELECT 
        DATE_TRUNC('month', c.signup_date) as signup_month,
        COUNT(c.customer_id) as customer_count,
        COUNT(o.customer_id) as customers_with_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id 
        AND o.order_date > c.signup_date + INTERVAL '30' DAY
        AND o.status = 'delivered'
    WHERE c.signup_date >= CURRENT_DATE - INTERVAL '12' MONTH
    GROUP BY DATE_TRUNC('month', c.signup_date)
) retention_stats
ORDER BY signup_month;
```

## Query Optimization Tips

### Use Proper Indexes
- Always filter on indexed columns when possible
- Use composite indexes for multi-column WHERE clauses
- Consider covering indexes for frequently accessed columns

### Efficient Date Filtering
```sql
-- Good: Uses index on order_date
WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'

-- Avoid: Functions on columns prevent index usage
WHERE EXTRACT(year FROM order_date) = 2023
```

### Limit Result Sets
```sql
-- Always use LIMIT for large result sets
SELECT * FROM orders ORDER BY order_date DESC LIMIT 100;
```

### Use EXISTS Instead of IN for Subqueries
```sql
-- More efficient
SELECT * FROM customers c 
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

-- Less efficient for large datasets
SELECT * FROM customers c 
WHERE c.customer_id IN (SELECT customer_id FROM orders);
```