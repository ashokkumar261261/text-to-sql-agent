# SQL Query Patterns

## Customer Analysis Patterns
- **Revenue by customer**: JOIN customers + orders, SUM(total_amount), GROUP BY customer
- **Top customers**: ORDER BY revenue DESC, LIMIT N
- **Customer activity**: Use MAX(order_date) for last activity
- **Churn analysis**: Calculate days since last order using date_diff()

## Product Analysis Patterns  
- **Product performance**: GROUP BY product_name, COUNT orders or SUM revenue
- **Trending products**: Add date filter for recent period
- **Profit margins**: Compare orders.price vs products.price for margin analysis
- **Category analysis**: GROUP BY category
- **Inventory analysis**: Use products.stock for availability
- **Supplier analysis**: GROUP BY supplier from products table

## Product-Order Relationships
- **Sales vs current price**: JOIN orders + products ON product_name
- **Historical pricing**: Use orders.price for historical, products.price for current
- **Stock levels**: Use products.stock for inventory queries
- **Product profitability**: Compare order price vs current price

## Regional Analysis Patterns
- **Sales by region**: GROUP BY state/city from customers table
- **Regional performance**: JOIN customers + orders, GROUP BY state
- **Regional product preferences**: JOIN all three tables, GROUP BY state + product

## Time-Based Patterns
- **Recent data**: Use date_add('day', -N, CURRENT_DATE) for last N days
- **This month**: Use date_add('day', -30, CURRENT_DATE)
- **Date differences**: Use date_diff('day', start_date, end_date)

## Three-Table Join Patterns
- **Complete analysis**: customers + orders + products
- **Customer product preferences**: JOIN all tables, GROUP BY customer + category
- **Regional product performance**: JOIN all tables, GROUP BY state + product_name

## Standard SQL Rules
- Always prefix tables: text_to_sql_demo.table_name
- Use 'Delivered' status for revenue calculations
- Include all non-aggregate SELECT columns in GROUP BY
- Use meaningful column aliases (total_revenue, order_count, etc.)
- Handle NULLs with NULLS FIRST/LAST in ORDER BY
- Join products table when analyzing current prices, stock, or suppliers