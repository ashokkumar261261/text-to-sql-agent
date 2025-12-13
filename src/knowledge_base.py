import boto3
import json
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class BedrockKnowledgeBase:
    """
    Amazon Bedrock Knowledge Base integration for enhanced SQL generation.
    Provides domain-specific context, business rules, and query patterns.
    """
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.knowledge_base_id = os.getenv('BEDROCK_KNOWLEDGE_BASE_ID')
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        
        # Initialize Bedrock clients
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=self.region)
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=self.region)
        
        # Knowledge base configuration
        self.max_results = int(os.getenv('KB_MAX_RESULTS', '10'))
        self.confidence_threshold = float(os.getenv('KB_CONFIDENCE_THRESHOLD', '0.7'))
        
    def query_knowledge_base(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Query the Bedrock Knowledge Base for relevant information.
        
        Args:
            query: Natural language query
            filters: Optional metadata filters
            
        Returns:
            List of relevant knowledge base entries
        """
        if not self.knowledge_base_id:
            logger.warning("Knowledge Base ID not configured")
            return []
        
        try:
            request_params = {
                'knowledgeBaseId': self.knowledge_base_id,
                'retrievalQuery': {
                    'text': query
                },
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': self.max_results
                    }
                }
            }
            
            # Add filters if provided
            if filters:
                request_params['retrievalConfiguration']['vectorSearchConfiguration']['filter'] = filters
            
            response = self.bedrock_agent_runtime.retrieve(
                **request_params
            )
            
            # Filter results by confidence score
            relevant_results = []
            for result in response.get('retrievalResults', []):
                confidence = result.get('score', 0)
                if confidence >= self.confidence_threshold:
                    relevant_results.append({
                        'content': result['content']['text'],
                        'confidence': confidence,
                        'metadata': result.get('metadata', {}),
                        'location': result.get('location', {})
                    })
            
            return relevant_results
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return []
    
    def get_enhanced_context(self, natural_language_query: str, schema_context: str) -> str:
        """
        Get enhanced context by combining schema with knowledge base information.
        
        Args:
            natural_language_query: User's natural language query
            schema_context: Database schema context
            
        Returns:
            Enhanced context string with knowledge base information
        """
        # Query knowledge base for relevant information
        kb_results = self.query_knowledge_base(natural_language_query)
        
        if not kb_results:
            return schema_context
        
        # Build enhanced context
        enhanced_parts = [schema_context]
        
        if kb_results:
            enhanced_parts.append("\n=== BUSINESS CONTEXT & DOMAIN KNOWLEDGE ===")
            
            for i, result in enumerate(kb_results[:5], 1):  # Limit to top 5 results
                confidence_pct = int(result['confidence'] * 100)
                enhanced_parts.append(f"\nKnowledge Entry {i} (Confidence: {confidence_pct}%):")
                enhanced_parts.append(result['content'])
                
                # Add metadata if available
                metadata = result.get('metadata', {})
                if metadata:
                    enhanced_parts.append(f"Source: {metadata}")
        
        return "\n".join(enhanced_parts)
    
    def get_query_suggestions(self, natural_language_query: str) -> List[str]:
        """
        Get query suggestions based on knowledge base content.
        
        Args:
            natural_language_query: User's natural language query
            
        Returns:
            List of suggested queries
        """
        kb_results = self.query_knowledge_base(f"similar queries to: {natural_language_query}")
        
        suggestions = []
        for result in kb_results[:3]:  # Top 3 suggestions
            content = result['content']
            # Extract query suggestions from content
            if 'example:' in content.lower() or 'query:' in content.lower():
                suggestions.append(content)
        
        return suggestions
    
    def validate_business_rules(self, sql_query: str, natural_language_query: str) -> Dict[str, Any]:
        """
        Validate SQL query against business rules from knowledge base.
        
        Args:
            sql_query: Generated SQL query
            natural_language_query: Original natural language query
            
        Returns:
            Validation results with business rule compliance
        """
        # Query knowledge base for business rules
        rules_query = f"business rules validation for: {natural_language_query}"
        kb_results = self.query_knowledge_base(rules_query)
        
        validation_result = {
            'compliant': True,
            'warnings': [],
            'suggestions': [],
            'applicable_rules': []
        }
        
        for result in kb_results:
            content = result['content'].lower()
            
            # Check for common business rule patterns
            if 'must include' in content or 'required filter' in content:
                validation_result['applicable_rules'].append(result['content'])
                
                # Simple validation logic (can be enhanced)
                if 'date range' in content and 'where' not in sql_query.lower():
                    validation_result['warnings'].append("Consider adding date range filter")
                    validation_result['compliant'] = False
                
                if 'active records only' in content and 'active' not in sql_query.lower():
                    validation_result['warnings'].append("Consider filtering for active records only")
        
        return validation_result


class KnowledgeBaseManager:
    """
    Manager for creating and maintaining the Bedrock Knowledge Base.
    """
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=self.region)
        self.s3_client = boto3.client('s3', region_name=self.region)
        
    def create_sample_knowledge_base_content(self) -> Dict[str, str]:
        """
        Create sample knowledge base content for the text-to-sql agent.
        
        Returns:
            Dictionary of knowledge base documents
        """
        
        documents = {
            "business_glossary.md": """# Business Glossary for E-commerce Database

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
""",

            "common_queries.md": """# Common Query Patterns

## Customer Analysis Queries

### Customer Demographics
Example: "Show me customers from California"
```sql
SELECT customer_id, name, email, city, state 
FROM customers 
WHERE state = 'CA' AND status = 'active'
```

### Customer Purchase Behavior
Example: "Find customers who spent more than $1000"
```sql
SELECT c.customer_id, c.name, SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status != 'cancelled'
GROUP BY c.customer_id, c.name
HAVING SUM(o.total_amount) > 1000
```

## Sales Analysis Queries

### Revenue by Category
Example: "Show revenue by product category"
```sql
SELECT category, SUM(total_amount) as revenue
FROM orders
WHERE status = 'delivered'
  AND order_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY category
ORDER BY revenue DESC
```

### Top Products
Example: "What are the best selling products?"
```sql
SELECT p.product_name, COUNT(o.order_id) as order_count, SUM(o.total_amount) as revenue
FROM products p
JOIN orders o ON p.product_id = o.product_id
WHERE o.status = 'delivered'
GROUP BY p.product_id, p.product_name
ORDER BY order_count DESC
LIMIT 10
```

## Time-based Analysis

### Monthly Trends
Example: "Show monthly sales trends"
```sql
SELECT 
  DATE_TRUNC('month', order_date) as month,
  COUNT(*) as order_count,
  SUM(total_amount) as revenue
FROM orders
WHERE status != 'cancelled'
  AND order_date >= CURRENT_DATE - INTERVAL '12' MONTH
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month
```
""",

            "data_quality_rules.md": """# Data Quality and Validation Rules

## Required Filters
- Customer queries should include status = 'active' unless historical analysis is requested
- Financial calculations must exclude cancelled orders
- Date-based queries should have reasonable date ranges (not more than 2 years unless specified)

## Data Validation
- Customer emails should be validated format
- Phone numbers should be in standard format
- Monetary amounts should be positive
- Dates should be within reasonable ranges

## Performance Guidelines
- Always use appropriate indexes
- Limit result sets to reasonable sizes (default LIMIT 1000)
- Use date partitioning when available
- Avoid SELECT * in production queries

## Security Rules
- Never expose full customer personal information
- Mask sensitive data like phone numbers and emails in general reports
- Require specific authorization for customer PII queries
- Log all data access for audit purposes

## Business Logic
- Revenue = total_amount for delivered orders only
- Active customers = customers with orders in last 12 months
- Premium customers = customers with >$1000 annual spend
- Seasonal analysis should account for holiday periods
""",

            "schema_relationships.md": """# Database Schema Relationships and Best Practices

## Table Relationships

### Customers ↔ Orders
- One customer can have many orders
- Join on: customers.customer_id = orders.customer_id
- Always check order status when calculating customer metrics

### Orders ↔ Products
- One order can contain multiple products (if order_items table exists)
- Direct relationship: orders.product_id = products.product_id
- For revenue analysis, use orders.total_amount

### Common Join Patterns

#### Customer Order Analysis
```sql
SELECT c.name, COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.customer_id, c.name
```

#### Product Performance
```sql
SELECT p.product_name, p.category, COUNT(o.order_id) as sales_count
FROM products p
JOIN orders o ON p.product_id = o.product_id
WHERE o.status = 'delivered'
GROUP BY p.product_id, p.product_name, p.category
```

## Data Types and Formats
- Dates: Use ISO format (YYYY-MM-DD)
- Currency: Stored as DECIMAL(10,2)
- Status fields: Use standardized values
- IDs: Always use appropriate data types (INT, VARCHAR)

## Query Optimization Tips
- Use table aliases for readability
- Filter early in WHERE clauses
- Use appropriate JOINs (INNER vs LEFT)
- Consider using DISTINCT when needed
- Use LIMIT for large result sets
"""
        }
        
        return documents
    
    def upload_knowledge_base_documents(self, bucket_name: str, documents: Dict[str, str]) -> List[str]:
        """
        Upload knowledge base documents to S3.
        
        Args:
            bucket_name: S3 bucket name for knowledge base documents
            documents: Dictionary of filename -> content
            
        Returns:
            List of uploaded S3 keys
        """
        uploaded_keys = []
        
        for filename, content in documents.items():
            key = f"knowledge-base/{filename}"
            
            try:
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=content.encode('utf-8'),
                    ContentType='text/markdown'
                )
                uploaded_keys.append(key)
                logger.info(f"Uploaded {filename} to s3://{bucket_name}/{key}")
                
            except Exception as e:
                logger.error(f"Failed to upload {filename}: {str(e)}")
        
        return uploaded_keys
    
    def create_knowledge_base_config(self, 
                                   kb_name: str,
                                   s3_bucket: str,
                                   role_arn: str,
                                   embedding_model: str = "amazon.titan-embed-text-v1") -> Dict[str, Any]:
        """
        Create configuration for Bedrock Knowledge Base.
        
        Args:
            kb_name: Name for the knowledge base
            s3_bucket: S3 bucket containing documents
            role_arn: IAM role ARN for Bedrock access
            embedding_model: Embedding model to use
            
        Returns:
            Knowledge base configuration
        """
        
        config = {
            "name": kb_name,
            "description": "Knowledge base for Text-to-SQL Agent with business context and query patterns",
            "roleArn": role_arn,
            "knowledgeBaseConfiguration": {
                "type": "VECTOR",
                "vectorKnowledgeBaseConfiguration": {
                    "embeddingModelArn": f"arn:aws:bedrock:{self.region}::foundation-model/{embedding_model}"
                }
            },
            "storageConfiguration": {
                "type": "OPENSEARCH_SERVERLESS",
                "opensearchServerlessConfiguration": {
                    "collectionArn": f"arn:aws:aoss:{self.region}:{{account-id}}:collection/{{collection-id}}",
                    "vectorIndexName": "text-to-sql-index",
                    "fieldMapping": {
                        "vectorField": "vector",
                        "textField": "text",
                        "metadataField": "metadata"
                    }
                }
            }
        }
        
        return config