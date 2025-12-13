# 📚 Knowledge Base Integration Guide

This guide explains how to set up and use Amazon Bedrock Knowledge Base with your Text-to-SQL Agent for enhanced query generation with business context and domain expertise.

## 🎯 Overview

The Knowledge Base integration adds intelligent context to your SQL generation by providing:

- **Business Glossary**: Domain-specific terminology and definitions
- **Query Patterns**: Common SQL patterns and best practices
- **Business Rules**: Data validation and compliance rules
- **Schema Relationships**: Enhanced understanding of table relationships
- **Query Suggestions**: Intelligent recommendations based on context

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Enhanced Agent  │───▶│   SQL Query     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Bedrock KB Query │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Business Context│
                       │  Query Patterns  │
                       │  Validation Rules│
                       └──────────────────┘
```

## 🚀 Quick Setup

### Prerequisites

- AWS Account with Bedrock access
- S3 bucket for knowledge base documents
- OpenSearch Serverless collection
- IAM role with appropriate permissions

### 1. Automated Setup

Use the provided setup script for quick deployment:

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup_knowledge_base.py --bucket-name your-kb-bucket-name

# Follow the instructions to complete setup in AWS Console
```

### 2. Manual Setup Steps

#### Step 1: Create S3 Bucket and Upload Documents

```bash
# Create S3 bucket
aws s3 mb s3://your-knowledge-base-bucket

# Upload sample documents (done automatically by setup script)
python -c "
from src.knowledge_base import KnowledgeBaseManager
kb = KnowledgeBaseManager()
docs = kb.create_sample_knowledge_base_content()
kb.upload_knowledge_base_documents('your-knowledge-base-bucket', docs)
"
```

#### Step 2: Create OpenSearch Serverless Collection

```bash
# Use the generated CloudFormation template
aws cloudformation create-stack \
  --stack-name text-to-sql-kb-infrastructure \
  --template-body file://knowledge_base_infrastructure.yaml \
  --capabilities CAPABILITY_IAM
```

#### Step 3: Create Bedrock Knowledge Base

1. Go to Amazon Bedrock Console
2. Navigate to "Knowledge bases"
3. Click "Create knowledge base"
4. Configure:
   - **Name**: `text-to-sql-knowledge-base`
   - **Data source**: S3
   - **S3 URI**: `s3://your-knowledge-base-bucket/knowledge-base/`
   - **Embeddings model**: `amazon.titan-embed-text-v1`
   - **Vector database**: OpenSearch Serverless
   - **Collection**: Select your created collection

#### Step 4: Update Environment Configuration

```bash
# Add to your .env file
BEDROCK_KNOWLEDGE_BASE_ID=your_knowledge_base_id
KB_MAX_RESULTS=10
KB_CONFIDENCE_THRESHOLD=0.7
```

## 📖 Knowledge Base Documents

The system includes four types of knowledge base documents:

### 1. Business Glossary (`business_glossary.md`)

Defines business terms and concepts:

```markdown
## Customer Information
- **Customer Status**: Active customers are those who have made a purchase in the last 12 months
- **Customer Tier**: Premium (>$1000 annual spend), Standard ($100-$1000), Basic (<$100)

## Business Rules
- Always filter for active customers unless specifically requested otherwise
- Revenue calculations should exclude cancelled orders
```

### 2. Common Query Patterns (`common_queries.md`)

Provides SQL examples for common business questions:

```markdown
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

### 3. Data Quality Rules (`data_quality_rules.md`)

Defines validation and business logic rules:

```markdown
## Required Filters
- Customer queries should include status = 'active' unless historical analysis is requested
- Financial calculations must exclude cancelled orders

## Security Rules
- Never expose full customer personal information
- Mask sensitive data like phone numbers and emails
```

### 4. Schema Relationships (`schema_relationships.md`)

Explains table relationships and join patterns:

```markdown
### Customers ↔ Orders
- One customer can have many orders
- Join on: customers.customer_id = orders.customer_id
- Always check order status when calculating customer metrics
```

## 🔧 Usage Examples

### Basic Enhanced Query

```python
from src.enhanced_agent import EnhancedTextToSQLAgent

# Initialize with knowledge base
agent = EnhancedTextToSQLAgent(enable_knowledge_base=True)

# Query with business context
result = agent.query(
    "Show me premium customers from California",
    use_knowledge_base=True,
    explain=True
)

print(f"SQL: {result['sql_query']}")
print(f"Business Context: {result['knowledge_base_insights']}")
```

### Query Intent Analysis

```python
# Analyze query complexity and intent
intent = agent.analyze_query_intent("Calculate monthly revenue trends")

print(f"Intent: {intent['intent_type']}")  # temporal_analysis
print(f"Complexity: {intent['complexity']}")  # high
print(f"Tables: {intent['tables_likely_needed']}")  # ['orders']
```

### Business Rule Validation

```python
# Query with business rule validation
result = agent.query(
    "Show all customer data",
    validate=True,
    use_knowledge_base=True
)

