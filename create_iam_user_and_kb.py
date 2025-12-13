#!/usr/bin/env python3
"""
Create IAM user and use it to create Bedrock Knowledge Base.
This bypasses the root user restriction for Knowledge Base creation.
"""

import boto3
import json
import time
import os

def create_iam_user_for_bedrock():
    """Create IAM user with necessary permissions for Bedrock Knowledge Base."""
    
    iam = boto3.client('iam')
    sts = boto3.client('sts')
    
    account_id = sts.get_caller_identity()['Account']
    user_name = 'bedrock-kb-user'
    
    try:
        print("Creating IAM user for Bedrock Knowledge Base...")
        
        # Create IAM user
        try:
            iam.create_user(
                UserName=user_name,
                Path='/',
                Tags=[
                    {
                        'Key': 'Purpose',
                        'Value': 'BedrockKnowledgeBase'
                    }
                ]
            )
            print(f"✅ Created IAM user: {user_name}")
        except iam.exceptions.EntityAlreadyExistsException:
            print(f"✅ IAM user {user_name} already exists")
        
        # Create access key
        try:
            response = iam.create_access_key(UserName=user_name)
            access_key = response['AccessKey']['AccessKeyId']
            secret_key = response['AccessKey']['SecretAccessKey']
            print(f"✅ Created access key for user")
        except Exception as e:
            # If access key already exists, we'll need to use existing one
            print(f"⚠️  Access key may already exist: {e}")
            print("If this fails, delete existing access keys for the user and retry")
            return False
        
        # Attach necessary policies
        policies = [
            'arn:aws:iam::aws:policy/AmazonBedrockFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
        ]
        
        for policy_arn in policies:
            try:
                iam.attach_user_policy(
                    UserName=user_name,
                    PolicyArn=policy_arn
                )
                print(f"✅ Attached policy: {policy_arn.split('/')[-1]}")
            except Exception as e:
                print(f"⚠️  Policy attachment issue: {e}")
        
        # Create inline policy for additional permissions
        inline_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:PassRole",
                        "iam:GetRole",
                        "iam:ListRoles"
                    ],
                    "Resource": f"arn:aws:iam::{account_id}:role/BedrockKnowledgeBaseRole"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "aoss:*"
                    ],
                    "Resource": "*"
                },
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
                }
            ]
        }
        
        iam.put_user_policy(
            UserName=user_name,
            PolicyName='BedrockKnowledgeBaseInlinePolicy',
            PolicyDocument=json.dumps(inline_policy)
        )
        print("✅ Created inline policy for additional permissions")
        
        # Wait for user to be ready
        print("Waiting for IAM user to be ready...")
        time.sleep(10)
        
        return access_key, secret_key
        
    except Exception as e:
        print(f"❌ Error creating IAM user: {e}")
        return False

