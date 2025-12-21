#!/usr/bin/env python3
"""
Create a new IAM role specifically for Knowledge Base with minimal permissions
"""

import boto3
import json

def create_kb_role():
    """Create a new IAM role for Knowledge Base"""
    
    iam_client = boto3.client('iam')
    sts_client = boto3.client('sts')
    
    account_id = sts_client.get_caller_identity()['Account']
    role_name = "BedrockKnowledgeBaseRole-Clean"
    
    # Trust policy
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::text-to-sql-kb-demo-2024",
                    "arn:aws:s3:::text-to-sql-kb-demo-2024/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "aoss:APIAccessAll"
                ],
                "Resource": [
                    f"arn:aws:aoss:us-east-1:{account_id}:collection/e9ex0v2xiya5ccb91445"
                ]
            }
        ]
    }
    
    try:
        # Create role
        print(f"Creating IAM role: {role_name}")
        
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Clean IAM role for Bedrock Knowledge Base with minimal permissions'
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ Role created: {role_arn}")
        
        # Attach inline policy
        print("Attaching permissions policy...")
        
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockKnowledgeBasePolicy',
            PolicyDocument=json.dumps(permissions_policy)
        )
        
        print("✅ Permissions policy attached")
        
        print(f"\n🎉 New role ready for Knowledge Base!")
        print(f"Role ARN: {role_arn}")
        print(f"\nUse this role when creating Knowledge Base in the UI:")
        print(f"Role name: {role_name}")
        
        return role_arn
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"✅ Role {role_name} already exists")
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"Role ARN: {role_arn}")
        return role_arn
        
    except Exception as e:
        print(f"❌ Failed to create role: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Creating clean IAM role for Knowledge Base...")
    print("="*60)
    
    role_arn = create_kb_role()
    
    if role_arn:
        print(f"\n✅ Success! Use this role in the Bedrock UI:")
        print(f"BedrockKnowledgeBaseRole-Clean")
    else:
        print("\n❌ Failed to create role")