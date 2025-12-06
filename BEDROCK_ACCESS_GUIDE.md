# AWS Bedrock Model Access Guide

## The Error You're Seeing

```
ResourceNotFoundException: Model use case details have not been submitted for this account.
Fill out the Anthropic use case details form before using the model.
```

This means you need to request access to Anthropic Claude models in AWS Bedrock.

## Quick Solution: Enable Model Access

### Option 1: Use AWS Console (Recommended)

1. **Go to AWS Bedrock Console**
   - URL: https://console.aws.amazon.com/bedrock/
   - Make sure you're in the correct region (top-right corner)

2. **Navigate to Model Access**
   - Click "Model access" in the left sidebar
   - Click "Modify model access" button

3. **Request Access to Claude**
   - Find "Anthropic" section
   - Check the box for "Claude 3 Sonnet"
   - Check the box for "Claude 3 Haiku" (optional, but recommended)

4. **Fill Out Use Case Form**
   - Anthropic requires a brief use case description
   - Example answers:
     ```
     Use Case: Text-to-SQL query generation
     Industry: Technology / Data Analytics
     Description: Converting natural language questions into SQL queries 
                  for data lake analysis using AWS Athena
     ```

5. **Submit and Wait**
   - Click "Submit"
   - Approval usually takes 5-15 minutes
   - You'll see status change from "Pending" to "Access granted"

6. **Test Access**
   ```powershell
   .\run.bat enable_bedrock_access.py
   ```

### Option 2: Use Amazon Titan (Instant Access)

Amazon Titan models are usually available immediately without a form:

1. **Enable Titan in Console**
   - Go to Bedrock → Model access
   - Check "Amazon Titan Text Express"
   - Submit (usually instant approval)

2. **Update your .env file**
   ```env
   BEDROCK_MODEL_ID=amazon.titan-text-express-v1
   ```

3. **Update agent.py to support Titan**
   - Titan uses a different API format than Claude
   - See the code modification below

## Code Modification for Titan Support

If you want to use Amazon Titan, you need to update `src/agent.py`:

<function_calls>
<invoke name="readFile">
<parameter name="path">text-to-sql-agent/src/agent.py