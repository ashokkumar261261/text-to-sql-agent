# 🚀 AWS Knowledge Base Setup Guide

## Step 1: Configure AWS Credentials

You have AWS CLI installed! Now we need to configure your credentials.

### Option A: Using AWS Configure (Recommended)
```bash
# Run this command and enter your credentials when prompted
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" configure

# You'll be asked for:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1 (or your preferred region)
# Default output format: json
```

### Option B: Using Environment Variables
If you prefer to use environment variables, add these to your `.env` file:
```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
```

## Step 2: Verify AWS Access

Test your AWS connection:
```bash
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sts get-caller-identity
```

This should return your AWS account information.

## Step 3: Check Bedrock Access

Verify you have access to Amazon Bedrock:
```bash
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" bedrock list-foundation-models --region us-east-1
```

## Step 4: Run Knowledge Base Setup

Once AWS is configured, run our setup script:
```bash
# Using the full Python path we identified earlier
C:\Users\Adarsh\AppData\Local\Programs\Python\Python311\python.exe setup_knowledge_base.py --bucket-name text-to-sql-kb-demo-2024
```

## Step 5: AWS Console Setup

After the script completes, you'll need to:

1. **Create OpenSearch Serverless Collection**
   - Go to AWS Console → OpenSearch Service → Serverless collections
   - Create new collection with vector search type
   - Name: `text-to-sql-collection`

2. **Create Bedrock Knowledge Base**
   - Go to AWS Console → Amazon Bedrock → Knowledge bases
   - Click "Create knowledge base"
   - Configure:
     - Name: `text-to-sql-knowledge-base`
     - Data source: S3
     - S3 URI: `s3://text-to-sql-kb-demo-2024/knowledge-base/`
     - Embeddings model: `amazon.titan-embed-text-v1`
     - Vector database: OpenSearch Serverless
     - Collection: Select your created collection

3. **Get Knowledge Base ID**
   - After creation, copy the Knowledge Base ID
   - Update your `.env` file:
   ```
   BEDROCK_KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
   ```

## Step 6: Test Integration

```bash
# Test the knowledge base integration
C:\Users\Adarsh\AppData\Local\Programs\Python\Python311\python.exe test_knowledge_base.py

# Launch the enhanced web UI
C:\Users\Adarsh\AppData\Local\Programs\Python\Python311\python.exe -m streamlit run web_ui_enhanced.py
```

## Troubleshooting

### Common Issues:

1. **"Unable to locate credentials"**
   - Run `aws configure` to set up credentials
   - Or set environment variables in `.env`

2. **"Access denied to Bedrock"**
   - Ensure your AWS user has Bedrock permissions
   - Run the `enable_bedrock_access.py` script if needed

3. **"Knowledge base not found"**
   - Verify the Knowledge Base ID in your `.env` file
   - Ensure the knowledge base is in the same region

### Required AWS Permissions:

Your AWS user needs these permissions:
- `AmazonBedrockFullAccess`
- `AmazonS3FullAccess`
- `AmazonOpenSearchServerlessFullAccess`
- `IAMFullAccess` (for role creation)

## Next Steps

Once everything is set up:

1. **Test with sample queries** in the web UI
2. **Add your own business knowledge** to the knowledge base documents
3. **Customize business rules** for your specific domain
4. **Train your team** on the enhanced capabilities

## Support

If you encounter issues:
1. Check the AWS Console for error messages
2. Review the CloudWatch logs
3. Run the test script for detailed diagnostics
4. Refer to the `KNOWLEDGE_BASE_GUIDE.md` for detailed documentation