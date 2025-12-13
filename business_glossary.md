# Business Glossary for E-commerce Database

## Customer Information
- **Customer ID**: Unique identifier for each customer
- **Customer Status**: Active customers are those who have made a purchase in the last 12 months
- **Customer Tier**: Premium (>$1000 annual spend), Standard ($100-$1000), Basic (<$100)

## Order Management
- **Order Status**: 
  - 'pending': Order placed but not processed
  - 'processing': Order being prepared
  - 'shipped': Order sent to customer
  - 'delivered': Order received by customer
  - 'cancelled': Order cancelled
- **Order Priority**: High priority orders are those >$500 or from Premium customers

## Product Categories
- **Electronics**: Computers, phones, tablets, accessories
- **Clothing**: Apparel, shoes, accessories
- **Home**: Furniture, appliances, decor
- **Books**: Physical and digital books
- **Sports**: Equipment, apparel, accessories

## Business Rules
- Always filter for active customers unless specifically requested otherwise
- Revenue calculations should exclude cancelled orders
- Date ranges should default to last 30 days unless specified
- Customer data is sensitive - limit personal information in results
