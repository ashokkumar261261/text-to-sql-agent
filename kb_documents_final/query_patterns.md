# Query Patterns and Best Practices

## Common Business Questions and SQL Patterns

### Revenue and Sales Analysis

#### "Show me top customers by revenue"
**Pattern**: Customer aggregation with revenue calculation
```sql
SELECT 
    c.customer_name,
    SUM(o.total_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;
```

#### "What are our monthly sales trends?"
**Pattern**: Time-based aggregation with date functions
```sql
SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(total_amount) as monthly_revenue,
    COUNT(*) as order_count
FROM orders
WHERE status = 'delivered'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;
```

#### "Which products generate the most profit?"
**Pattern**: Product profitability with cost calculation
```sql
SELECT 
    p.product_name,
    SUM(oi.quantity) as units_sold,
    SUM(oi.line_total) as revenue,
    SUM(oi.quantity * p.cost) as total_cost,
    SUM(oi.line_total) - SUM(oi.quantity * p.cost) as profit
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
GROUP BY p.product_id, p.product_name
ORDER BY profit DESC;
```

### Customer Analysis

#### "Find customers who haven't ordered recently"
**Pattern**: Customer activity analysis with date comparisons
```sql
SELECT 
    c.customer_name,
    c.email,
    MAX(o.order_date) as last_order_date,
    CURRENT_DATE - MAX(o.order_date) as days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.email
WHERE MAX(o.order_date) < CURRENT_DATE - INTERVAL '90' DAY
    OR MAX(o.order_date) IS NULL
ORDER BY days_since_last_order DESC;
```

#### "What's the average order value by customer segment?"
**Pattern**: Customer segmentation with conditional aggregation
```sql
SELECT 
    CASE 
        WHEN order_count >= 10 THEN 'High Value'
        WHEN order_count >= 5 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    AVG(avg_order_value) as segment_avg_order_value,
    COUNT(*) as customers_in_segment
FROM (
    SELECT 
        c.customer_id,
        COUNT(o.order_id) as order_count,
        AVG(o.total_amount) as avg_order_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'delivered'
    GROUP BY c.customer_id
) customer_stats
GROUP BY customer_segment;
```

### Product Performance

#### "Which products are selling best this quarter?"
**Pattern**: Product performance with time filtering
```sql
SELECT 
    p.product_name,
    p.category,
    SUM(oi.quantity) as units_sold,
    SUM(oi.line_total) as revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'delivered'
    AND o.order_date >= DATE_TRUNC('quarter', CURRENT_DATE)
GROUP BY p.product_id, p.product_name, p.category
ORDER BY units_sold DESC;
```

#### "Show me product performance by category"
**Pattern**: Category-level aggregation
```sql
SELECT 
    category,
    COUNT(DISTINCT product_id) as product_count,
    SUM(units_sold) as total_units_sold,
    SUM(revenue) as total_revenue,
    AVG(revenue) as avg_product_revenue
FROM (
    SELECT 
        p.product_id,
        p.category,
        SUM(oi.quantity) as units_sold,
        SUM(oi.line_total) as revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'delivered'
    GROUP BY p.product_id, p.category
) product_stats
GROUP BY category
ORDER BY total_revenue DESC;
```

### Sales Team Performance

#### "How are our sales reps performing against quota?"
**Pattern**: Sales rep performance with quota comparison
```sql
SELECT 
    sr.rep_name,
    sr.territory,
    sr.quota,
    COALESCE(SUM(s.sale_amount), 0) as actual_sales,
    ROUND((COALESCE(SUM(s.sale_amount), 0) / sr.quota) * 100, 2) as quota_achievement
FROM sales_reps sr
LEFT JOIN sales s ON sr.rep_id = s.rep_id
    AND s.sale_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY sr.rep_id, sr.rep_name, sr.territory, sr.quota
ORDER BY quota_achievement DESC;
```

#### "Which territory is generating the most revenue?"
**Pattern**: Territory-based aggregation
```sql
SELECT 
    sr.territory,
    COUNT(DISTINCT sr.rep_id) as rep_count,
    SUM(s.sale_amount) as territory_revenue,
    AVG(s.sale_amount) as avg_sale_amount
FROM sales_reps sr
JOIN sales s ON sr.rep_id = s.rep_id
WHERE s.sale_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY sr.territory
ORDER BY territory_revenue DESC;
```

## Advanced Query Patterns

