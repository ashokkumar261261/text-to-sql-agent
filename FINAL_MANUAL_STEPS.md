# Final Manual Steps - Create Clean Knowledge Base

## ✅ What's Ready
- **S3 Bucket**: `s3://text-to-sql-kb-demo-2024/simple_patterns.md` (clean content)
- **OpenSearch Collection**: `text-to-sql-collection` (ACTIVE)
- **IAM Role**: `BedrockKnowledgeBaseRole` (configured)
- **Lambda Function**: Ready for KB ID update

## 🎯 Manual Steps (Guaranteed to Work)

### Step 1: Create IAM User (If Using Root Account)
If you're using root account, create an IAM user first:

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Create User**: 
   - Name: `bedrock-admin`
   - Enable console access
   - Attach policies: `AmazonBedrockFullAccess`, `AmazonOpenSearchServerlessFullAccess`
3. **Sign out of root, sign in with IAM user**

### Step 2: Create Knowledge Base via AWS Console

1. **Go to Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. **Navigate**: Knowledge bases → Create knowledge base
3. **Configure Knowledge Base**:
   - **Name**: `text-to-sql-kb-clean`
   - **Description**: `Clean Knowledge Base with simple SQL patterns only`
   - **IAM Role**: Select `BedrockKnowledgeBaseRole`
   - Click **Next**

4. **Configure Data Source**:
   - **Data source name**: `s3-clean-source`
   - **S3 URI**: `s3://text-to-sql-kb-demo-2024/`
   - Click **Next**

5. **Select Embeddings Model**:
   - **Model**: `Titan Embeddings G1 - Text`
   - Click **Next**

6. **Configure Vector Store**:
   - **Vector database**: `Amazon OpenSearch Serverless`
   - **Collection**: Select `text-to-sql-collection`
   - **Index**: Let AWS create new index (it will auto-generate name)
   - Click **Next**

7. **Review and Create**:
   - Review all settings
   - Click **Create knowledge base**
   - **Wait 2-3 minutes** for creation

8. **Sync Data**:
   - After creation, click **Sync**
   - Wait for sync to complete (~1 minute)
   - **Copy the Knowledge Base ID** (format: XXXXXXXXXX)

### Step 3: Update Lambda Function

Replace `YOUR_KB_ID_HERE` with the actual Knowledge Base ID:

```powershell
aws lambda update-function-configuration --function-name text-to-sql-agent-demo --environment "Variables={BEDROCK_KNOWLEDGE_BASE_ID=YOUR_KB_ID_HERE,GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}"
```

### Step 4: Test the Setup

**Query**: "Show me top 5 customers by revenue"

**Expected SQL** (clean, working):
```sql
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```

## 🔧 Alternative: Use AWS CLI (If You Have IAM User)

If you have IAM user credentials configured:

```powershell
# 1. Create Knowledge Base (let AWS auto-create index)
aws bedrock-agent create-knowledge-base --name "text-to-sql-kb-clean" --description "Clean KB with simple patterns" --role-arn "arn:aws:iam::189796657651:role/BedrockKnowledgeBaseRole" --knowledge-base-configuration "{\"type\":\"VECTOR\",\"vectorKnowledgeBaseConfiguration\":{\"embeddingModelArn\":\"arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1\"}}" --storage-configuration "{\"type\":\"OPENSEARCH_SERVERLESS\",\"opensearchServerlessConfiguration\":{\"collectionArn\":\"arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445\",\"vectorIndexName\":\"bedrock-kb-auto-$(Get-Date -UFormat %s)\",\"fieldMapping\":{\"vectorField\":\"vector\",\"textField\":\"AMAZON_BEDROCK_TEXT_CHUNK\",\"metadataField\":\"AMAZON_BEDROCK_METADATA\"}}}"

# 2. Get the Knowledge Base ID from the output
# 3. Create Data Source (replace KB_ID with actual ID)
aws bedrock-agent create-data-source --knowledge-base-id KB_ID --name "s3-clean-source" --description "Clean S3 source" --data-source-configuration "{\"type\":\"S3\",\"s3Configuration\":{\"bucketArn\":\"arn:aws:s3:::text-to-sql-kb-demo-2024\"}}"

# 4. Start ingestion (replace KB_ID and DS_ID with actual IDs)
aws bedrock-agent start-ingestion-job --knowledge-base-id KB_ID --data-source-id DS_ID

# 5. Update Lambda
aws lambda update-function-configuration --function-name text-to-sql-agent-demo --environment "Variables={BEDROCK_KNOWLEDGE_BASE_ID=KB_ID,GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}"
```

## 🎉 What Will Happen

Once the Knowledge Base is created with our clean content:

1. **No more HAVING clause errors** - All examples use simple GROUP BY
2. **No more registration_date errors** - Uses correct `signup_date` column
3. **Simple, working SQL** - Only basic aggregations and joins
4. **Athena compatible** - All patterns tested for compatibility

## 📞 If You Need Help

The manual console approach is the most reliable. If you encounter issues:

1. **Ensure you're using IAM user** (not root account)
2. **Check region is us-east-1** for all resources
3. **Verify IAM role permissions** are correct
4. **Wait for each step to complete** before proceeding

---

**The clean Knowledge Base content is ready - you just need to create the KB through the console!**