# Check business rule compliance
compliance = result['validation']['business_rule_compliance']
if not compliance['compliant']:
    print("Warnings:", compliance['warnings'])
```

### Intelligent Suggestions

```python
# Get context-aware query suggestions
suggestions = agent.get_query_suggestions("customer analysis")

for suggestion in suggestions:
    print(f"• {suggestion}")
```

## 🌐 Web UI Integration

The enhanced web UI (`web_ui_enhanced.py`) provides:

### Features

1. **Knowledge Base Status**: Real-time connection status
2. **Query Analysis**: Intent and complexity analysis
3. **Business Context**: Relevant knowledge base entries
4. **Smart Suggestions**: Context-aware query recommendations
5. **Rule Validation**: Business rule compliance checking

### Usage

```bash
# Start enhanced web UI
streamlit run web_ui_enhanced.py
```

### Interface Components

- **Query Interface**: Enhanced with intent analysis
- **Suggestions Tab**: Intelligent query recommendations
- **Knowledge Base Tab**: Management and testing interface
- **Results Display**: Includes business context and validation

## 🔍 Advanced Configuration

### Custom Knowledge Base Content

Create your own knowledge base documents:

```python
from src.knowledge_base import KnowledgeBaseManager

kb_manager = KnowledgeBaseManager()

# Create custom documents
custom_docs = {
    "custom_business_rules.md": """
    # Custom Business Rules
    
    ## Sales Analysis
    - Include only completed transactions
    - Exclude test accounts (customer_id < 1000)
    """,
    
    "domain_specific_queries.md": """
    # Domain-Specific Query Patterns
    
    ### E-commerce Metrics
    Example: "Monthly recurring revenue"
    ```sql
    SELECT DATE_TRUNC('month', order_date) as month,
           SUM(total_amount) as mrr
    FROM orders 
    WHERE subscription_type = 'recurring'
    GROUP BY month
    ```
    """
}

# Upload to S3
kb_manager.upload_knowledge_base_documents("your-bucket", custom_docs)
```

### Fine-tuning Parameters

Adjust knowledge base behavior:

```python
# In your .env file
KB_MAX_RESULTS=15              # More results for complex queries
KB_CONFIDENCE_THRESHOLD=0.8    # Higher confidence threshold
```

### Custom Validation Rules

Extend business rule validation:

```python
class CustomKnowledgeBase(BedrockKnowledgeBase):
    def validate_business_rules(self, sql_query, natural_language_query):
        result = super().validate_business_rules(sql_query, natural_language_query)
        
        # Add custom validation
        if 'customer' in sql_query.lower() and 'gdpr_consent' not in sql_query.lower():
            result['warnings'].append("Consider GDPR compliance for customer data")
        
        return result
```

## 📊 Monitoring and Analytics

### Knowledge Base Performance

Monitor knowledge base effectiveness:

```python
# Get knowledge base insights
insights = agent._get_knowledge_base_insights(query, sql)

print(f"Relevant contexts found: {len(insights['relevant_context'])}")
print(f"Average confidence: {sum(c['confidence'] for c in insights['relevant_context']) / len(insights['relevant_context'])}")
```

### Query Pattern Analysis

Track common query patterns:

```python
# Analyze conversation history
summary = agent.get_conversation_summary()
print(f"Total queries: {summary['total_queries']}")
print(f"Most common intent: {summary['most_common_intent']}")
```

## 🛠️ Troubleshooting

### Common Issues

#### Knowledge Base Not Found

```
Error: Knowledge Base ID not configured
```

**Solution**: Set `BEDROCK_KNOWLEDGE_BASE_ID` in your `.env` file

#### Low Confidence Results

```
Warning: No high-confidence results from knowledge base
```

**Solutions**:
- Lower `KB_CONFIDENCE_THRESHOLD`
- Add more relevant documents
- Improve document content quality

#### Permission Errors

```
Error: Access denied to knowledge base
```

**Solution**: Check IAM role permissions for Bedrock and OpenSearch

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show knowledge base query details
agent = EnhancedTextToSQLAgent(enable_knowledge_base=True)
```

## 🔄 Maintenance

### Updating Knowledge Base Content

1. **Update Documents**: Modify files in S3 bucket
2. **Sync Knowledge Base**: Trigger sync in Bedrock console
3. **Test Changes**: Use the web UI test interface

### Performance Optimization

- **Document Size**: Keep documents focused and concise
- **Metadata**: Add relevant metadata for better filtering
- **Embeddings**: Consider using different embedding models for domain-specific content

## 🚀 Next Steps

1. **Custom Domain Content**: Add your specific business rules and patterns
2. **Integration Testing**: Test with your actual data schema
3. **User Training**: Train users on enhanced query capabilities
4. **Monitoring Setup**: Implement usage analytics and performance monitoring

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review AWS Bedrock documentation
3. Open an issue on the GitHub repository
4. Contact your AWS support team for Bedrock-specific issues

---

**Built with ❤️ using Amazon Bedrock Knowledge Base**