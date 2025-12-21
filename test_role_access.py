#!/usr/bin/env python3
"""
Test if BedrockKnowledgeBaseRole can access the S3 bucket
"""

import boto3
import json

def test_role_access():
    """Test if the role can access S3 bucket"""
    
    # Assume the role
    sts_client = boto3.client('sts')
    
    try:
        # Get current account ID
        account_id = sts_client.get_caller_identity()['Account']
        role_arn = f"arn:aws:iam::{account_id}:role/BedrockKnowledgeBaseRole"
        
        print(f"Testing role access: {role_arn}")
        
        # Assume the role
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='test-kb-access'
        )
        
        # Create S3 client with assumed role credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
            aws_session_token=assumed_role['Credentials']['SessionToken']
        )
        
        # Test bucket access
        bucket_name = 'text-to-sql-kb-demo-2024'
        
        print(f"Testing bucket access: {bucket_name}")
        
        # List bucket contents
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            print(f"✅ Successfully accessed bucket!")
            print(f"Found {len(response['Contents'])} objects:")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("✅ Bucket accessible but empty")
        
        # Test reading the specific file
        try:
            obj_response = s3_client.get_object(Bucket=bucket_name, Key='simple_patterns.md')
            content = obj_response['Body'].read().decode('utf-8')
            print(f"✅ Successfully read simple_patterns.md ({len(content)} characters)")
            print(f"Content preview: {content[:200]}...")
        except Exception as e:
            print(f"❌ Failed to read simple_patterns.md: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Role access test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing BedrockKnowledgeBaseRole S3 access...")
    print("="*60)
    
    success = test_role_access()
    
    if success:
        print("\n✅ Role access test passed!")
        print("The role should now work in the Bedrock Knowledge Base UI.")
    else:
        print("\n❌ Role access test failed!")
        print("Check IAM permissions and try again.")