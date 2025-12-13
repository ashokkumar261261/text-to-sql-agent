#!/usr/bin/env python3
"""
Create Knowledge Base using default vector store (no OpenSearch required).
"""

import boto3
import json
import time

def create_knowledge_base_default():
    """Create Knowledge Base with default vector store."""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    sts = boto3.client('sts')
    
    account_id = sts.get_caller_identity()['Account']
    
    try:
        print("Creating Knowledge Base with default vector store...")
        
        # Create Knowledge Base without OpenSearch - use default vector store
        kb_config = {
            'name': 'text-to-sql-kb-default',
            'description': 'Knowledge base for Text-to-SQL Agent using default vector store',
            'roleArn': f'arn:aws:iam::{account_id}:role/BedrockKnowledgeBaseRole',
            'knowledgeBaseConfiguration': {
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
                }
            }
            # No storageConfiguration - use default
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
        max_wait = 600  # 10 minutes
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
                
                time.sleep(20)
                
            except Exception as e:
                print(f"   Error checking status: {e}")
                time.sleep(20)
        
        # Save configuration
        env_content = f"""# Add these to your .env file:
BEDROCK_KNOWLEDGE_BASE_ID={kb_id}
KB_MAX_RESULTS=10
KB_CONFIDENCE_THRESHOLD=0.7
"""
        
        with open('.env.kb', 'w') as f:
            f.write(env_content)
        
        print(f"\n🎉 Knowledge Base setup complete!")
        print(f"Knowledge Base ID: {kb_id}")
        print(f"Configuration saved to .env.kb")
        
        print(f"\n📝 Next steps:")
        print(f"1. Copy configuration from .env.kb to your .env file")
        print(f"2. Test: python test_knowledge_base.py")
        print(f"3. Launch UI: streamlit run web_ui_enhanced.py")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Knowledge Base with Default Vector Store")
    print("=" * 60)
    
    kb_id = create_knowledge_base_default()
    
    if kb_id:
        print(f"\n✅ SUCCESS! Knowledge Base is ready!")
        print(f"Knowledge Base ID: {kb_id}")
    else:
        print(f"\n❌ Failed to create Knowledge Base")
        print(f"Check AWS permissions and try again")