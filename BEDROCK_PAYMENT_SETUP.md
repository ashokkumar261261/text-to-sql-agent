# Bedrock Payment Setup Guide

## Issue: INVALID_PAYMENT_INSTRUMENT Error

The error "Model access is denied due to INVALID_PAYMENT_INSTRUMENT" occurs when AWS Bedrock requires a valid payment method to access certain foundation models.

## Solution Steps

### 1. Add Payment Method to AWS Account
1. Go to AWS Console → Billing and Cost Management
2. Navigate to "Payment methods" 
3. Add a valid credit card or payment method
4. Set it as the default payment method

### 2. Enable Model Access in Bedrock
1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access" in the left sidebar
3. Click "Enable specific models" or "Manage model access"
4. Enable the following models:
   - `anthropic.claude-3-haiku-20240307-v1:0` (recommended - lower cost)
   - `anthropic.claude-3-5-haiku-20241022-v1:0` (alternative)
   - `amazon.titan-embed-text-v2:0` (for Knowledge Base)

### 3. Wait for Model Access Activation
- Model access can take 5-10 minutes to activate
- Check the status in Bedrock Console → Model access

### 4. Alternative: Use Free Tier Models
If you want to avoid charges, use these models that don't require payment setup:
- `amazon.titan-text-express-v1` (free tier available)
- Some older Claude models may work without payment setup

## Updated Configuration

The Lambda function has been updated to use:
- **Model**: `anthropic.claude-3-haiku-20240307-v1:0` (ACTIVE status, lower cost)
- **Knowledge Base**: `MJ2GCTRK6Z` (with comprehensive SQL documentation)

## Test the System

Once payment method is added and models are enabled:

1. **Test Knowledge Base Retrieval**:
```bash
aws bedrock-agent-runtime retrieve --knowledge-base-id MJ2GCTRK6Z --retrieval-query "top customers by revenue"
```

2. **Test Lambda Function**:
```bash
aws lambda invoke --function-name text-to-sql-agent-demo --payload '{"query": "Show me top 5 customers by revenue"}' response.json
```

## Expected SQL Output

The system should generate this SQL query:
```sql
SELECT 
    c.customer_name,
    c.email,
    SUM(o.total_amount) as total_revenue,
    COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.customer_name, c.email
ORDER BY total_revenue DESC
LIMIT 5;
```

## Cost Considerations

- **Claude 3 Haiku**: ~$0.25 per 1M input tokens, $1.25 per 1M output tokens
- **Knowledge Base**: ~$0.10 per 1K queries
- **Embedding**: ~$0.0001 per 1K tokens

## Troubleshooting

If you still get payment errors:
1. Verify payment method is valid and not expired
2. Check AWS account is in good standing
3. Try using `amazon.titan-text-express-v1` as fallback
4. Contact AWS Support if issues persist

## Alternative: Local Testing

For immediate testing without AWS charges, you can:
1. Use the SQL query directly in your database
2. Test with sample data
3. Validate the Knowledge Base retrieval works (this is free)