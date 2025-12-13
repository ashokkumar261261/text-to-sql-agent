#!/usr/bin/env python3
"""
Final Knowledge Base setup - create KB and let Bedrock handle the index.
"""

import boto3
import json
import time
import os

def create_knowledge_base_final():
    """Create Knowledge Base with automatic index creation."""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    sts = boto3.client('sts')
    
    # Get account ID
    account_id = sts.get_caller_identity()['Account']
    
    # Collection details
    collection_arn = "arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445"
    kb_name = "text-to-sql-knowledge-base"
    
    try:
        print("Creating Bedrock Knowledge Base...")
        
        # Create Knowledge Base without specifying index name - let Bedrock create it
        kb_config = {
            'name': kb_name,
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
                    'vectorIndexName': f'{kb_name}-index',  # Use KB name for index
                    'fieldMapping': {
                        'vectorField': 'vector',
                        'textField': 'text', 
                        'metadataField': 'metadata'
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
        
        print(f"✅ Data source created!")
        print(f"   ID: {data_source_id}")
        
        # Start ingestion job
        print("Starting ingestion job...")
        
        ingestion_response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=data_source_id,
            description='Initial ingestion of knowledge base documents'
        )
        
        ingestion_job_id = ingestion_response['ingestionJob']['ingestionJobId']
        
        print(f"✅ Ingestion job started!")
        print(f"   Job ID: {ingestion_job_id}")
        
        # Wait for ingestion to complete
        print("Waiting for ingestion to complete (this may take a few minutes)...")
        max_wait_time = 600  # 10 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                job_response = bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=ingestion_job_id
                )
                
                status = job_response['ingestionJob']['status']
                print(f"   Ingestion status: {status}")
                
                if status == 'COMPLETE':
                    print("✅ Ingestion completed successfully!")
                    break
                elif status == 'FAILED':
                    print("❌ Ingestion failed")
                    failure_reasons = job_response['ingestionJob'].get('failureReasons', [])
                    for reason in failure_reasons:
                        print(f"   Failure reason: {reason}")
                    return False
                
                time.sleep(30)  # Wait 30 seconds between checks
                
            except Exception as e:
                print(f"   Error checking ingestion status: {e}")
                time.sleep(30)
        
        if time.time() - start_time >= max_wait_time:
            print("⚠️  Ingestion is taking longer than expected, but KB is created")
            print("   You can check the status in AWS Console")
        
        # Create .env configuration
        env_content = f"""# Add these to your .env file:
BEDROCK_KNOWLEDGE_BASE_ID={kb_id}
KB_MAX_RESULTS=10
KB_CONFIDENCE_THRESHOLD=0.7
"""
        
        with open('.env.kb', 'w') as f:
            f.write(env_content.strip())
        
        print(f"\n🎉 Knowledge Base setup complete!")
        print(f"Knowledge Base ID: {kb_id}")
        print(f"Configuration saved to .env.kb")
        
        print(f"\n📝 Next steps:")
        print(f"1. Copy the configuration from .env.kb to your .env file")
        print(f"2. Test: python test_knowledge_base.py")
        print(f"3. Launch UI: streamlit run web_ui_enhanced.py")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        
        # If it's an index error, try with a different approach
        if "no such index" in str(e):
            print("\n🔄 Trying alternative approach...")
            return create_kb_alternative()
        
        return False

def create_kb_alternative():
    """Alternative approach - create KB without custom field mapping."""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    sts = boto3.client('sts')
    
    account_id = sts.get_caller_identity()['Account']
    collection_arn = "arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445"
    
    try:
        print("Creating Knowledge Base with default settings...")
        
        # Simplified configuration
        kb_config = {
            'name': 'text-to-sql-kb-simple',
            'description': 'Knowledge base for Text-to-SQL Agent',
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
                    'vectorIndexName': 'kb-simple-index',
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
        
        print(f"✅ Alternative Knowledge Base created: {kb_id}")
        
        # Save configuration
        with open('.env.kb', 'w') as f:
            f.write(f"BEDROCK_KNOWLEDGE_BASE_ID={kb_id}\n")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Alternative approach also failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Final Knowledge Base Setup")
    print("=" * 50)
    
    kb_id = create_knowledge_base_final()
    
    if kb_id:
        print(f"\n✅ SUCCESS! Knowledge Base is ready!")
        print(f"Knowledge Base ID: {kb_id}")
        
        # Test the setup
        print(f"\n🧪 Testing the setup...")
        try:
            os.system("python test_knowledge_base.py")
        except:
            print("Run 'python test_knowledge_base.py' to test the integration")
    else:
        print(f"\n❌ Setup failed. You may need to create the Knowledge Base manually in AWS Console.")
        print(f"Use these details:")
        print(f"- S3 bucket: s3://text-to-sql-kb-demo-2024/knowledge-base/")
        print(f"- IAM role: arn:aws:iam::189796657651:role/BedrockKnowledgeBaseRole")
        print(f"- Collection: arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445")