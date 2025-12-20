#!/bin/bash
# Create IAM role for App Runner service

set -e

ROLE_NAME="AppRunnerTextToSQLRole"
POLICY_NAME="TextToSQLAgentPolicy"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🔐 Creating IAM role for Text-to-SQL Agent..."

# Create trust policy for App Runner
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "tasks.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the IAM role
echo "📝 Creating IAM role: $ROLE_NAME"
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json \
    --description "IAM role for Text-to-SQL Agent App Runner service" || echo "Role may already exist"

# Create and attach the policy
echo "📋 Creating IAM policy: $POLICY_NAME"
aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://iam-role-policy.json \
    --description "Policy for Text-to-SQL Agent to access AWS services" || echo "Policy may already exist"

# Attach policy to role
echo "🔗 Attaching policy to role"
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn "arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME"

# Clean up temporary files
rm trust-policy.json

echo "✅ IAM role created successfully!"
echo "📋 Role ARN: arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
echo ""
echo "🔧 Update your deploy-aws.sh script with this role ARN:"
echo "SERVICE_ROLE=\"arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME\""
echo ""
echo "🚀 Now you can run: ./deploy-aws.sh"