### Cohort Analysis
**Pattern**: Customer behavior analysis over time
```sql
SELECT 
    signup_month,
    months_since_signup,
    COUNT(DISTINCT customer_id) as active_customers,
    SUM(revenue) as cohort_revenue
FROM (
    SELECT 
        c.customer_id,
        DATE_TRUNC('month', c.signup_date) as signup_month,
        DATE_TRUNC('month', o.order_date) as order_month,
        EXTRACT(month FROM AGE(o.order_date, c.signup_date)) as months_since_signup,
        o.total_amount as revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'delivered'
) cohort_data
GROUP BY signup_month, months_since_signup
ORDER BY signup_month, months_since_signup;
```

### Running Totals
**Pattern**: Cumulative calculations using window functions
```sql
SELECT 
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (ORDER BY order_date) as running_total
FROM (
    SELECT 
        order_date,
        SUM(total_amount) as daily_revenue
    FROM orders
    WHERE status = 'delivered'
    GROUP BY order_date
) daily_sales
ORDER BY order_date;
```

### Ranking and Percentiles
**Pattern**: Competitive analysis with ranking functions
```sql
SELECT 
    product_name,
    category,
    revenue,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) as category_rank,
    PERCENT_RANK() OVER (ORDER BY revenue DESC) as revenue_percentile
FROM (
    SELECT 
        p.product_name,
        p.category,
        SUM(oi.line_total) as revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'delivered'
    GROUP BY p.product_id, p.product_name, p.category
) product_revenue
ORDER BY category, category_rank;
```

## Query Optimization Guidelines

### 1. Use Appropriate WHERE Clauses
- Always filter on indexed columns first
- Use date ranges instead of functions on date columns
- Apply most selective filters first

### 2. Efficient JOINs
- Use INNER JOIN when you only need matching records
- Use LEFT JOIN when you need all records from the left table
- Ensure JOIN conditions use indexed columns

### 3. GROUP BY Best Practices
- Include all non-aggregated columns in GROUP BY
- Use HAVING for filtering aggregated results
- Consider using window functions instead of subqueries

### 4. Subquery vs JOIN Performance
```sql
-- Often more efficient: JOIN
SELECT c.customer_name, o.order_count
FROM customers c
JOIN (
    SELECT customer_id, COUNT(*) as order_count
    FROM orders
    GROUP BY customer_id
) o ON c.customer_id = o.customer_id;

-- May be less efficient: Correlated subquery
SELECT 
    customer_name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count
FROM customers c;
```

### 5. LIMIT and Pagination
```sql
-- For pagination, use OFFSET with LIMIT
SELECT * FROM orders 
ORDER BY order_date DESC 
LIMIT 20 OFFSET 40;  -- Page 3, 20 records per page
```

## Common Anti-Patterns to Avoid

### 1. Functions in WHERE Clauses
```sql
-- Avoid: Prevents index usage
WHERE EXTRACT(year FROM order_date) = 2023

-- Better: Use date ranges
WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'
```

### 2. SELECT * in Production Queries
```sql
-- Avoid: Retrieves unnecessary data
SELECT * FROM orders WHERE customer_id = 123

-- Better: Select only needed columns
SELECT order_id, order_date, total_amount FROM orders WHERE customer_id = 123
```

### 3. Unnecessary DISTINCT
```sql
-- Avoid: DISTINCT when not needed
SELECT DISTINCT customer_name FROM customers

-- Better: Only use DISTINCT when duplicates are possible
SELECT customer_name FROM customers  -- customer_name is already unique per customer
```

### 4. Inefficient Subqueries
```sql
-- Avoid: Correlated subquery in SELECT
SELECT 
    customer_name,
    (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.customer_id)
FROM customers c

-- Better: Use JOIN
SELECT 
    c.customer_name,
    COALESCE(SUM(o.total_amount), 0) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
```

## Data Quality Checks

### Find Orphaned Records
```sql
-- Orders without customers
SELECT * FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Order items without orders
SELECT * FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;
```

### Identify Data Inconsistencies
```sql
-- Orders with total_amount not matching sum of line items
SELECT 
    o.order_id,
    o.total_amount as order_total,
    SUM(oi.line_total) as calculated_total,
    ABS(o.total_amount - SUM(oi.line_total)) as difference
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.total_amount
WHERE ABS(o.total_amount - SUM(oi.line_total)) > 0.01;
```