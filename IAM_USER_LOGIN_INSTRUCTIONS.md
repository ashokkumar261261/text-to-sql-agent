# IAM User Login Instructions for Knowledge Base Creation

## ✅ IAM User Created Successfully!

### 🔑 Login Credentials
- **Account ID**: `189796657651`
- **Username**: `bedrock-kb-admin`
- **Password**: `BedrockKB2024!`
- **Password Reset Required**: Yes (you'll need to change it on first login)

### 🌐 AWS Console Login URL
```
https://189796657651.signin.aws.amazon.com/console
```

### 📋 Login Steps

1. **Go to AWS Console**: https://189796657651.signin.aws.amazon.com/console
2. **Enter Credentials**:
   - Account ID: `189796657651` (should be pre-filled)
   - Username: `bedrock-kb-admin`
   - Password: `BedrockKB2024!`
3. **Change Password**: You'll be prompted to set a new password
4. **Navigate to Bedrock**: Go to Amazon Bedrock service
5. **Create Knowledge Base**: Follow the manual steps

### 🔐 User Permissions
The `bedrock-kb-admin` user has permissions to:
- ✅ Create and manage Bedrock Knowledge Bases
- ✅ Access OpenSearch Serverless collections
- ✅ List and access S3 buckets
- ✅ Use the `BedrockKnowledgeBaseRole-Clean` role
- ✅ View IAM roles for Knowledge Base creation

### 🎯 What to Do Next

1. **Login with the IAM user** (not root account)
2. **Go to Bedrock Console** → Knowledge Bases
3. **Create Knowledge Base** using:
   - **S3 Bucket**: `s3://text-to-sql-kb-demo-2024/`
   - **IAM Role**: `BedrockKnowledgeBaseRole-Clean`
   - **Collection**: `text-to-sql-collection`

### 🔧 If You Have Issues

**Can't see S3 buckets?**
- Make sure you're using the `BedrockKnowledgeBaseRole-Clean` role (not the old one)

**Can't see IAM roles?**
- The user has permission to list and use the Knowledge Base roles

**Login issues?**
- Use the account-specific URL: https://189796657651.signin.aws.amazon.com/console
- Make sure you're using `bedrock-kb-admin` (not root)

### 🎉 After Knowledge Base Creation

Once you create the Knowledge Base:
1. **Copy the Knowledge Base ID**
2. **Update Lambda function** with the new KB ID
3. **Test the query**: "Show me top 5 customers by revenue"

---

**This IAM user is specifically created for Knowledge Base management and has all the necessary permissions!**