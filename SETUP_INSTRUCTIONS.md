# Setup Instructions

## Current Status

✅ Python installed (3.9.5)
✅ Dependencies installed
❌ AWS credentials not configured
❌ .env file needs real values

## Step 1: Configure AWS Credentials

Run this command:
```powershell
C:\Users\HP\AppData\Local\Programs\Python\Python39\python.exe configure_aws.py
```

Or use the batch file:
```powershell
.\run.bat configure_aws.py
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- AWS Region (e.g., us-east-1)

### Where to get AWS credentials:

1. Go to AWS Console
2. Click your username (top right) → Security credentials
3. Under "Access keys" → Create access key
4. Copy the Access Key ID and Secret Access Key

## Step 2: Update .env File

Edit `.env` file and replace placeholder values:

```env
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
GLUE_DATABASE=your_actual_database_name
ATHENA_OUTPUT_LOCATION=s3://your-actual-bucket/athena-results/
ATHENA_WORKGROUP=primary
```

### What you need:

**GLUE_DATABASE**: 
- Your AWS Glue Catalog database name
- If you don't have one, create it in AWS Glue Console
- Or run: `.\run.bat setup_glue_sample.py` (after configuring credentials)

**ATHENA_OUTPUT_LOCATION**:
- An S3 bucket where Athena can store query results
- Format: `s3://bucket-name/path/`
- Create bucket in S3 Console if needed

## Step 3: Enable Bedrock Access

1. Go to AWS Bedrock Console
2. Click "Model access" in left menu
3. Click "Manage model access"
4. Check "Anthropic Claude 3 Sonnet"
5. Click "Request model access"
6. Wait for approval (usually instant)

## Step 4: Verify Setup

Run the test script:
```powershell
.\run.bat test_setup.py
```

This will check:
- ✓ AWS credentials
- ✓ Glue database exists
- ✓ S3 bucket accessible
- ✓ Bedrock model access

## Step 5: Run the Agent

Once all checks pass:
```powershell
.\run.bat example.py
```

## Quick Commands

```powershell
# Configure AWS
.\run.bat configure_aws.py

# Test setup
.\run.bat test_setup.py

# Create sample Glue database
.\run.bat setup_glue_sample.py

# Run examples
.\run.bat example.py
```

## Troubleshooting

### "Unable to locate credentials"
- Run `.\run.bat configure_aws.py`
- Or manually create `C:\Users\HP\.aws\credentials` file

### "Glue database not found"
- Update GLUE_DATABASE in .env
- Or create database: `.\run.bat setup_glue_sample.py`

### "S3 bucket not accessible"
- Create bucket in S3 Console
- Update ATHENA_OUTPUT_LOCATION in .env
- Check IAM permissions

### "Bedrock access denied"
- Enable model access in Bedrock Console
- Wait a few minutes for permissions to propagate

## Need Help?

Check these files:
- `README.md` - Full documentation
- `IAM_PERMISSIONS.md` - Required permissions
- `QUICKSTART.md` - Quick start guide
