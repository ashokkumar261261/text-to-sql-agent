# Complete Knowledge Base Creation Guide

## 🎯 Ready-to-Use Solution

### ✅ Everything is Prepared:
- **IAM User**: `bedrock-kb-admin` (ready to login)
- **IAM Role**: `BedrockKnowledgeBaseRole-Clean` (proper permissions)
- **S3 Bucket**: `s3://text-to-sql-kb-clean-2024/simple_patterns.md` (clean content uploaded)
- **OpenSearch Collection**: `text-to-sql-collection` (ACTIVE)

### 🔑 Login Credentials
- **Account ID**: `189796657651`
- **Username**: `bedrock-kb-admin`
- **Password**: `BedrockKB2024!` (change on first login)
- **Login URL**: https://189796657651.signin.aws.amazon.com/console

## 📋 Step-by-Step Instructions

### Step 1: Login to AWS Console
1. Go to: https://189796657651.signin.aws.amazon.com/console
2. Enter credentials:
   - Username: `bedrock-kb-admin`
   - Password: `BedrockKB2024!`
3. Change password when prompted
4. You're now logged in with proper permissions!

### Step 2: Navigate to Bedrock
1. In AWS Console, search for "Bedrock"
2. Click on "Amazon Bedrock"
3. In the left menu, click "Knowledge bases"
4. Click "Create knowledge base"

### Step 3: Configure Knowledge Base
**Page 1: Knowledge base details**
- **Name**: `text-to-sql-kb-clean`
- **Description**: `Clean Knowledge Base with simple SQL patterns only`
- **IAM role**: Select `BedrockKnowledgeBaseRole-Clean` (this is the role with proper S3 permissions)
- Click **Next**

**Page 2: Data source**
- **Data source name**: `s3-clean-source`
- **S3 URI**: `s3://text-to-sql-kb-clean-2024/`
- Leave other settings as default
- Click **Next**

**Page 3: Embeddings model**
- **Embeddings model**: Select `Titan Embeddings G1 - Text`
- Click **Next**

**Page 4: Vector database**
- **Vector database**: Select `Amazon OpenSearch Serverless`
- **Collection**: Select `text-to-sql-collection`
- **Vector index**: Let AWS create a new index (it will auto-generate the name)
- Click **Next**

**Page 5: Review**
- Review all settings
- Click **Create knowledge base**
- **Wait 2-3 minutes** for creation to complete

### Step 4: Sync Data
1. After creation, you'll see the Knowledge Base details page
2. Click the **Sync** button
3. Wait for sync to complete (~1 minute)
4. **Copy the Knowledge Base ID** (format: XXXXXXXXXX)

### Step 5: Update Lambda Function
Replace `YOUR_KB_ID_HERE` with the actual Knowledge Base ID:

```powershell
aws lambda update-function-configuration --function-name text-to-sql-agent-demo --environment "Variables={BEDROCK_KNOWLEDGE_BASE_ID=YOUR_KB_ID_HERE,GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}"
```

### Step 6: Test the Setup
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

## 🔧 Troubleshooting

### Can't see the IAM role?
- Make sure you selected `BedrockKnowledgeBaseRole-Clean` (not the old one)
- The user has permission to list and use this role

### Can't see the S3 bucket?
- The bucket `s3://text-to-sql-kb-clean-2024/` should be visible
- The role has proper S3 permissions

### Can't see the OpenSearch collection?
- Select `text-to-sql-collection`
- It should show as ACTIVE

### Knowledge Base creation fails?
- Make sure you're using the IAM user (not root)
- Check that all resources are in us-east-1 region
- Wait for each step to complete before proceeding

## 🎉 What Will Happen

Once the Knowledge Base is created:
1. **No more HAVING clause errors** - All examples use simple GROUP BY
2. **No more registration_date errors** - Uses correct `signup_date` column  
3. **Simple, working SQL** - Only basic aggregations and joins
4. **Athena compatible** - All patterns tested for compatibility

## 📊 Clean Content in Knowledge Base

The Knowledge Base contains only these simple, working patterns:

```sql
-- Top customers by revenue (SIMPLE - NO HAVING CLAUSES)
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;

-- Sales by category
SELECT category,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as total_revenue
FROM text_to_sql_demo.orders
GROUP BY category
ORDER BY total_revenue DESC;
```

**CRITICAL RULES in Knowledge Base:**
1. NEVER use column aliases in HAVING clauses
2. NEVER use CASE expressions in HAVING clauses  
3. Use signup_date for customer dates (NOT registration_date)
4. Keep queries simple with basic aggregations only
5. Always use LIMIT for large result sets

---

**Everything is ready - just follow the steps above to create the Knowledge Base!**