# Final Setup Instructions for Knowledge Base

## ⚠️ Important: Use IAM User, Not Root Account

The error "Knowledge Base creation with a root user is not supported" means you need to:

### Option 1: Create IAM User (Recommended)
1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Create new IAM user**:
   - Username: `bedrock-admin`
   - Enable console access
   - Attach policies:
     - `AmazonBedrockFullAccess`
     - `AmazonOpenSearchServerlessFullAccess`
     - `AmazonS3FullAccess`
3. **Sign out of root account**
4. **Sign in with new IAM user**
5. **Create Knowledge Base** through Bedrock Console

### Option 2: Use Existing IAM Role (Simpler)
Since you already have `BedrockKnowledgeBaseRole`, you can:

1. **Switch to IAM user** (if you have one)
2. **Or create a temporary IAM user** with admin access
3. **Then create Knowledge Base** through console

## 📋 Knowledge Base Creation Steps (With IAM User)

### 1. Navigate to Bedrock Console
- URL: https://console.aws.amazon.com/bedrock/
- Region: **us-east-1**
- Click "Knowledge bases" → "Create knowledge base"

### 2. Configure Knowledge Base
- **Name**: `text-to-sql-kb-clean`
- **Description**: `Clean Knowledge Base with simple SQL patterns`
- **IAM Role**: Select `BedrockKnowledgeBaseRole`
- Click "Next"

### 3. Add Data Source
- **Data source name**: `s3-clean-source`
- **S3 URI**: `s3://text-to-sql-kb-demo-2024/`
- Click "Next"

### 4. Select Embeddings Model
- **Model**: `Titan Embeddings G1 - Text`
- Click "Next"

### 5. Configure Vector Store
- **Vector database**: `Amazon OpenSearch Serverless`
- **Collection**: Select `text-to-sql-collection`
- **Let AWS create new index automatically**
- Click "Next"

### 6. Review and Create
- Review settings
- Click "Create knowledge base"
- **Wait for creation** (~2-3 minutes)

### 7. Sync Data
- After creation, click "Sync"
- Wait for sync to complete (~1 minute)
- **Copy the Knowledge Base ID** (format: XXXXXXXXXX)

### 8. Update Lambda Function
Run this command with your Knowledge Base ID:

```powershell
aws lambda update-function-configuration `
  --function-name text-to-sql-agent-demo `
  --environment "Variables={BEDROCK_KNOWLEDGE_BASE_ID=YOUR_KB_ID_HERE,GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}"
```

Replace `YOUR_KB_ID_HERE` with the actual Knowledge Base ID.

## 🧪 Test the Setup

Once complete, test with:
**Query**: "Show me top 5 customers by revenue"

**Expected SQL**:
```sql
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
```

## ✅ What's Already Done

- ✅ S3 bucket with clean document: `s3://text-to-sql-kb-demo-2024/simple_patterns.md`
- ✅ OpenSearch collection: `text-to-sql-collection` (ACTIVE)
- ✅ IAM Role: `BedrockKnowledgeBaseRole` (configured)
- ✅ Lambda function: Ready and waiting for KB ID
- ✅ Correct schemas: No registration_date, no HAVING clauses
- ✅ Simple patterns only: All Athena-compatible

## 🔧 Troubleshooting

### If you can't create IAM user:
Contact your AWS account administrator to:
1. Create an IAM user for you
2. Or grant you IAM user credentials
3. Or create the Knowledge Base for you

### If Knowledge Base creation fails:
- Ensure you're signed in as IAM user (not root)
- Check that all resources are in `us-east-1` region
- Verify IAM role has correct permissions

### If Lambda update fails:
```powershell
# Check current Lambda configuration
aws lambda get-function-configuration --function-name text-to-sql-agent-demo

# Verify the function exists
aws lambda list-functions --query "Functions[?FunctionName=='text-to-sql-agent-demo']"
```

## 📞 Need Help?

If you encounter issues:
1. Check AWS CloudWatch logs for errors
2. Verify all resources are in the same region (us-east-1)
3. Ensure IAM permissions are correctly configured
4. Test with a simple query first

---

**Once the Knowledge Base is created and Lambda is updated, the system will generate simple, working SQL queries without the previous errors!**
