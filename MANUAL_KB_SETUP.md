# 🎯 Manual Knowledge Base Setup Guide

## ✅ What's Already Done

Your AWS infrastructure is **95% complete**! Here's what we've successfully set up:

- ✅ **S3 Bucket**: `text-to-sql-kb-demo-2024` with 4 knowledge documents
- ✅ **IAM Role**: `BedrockKnowledgeBaseRole` with proper permissions
- ✅ **OpenSearch Collection**: `text-to-sql-collection` (ACTIVE)
- ✅ **Security Policies**: Encryption, network, and data access policies

## 🎯 Final Step: Create Knowledge Base in AWS Console

### Step 1: Open AWS Console

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **Amazon Bedrock** service
3. In the left sidebar, click **Knowledge bases**

### Step 2: Create Knowledge Base

1. Click **"Create knowledge base"**
2. Fill in the details:

**Basic Information:**
- **Name**: `text-to-sql-knowledge-base`
- **Description**: `Knowledge base for Text-to-SQL Agent with business context and query patterns`
- **IAM Role**: Select **"Use an existing service role"**
- **Service Role**: `BedrockKnowledgeBaseRole`

### Step 3: Configure Data Source

**Data Source Details:**
- **Data source name**: `text-to-sql-s3-source`
- **Description**: `S3 data source for knowledge base documents`
- **S3 URI**: `s3://text-to-sql-kb-demo-2024/knowledge-base/`

**Chunking Strategy:**
- **Chunking strategy**: Default chunking
- **Max tokens**: 300
- **Overlap percentage**: 20%

### Step 4: Configure Vector Store

**Vector Database:**
- **Vector database**: Amazon OpenSearch Serverless
- **Collection**: Select `text-to-sql-collection`
- **Vector index name**: `bedrock-knowledge-base-index` (it will be created automatically)

**Vector Field Configurations:**
- **Vector field**: `bedrock-knowledge-base-default-vector`
- **Text field**: `AMAZON_BEDROCK_TEXT_CHUNK`
- **Metadata field**: `AMAZON_BEDROCK_METADATA`

### Step 5: Select Embeddings Model

- **Embeddings model**: `Titan Embeddings G1 - Text`
- **Dimensions**: 1536

### Step 6: Review and Create

1. Review all settings
2. Click **"Create knowledge base"**
3. Wait for creation to complete (2-3 minutes)

### Step 7: Sync Data Source

1. After creation, go to your knowledge base
2. Click on the **Data sources** tab
3. Select your data source
4. Click **"Sync"** to ingest the documents
5. Wait for sync to complete (3-5 minutes)

## 🔧 Update Your Configuration

After the knowledge base is created:

1. **Copy the Knowledge Base ID** from the AWS Console
2. **Update your `.env` file**:

```bash
# Add these lines to your .env file
BEDROCK_KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
KB_MAX_RESULTS=10
KB_CONFIDENCE_THRESHOLD=0.7
```

## 🧪 Test Your Setup

Run these commands to test everything:

```bash
# Test the knowledge base integration
python test_knowledge_base.py

# Launch the enhanced web UI
streamlit run web_ui_enhanced.py

# Try the example script
python example_knowledge_base.py
```

## 🎉 Expected Results

Once complete, you should see:

- ✅ **Knowledge Base Status**: Active
- ✅ **Data Source Status**: Available  
- ✅ **Documents Ingested**: 4 documents
- ✅ **Vector Index**: Created and populated

## 🔍 Verification Queries

Test these queries in the web UI:

1. **"Show me business rules for customer data"**
2. **"What are common SQL patterns for revenue analysis?"**
3. **"How should I handle cancelled orders?"**

## 📊 Infrastructure Summary

Here's what you now have:

```
🏗️ AWS Infrastructure:
├── S3 Bucket: text-to-sql-kb-demo-2024
│   └── knowledge-base/
│       ├── business_glossary.md
│       ├── common_queries.md  
│       ├── data_quality_rules.md
│       └── schema_relationships.md
├── IAM Role: BedrockKnowledgeBaseRole
├── OpenSearch Collection: text-to-sql-collection
└── Knowledge Base: text-to-sql-knowledge-base (manual creation)

💻 Local Components:
├── Enhanced Agent (src/enhanced_agent.py)
├── Knowledge Base Integration (src/knowledge_base.py)
├── Enhanced Web UI (web_ui_enhanced.py)
├── Test Suite (test_knowledge_base.py)
└── Documentation & Examples
```

## 🚀 Next Steps After Setup

1. **Customize Knowledge Base**: Add your own business rules and patterns
2. **Train Your Team**: Show them the enhanced query capabilities
3. **Monitor Usage**: Track query patterns and effectiveness
4. **Expand Content**: Add more domain-specific knowledge over time

## 🆘 Troubleshooting

**If Knowledge Base creation fails:**
- Ensure the IAM role has all required permissions
- Check that the OpenSearch collection is ACTIVE
- Verify the S3 bucket contains the documents

**If sync fails:**
- Check S3 bucket permissions
- Ensure documents are in the correct format (Markdown)
- Verify the S3 URI path is correct

**If queries don't work:**
- Confirm the Knowledge Base ID in your .env file
- Test with simple queries first
- Check the confidence threshold setting

## 📞 Support

- **AWS Documentation**: [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- **Test Script**: Run `python test_knowledge_base.py` for diagnostics
- **Logs**: Check CloudWatch logs for detailed error messages

---

**You're almost there! Just one manual step in the AWS Console and your intelligent Knowledge Base will be fully operational! 🎉**