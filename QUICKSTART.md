# Quick Start Guide

## ✅ Installation Complete!

All dependencies have been installed successfully.

## 📝 Next Steps

### 1. Configure Environment Variables

Edit the `.env` file with your AWS settings:

```powershell
notepad .env
```

Update these values:
- `GLUE_DATABASE` - Your Glue Catalog database name
- `ATHENA_OUTPUT_LOCATION` - S3 path for Athena results (e.g., `s3://my-bucket/athena-results/`)
- `AWS_REGION` - Your AWS region (e.g., `us-east-1`)

### 2. Configure AWS Credentials

If you haven't already:

```powershell
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region
- Output format (json)

### 3. Enable Bedrock Model Access

1. Go to AWS Console → Bedrock
2. Navigate to "Model access"
3. Request access to "Anthropic Claude 3 Sonnet"
4. Wait for approval (usually instant)

### 4. Set Up Glue Catalog (if needed)

If you don't have a Glue database yet, you can create a sample one:

```powershell
# Edit setup_glue_sample.py to update S3 locations
notepad setup_glue_sample.py

# Run the setup script
py setup_glue_sample.py
```

### 5. Test the Agent

Run the example script:

```powershell
py example.py
```

## 🎯 Usage Examples

### Generate SQL (without execution)

```python
from src.agent import TextToSQLAgent

agent = TextToSQLAgent()
result = agent.query("Show me all sales from last month", execute=False)
print(result['sql_query'])
```

### Execute Query on Athena

```python
result = agent.query("Count total orders by region", execute=True)
print(f"Results: {result['results']}")
```

### List Available Tables

```python
from src.schema import SchemaManager

schema_manager = SchemaManager()
tables = schema_manager.list_tables()
print(f"Available tables: {tables}")
```

## 📚 Documentation

- `README.md` - Full documentation
- `IAM_PERMISSIONS.md` - Required AWS permissions
- `WINDOWS_SETUP.md` - Windows-specific commands

## 🚀 Deploy to AWS Lambda

```powershell
# Install SAM CLI first
# Then:
sam build
sam deploy --guided
```

## ⚠️ Troubleshooting

### "Python not found"
Use `py` instead of `python` on Windows

### AWS Credentials Error
Run `aws configure` to set up credentials

### Glue Database Not Found
Make sure `GLUE_DATABASE` in `.env` matches your actual Glue database name

### Bedrock Access Denied
Enable model access in AWS Bedrock console

## 💡 Tips

- Start with `execute=False` to test SQL generation
- Use partition columns in queries for better performance
- Check Athena query history in AWS Console for debugging
- Monitor costs - Athena charges per TB scanned

## 🆘 Need Help?

Check the documentation files or AWS documentation:
- [AWS Athena](https://docs.aws.amazon.com/athena/)
- [AWS Glue Catalog](https://docs.aws.amazon.com/glue/)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)
