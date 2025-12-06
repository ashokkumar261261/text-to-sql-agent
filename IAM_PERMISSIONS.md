# Required IAM Permissions

This document outlines the IAM permissions required for the Text-to-SQL Agent.

## For Local Development

Your AWS user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "athena:StartQueryExecution",
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:StopQueryExecution"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:GetTables",
        "glue:GetPartitions"
      ],
      "Resource": [
        "arn:aws:glue:REGION:ACCOUNT_ID:catalog",
        "arn:aws:glue:REGION:ACCOUNT_ID:database/YOUR_DATABASE",
        "arn:aws:glue:REGION:ACCOUNT_ID:table/YOUR_DATABASE/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-data-bucket",
        "arn:aws:s3:::your-data-bucket/*",
        "arn:aws:s3:::your-athena-results-bucket",
        "arn:aws:s3:::your-athena-results-bucket/*"
      ]
    }
  ]
}
```

## For Lambda Deployment

The CloudFormation template automatically creates the necessary IAM role with these permissions.

## Bedrock Model Access

Ensure you have enabled access to the Claude 3 Sonnet model in your AWS account:

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access to "Anthropic Claude 3 Sonnet"
4. Wait for approval (usually instant)

## S3 Bucket Policies

Your S3 data bucket should allow Athena to read:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "athena.amazonaws.com"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-data-bucket",
        "arn:aws:s3:::your-data-bucket/*"
      ]
    }
  ]
}
```