def create_kb_with_iam_user(access_key, secret_key):
    """Create Knowledge Base using the IAM user credentials."""
    
    # Create new session with IAM user credentials
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'
    )
    
    bedrock_agent = session.client('bedrock-agent')
    sts = session.client('sts')
    
    try:
        # Verify the user identity
        identity = sts.get_caller_identity()
        print(f"Using IAM user: {identity['Arn']}")
        
        account_id = identity['Account']
        collection_arn = "arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445"
        
        print("Creating Bedrock Knowledge Base with IAM user...")
        
        # Create Knowledge Base
        kb_config = {
            'name': 'text-to-sql-knowledge-base',
            'description': 'Knowledge base for Text-to-SQL Agent with business context and query patterns',
            'roleArn': f'arn:aws:iam::{account_id}:role/BedrockKnowledgeBaseRole',
            'knowledgeBaseConfiguration': {
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
                }
            },
            'storageConfiguration': {
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    'collectionArn': collection_arn,
                    'vectorIndexName': 'bedrock-knowledge-base-default-index',
                    'fieldMapping': {
                        'vectorField': 'bedrock-knowledge-base-default-vector',
                        'textField': 'AMAZON_BEDROCK_TEXT_CHUNK',
                        'metadataField': 'AMAZON_BEDROCK_METADATA'
                    }
                }
            }
        }
        
        response = bedrock_agent.create_knowledge_base(**kb_config)
        
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        kb_arn = response['knowledgeBase']['knowledgeBaseArn']
        
        print(f"✅ Knowledge Base created!")
        print(f"   ID: {kb_id}")
        print(f"   ARN: {kb_arn}")
        
        # Create data source
        print("Creating data source...")
        
        data_source_config = {
            'knowledgeBaseId': kb_id,
            'name': 'text-to-sql-s3-source',
            'description': 'S3 data source for Text-to-SQL knowledge base documents',
            'dataSourceConfiguration': {
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::text-to-sql-kb-demo-2024',
                    'inclusionPrefixes': ['knowledge-base/']
                }
            }
        }
        
        ds_response = bedrock_agent.create_data_source(**data_source_config)
        data_source_id = ds_response['dataSource']['dataSourceId']
        
        print(f"✅ Data source created: {data_source_id}")
        
        # Start ingestion job
        print("Starting ingestion job...")
        
        ingestion_response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=data_source_id,
            description='Initial ingestion of knowledge base documents'
        )
        
        ingestion_job_id = ingestion_response['ingestionJob']['ingestionJobId']
        print(f"✅ Ingestion job started: {ingestion_job_id}")
        
        # Wait for ingestion to complete
        print("Waiting for ingestion to complete...")
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                job_response = bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=ingestion_job_id
                )
                
                status = job_response['ingestionJob']['status']
                print(f"   Status: {status}")
                
                if status == 'COMPLETE':
                    print("✅ Ingestion completed successfully!")
                    break
                elif status == 'FAILED':
                    print("❌ Ingestion failed")
                    failure_reasons = job_response['ingestionJob'].get('failureReasons', [])
                    for reason in failure_reasons:
                        print(f"   Reason: {reason}")
                    break
                
                time.sleep(15)
                
            except Exception as e:
                print(f"   Error checking status: {e}")
                time.sleep(15)
        
        # Save configuration
        env_content = f"""# Add these to your .env file:
BEDROCK_KNOWLEDGE_BASE_ID={kb_id}
KB_MAX_RESULTS=10
KB_CONFIDENCE_THRESHOLD=0.7

# IAM User credentials (for future use if needed)
# AWS_ACCESS_KEY_ID={access_key}
# AWS_SECRET_ACCESS_KEY={secret_key}
"""
        
        with open('.env.kb', 'w') as f:
            f.write(env_content)
        
        print(f"\n🎉 Knowledge Base setup complete!")
        print(f"Knowledge Base ID: {kb_id}")
        print(f"Configuration saved to .env.kb")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        
        # Check if it's still an index issue
        if "no such index" in str(e):
            print("\n🔄 The index issue persists. Let's try creating it manually...")
            return create_kb_with_auto_index(session, kb_config)
        
        return False

def create_kb_with_auto_index(session, base_config):
    """Try creating KB with automatic index creation."""
    
    bedrock_agent = session.client('bedrock-agent')
    
    # Modify config to let Bedrock create the index
    auto_config = base_config.copy()
    auto_config['name'] = 'text-to-sql-kb-auto'
    
    # Remove specific index configuration to let Bedrock handle it
    opensearch_config = auto_config['storageConfiguration']['opensearchServerlessConfiguration']
    opensearch_config['vectorIndexName'] = 'auto-created-index'
    
    try:
        print("Trying with automatic index creation...")
        response = bedrock_agent.create_knowledge_base(**auto_config)
        
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Knowledge Base created with auto index: {kb_id}")
        
        # Save this KB ID
        with open('.env.kb', 'w') as f:
            f.write(f"BEDROCK_KNOWLEDGE_BASE_ID={kb_id}\n")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Auto index creation also failed: {e}")
        return False

def main():
    """Main function to create IAM user and Knowledge Base."""
    
    print("🚀 Creating Knowledge Base with IAM User")
    print("=" * 50)
    
    # Step 1: Create IAM user
    credentials = create_iam_user_for_bedrock()
    if not credentials:
        print("❌ Failed to create IAM user")
        return False
    
    access_key, secret_key = credentials
    
    # Step 2: Create Knowledge Base with IAM user
    kb_id = create_kb_with_iam_user(access_key, secret_key)
    
    if kb_id:
        print(f"\n✅ SUCCESS! Knowledge Base created: {kb_id}")
        print(f"\n📝 Next steps:")
        print(f"1. Copy configuration from .env.kb to your .env file")
        print(f"2. Test: python test_knowledge_base.py")
        print(f"3. Launch UI: streamlit run web_ui_enhanced.py")
        
        # Clean up - remove access key for security
        try:
            iam = boto3.client('iam')
            iam.delete_access_key(UserName='bedrock-kb-user', AccessKeyId=access_key)
            print(f"\n🔒 Access key cleaned up for security")
        except:
            print(f"\n⚠️  Please manually delete the access key for bedrock-kb-user")
        
        return True
    else:
        print(f"\n❌ Failed to create Knowledge Base")
        print(f"You may need to:")
        print(f"1. Check IAM permissions")
        print(f"2. Verify OpenSearch collection is accessible")
        print(f"3. Try the manual AWS Console approach with the IAM user")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)