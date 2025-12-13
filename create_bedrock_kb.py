#!/usr/bin/env python3
"""
Create Bedrock Knowledge Base after OpenSearch collection is ready.
"""

import boto3
import json
import time

def create_bedrock_knowledge_base():
    """Create Bedrock Knowledge Base with the OpenSearch collection."""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    opensearch = boto3.client('opensearchserverless', region_name='us-east-1')
    sts = boto3.client('sts')
    
    # Get account ID
    account_id = sts.get_caller_identity()['Account']
    
    # Collection details
    collection_name = "text-to-sql-collection"
    kb_name = "text-to-sql-knowledge-base"
    
    # Wait for collection to be active
    print("Checking OpenSearch collection status...")
    while True:
        try:
            response = opensearch.batch_get_collection(names=[collection_name])
            if response['collectionDetails']:
                status = response['collectionDetails'][0]['status']
                collection_arn = response['collectionDetails'][0]['arn']
                collection_endpoint = response['collectionDetails'][0]['collectionEndpoint']
                
                print(f"Collection status: {status}")
                
                if status == 'ACTIVE':
                    print("✅ Collection is active!")
                    break
                elif status == 'FAILED':
                    print("❌ Collection creation failed")
                    return False
                    
                time.sleep(10)
            else:
                print("❌ Collection not found")
                return False
        except Exception as e:
            print(f"❌ Error checking collection: {e}")
            return False
    
    # Create Knowledge Base
    try:
        print("Creating Bedrock Knowledge Base...")
        
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
        print("Waiting for ingestion to complete...")
        while True:
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
            
            time.sleep(15)
        
        print(f"\n🎉 Knowledge Base setup complete!")
        print(f"Knowledge Base ID: {kb_id}")
        print(f"Collection Endpoint: {collection_endpoint}")
        
        # Update .env file
        env_content = f"""
# Add this to your .env file:
BEDROCK_KNOWLEDGE_BASE_ID={kb_id}
KB_MAX_RESULTS=10
KB_CONFIDENCE_THRESHOLD=0.7
"""
        
        with open('.env.kb', 'w') as f:
            f.write(env_content.strip())
        
        print(f"\n📝 Configuration saved to .env.kb")
        print(f"Copy these values to your .env file:")
        print(env_content)
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        return False

if __name__ == "__main__":
    kb_id = create_bedrock_knowledge_base()
    if kb_id:
        print(f"\n✅ Success! Your Knowledge Base is ready to use.")
        print(f"Run: python test_knowledge_base.py")
    else:
        print("❌ Failed to create Knowledge Base")