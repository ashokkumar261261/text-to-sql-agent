# Manual Steps to Create Clean Knowledge Base

## Prerequisites
✅ S3 bucket with clean document: `s3://text-to-sql-kb-demo-2024/simple_patterns.md`
✅ OpenSearch Serverless collection: `text-to-sql-collection` (e9ex0v2xiya5ccb91445)
✅ IAM Role: `BedrockKnowledgeBaseRole`

## Steps to Create Knowledge Base via AWS Console

### 1. Navigate to Amazon Bedrock Console
- Go to: https://console.aws.amazon.com/bedrock/
- Region: us-east-1
- Click on "Knowledge bases" in the left menu

### 2. Create Knowledge Base
- Click "Create knowledge base"
- Name: `text-to-sql-kb-s3-clean`
- Description: `Clean Knowledge Base with simple SQL patterns only`
- IAM Role: Select existing role `BedrockKnowledgeBaseRole`
- Click "Next"

### 3. Configure Data Source
- Data source name: `s3-clean-source`
- S3 URI: `s3://text-to-sql-kb-demo-2024/`
- Click "Next"

### 4. Select Embeddings Model
- Embeddings model: `Titan Embeddings G1 - Text`
- Click "Next"

### 5. Configure Vector Store
- Vector database: `Amazon OpenSearch Serverless`
- Select existing collection: `text-to-sql-collection`
- Create new vector index with name: `kb-clean-index-v3`
- Click "Next"

### 6. Review and Create
- Review all settings
- Click "Create knowledge base"

### 7. Sync Data Source
- After creation, click "Sync" to ingest the documents
- Wait for sync to complete (should take ~1 minute)

### 8. Get Knowledge Base ID
- Copy the Knowledge Base ID (format: XXXXXXXXXX)
- Update Lambda environment variable:
  ```bash
  aws lambda update-function-configuration \
    --function-name text-to-sql-agent-demo \
    --environment "Variables={BEDROCK_KNOWLEDGE_BASE_ID=<YOUR_KB_ID>,GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}"
  ```

## Alternative: Use AWS CLI (if console doesn't work)

The issue is that OpenSearch index must be created first. Here's a workaround:

1. Let Bedrock create the index automatically by using a new index name
2. Or manually create the index using the OpenSearch API

## Test Query After Setup
Once the Knowledge Base is created and Lambda is updated, test with:
"Show me top 5 customers by revenue"

Expected SQL:
```sql
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```
