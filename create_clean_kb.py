#!/usr/bin/env python3
"""
Create clean Bedrock Knowledge Base using the same approach as main branch
but with clean, simple SQL patterns only.
"""

import boto3
import json
import time

def create_clean_knowledge_base():
    """Create Bedrock Knowledge Base with clean content using existing infrastructure."""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    opensearch = boto3.client('opensearchserverless', region_name='us-east-1')
    sts = boto3.client('sts')
    
    # Get account ID
    account_id = sts.get_caller_identity()['Account']
    
    # Use existing collection details
    collection_name = "text-to-sql-collection"
    kb_name = "text-to-sql-kb-clean"
    
    print("🔍 Checking existing OpenSearch collection...")
    try:
        response = opensearch.batch_get_collection(names=[collection_name])
        if response['collectionDetails']:
            collection_details = response['collectionDetails'][0]
            status = collection_details['status']
            collection_arn = collection_details['arn']
            collection_endpoint = collection_details['collectionEndpoint']
            
            print(f"✅ Found collection: {collection_name}")
            print(f"   Status: {status}")
            print(f"   ARN: {collection_arn}")
            
            if status != 'ACTIVE':
                print(f"❌ Collection is not active (status: {status})")
                return False
        else:
            print("❌ Collection not found")
            return False
    except Exception as e:
        print(f"❌ Error checking collection: {e}")
        return False
    
    # Create Knowledge Base with clean configuration
    try:
        print("🚀 Creating clean Bedrock Knowledge Base...")
        
        # Use a unique index name to avoid conflicts
        index_name = f"bedrock-kb-clean-{int(time.time())}"
        
        kb_config = {
            'name': kb_name,
            'description': 'Clean Knowledge Base with simple SQL patterns only - no HAVING clauses',
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
                    'vectorIndexName': index_name,
                    'fieldMapping': {
                        'vectorField': 'bedrock-kb-clean-vector',
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
        print(f"   Index: {index_name}")
        
        # Create data source pointing to our clean S3 bucket
        print("📂 Creating data source...")
        
        data_source_config = {
            'knowledgeBaseId': kb_id,
            'name': 'text-to-sql-s3-clean-source',
            'description': 'S3 data source with clean simple SQL patterns',
            'dataSourceConfiguration': {
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::text-to-sql-kb-demo-2024'
                    # No inclusionPrefixes - use all files in bucket
                }
            }
        }
        
        ds_response = bedrock_agent.create_data_source(**data_source_config)
        
        data_source_id = ds_response['dataSource']['dataSourceId']
        
        print(f"✅ Data source created!")
        print(f"   ID: {data_source_id}")
        
        # Start ingestion job
        print("🔄 Starting ingestion job...")
        
        ingestion_response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=data_source_id,
            description='Ingestion of clean SQL patterns'
        )
        
        ingestion_job_id = ingestion_response['ingestionJob']['ingestionJobId']
        
        print(f"✅ Ingestion job started!")
        print(f"   Job ID: {ingestion_job_id}")
        
        # Wait for ingestion to complete
        print("⏳ Waiting for ingestion to complete...")
        max_attempts = 20  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                job_response = bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=ingestion_job_id
                )
                
                status = job_response['ingestionJob']['status']
                stats = job_response['ingestionJob'].get('statistics', {})
                
                print(f"   Status: {status}")
                if stats:
                    docs_scanned = stats.get('numberOfDocumentsScanned', 0)
                    docs_indexed = stats.get('numberOfNewDocumentsIndexed', 0)
                    print(f"   Documents: {docs_scanned} scanned, {docs_indexed} indexed")
                
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
                attempt += 1
                
            except Exception as e:
                print(f"   Error checking ingestion status: {e}")
                time.sleep(15)
                attempt += 1
        
        if attempt >= max_attempts:
            print("⚠️ Ingestion taking longer than expected, but continuing...")
        
        # Update Lambda environment variable
        print("🔧 Updating Lambda environment...")
        try:
            lambda_client = boto3.client('lambda', region_name='us-east-1')
            
            lambda_client.update_function_configuration(
                FunctionName='text-to-sql-agent-demo',
                Environment={
                    'Variables': {
                        'BEDROCK_KNOWLEDGE_BASE_ID': kb_id,
                        'GLUE_DATABASE': 'text_to_sql_demo',
                        'BEDROCK_MODEL_ID': 'amazon.titan-text-express-v1',
                        'ATHENA_OUTPUT_LOCATION': 's3://text-to-sql-athena-results/'
                    }
                }
            )
            print("✅ Lambda environment updated!")
        except Exception as e:
            print(f"⚠️ Warning: Failed to update Lambda environment: {e}")
            print(f"   Please manually update BEDROCK_KNOWLEDGE_BASE_ID to: {kb_id}")
        
        print(f"\n🎉 Clean Knowledge Base setup complete!")
        print(f"="*60)
        print(f"Knowledge Base ID: {kb_id}")
        print(f"Data Source ID: {data_source_id}")
        print(f"Collection Endpoint: {collection_endpoint}")
        print(f"Vector Index: {index_name}")
        
        # Save configuration
        config = {
            'knowledge_base_id': kb_id,
            'data_source_id': data_source_id,
            'collection_arn': collection_arn,
            'index_name': index_name,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
        
        with open('.env.kb.clean', 'w') as f:
            f.write(f"# Clean Knowledge Base Configuration\\n")
            f.write(f"BEDROCK_KNOWLEDGE_BASE_ID={kb_id}\\n")
            f.write(f"KB_DATA_SOURCE_ID={data_source_id}\\n")
            f.write(f"KB_COLLECTION_ARN={collection_arn}\\n")
            f.write(f"KB_INDEX_NAME={index_name}\\n")
        
        with open('kb_clean_info.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\\n📝 Configuration saved to:")
        print(f"   - .env.kb.clean")
        print(f"   - kb_clean_info.json")
        
        print(f"\\n🧪 Ready to test!")
        print(f"Query: 'Show me top 5 customers by revenue'")
        print(f"Expected SQL:")
        print(f"SELECT c.name, c.email, c.city,")
        print(f"       SUM(o.total_amount) as total_revenue")
        print(f"FROM text_to_sql_demo.customers c")
        print(f"JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id")
        print(f"GROUP BY c.customer_id, c.name, c.email, c.city")
        print(f"ORDER BY total_revenue DESC")
        print(f"LIMIT 5;")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Creating clean Knowledge Base for Text-to-SQL Agent")
    print("="*60)
    
    kb_id = create_clean_knowledge_base()
    if kb_id:
        print(f"\\n✅ SUCCESS! Clean Knowledge Base is ready.")
        print(f"Knowledge Base ID: {kb_id}")
        print(f"\\nYou can now test the query: 'Show me top 5 customers by revenue'")
    else:
        print("\\n❌ Failed to create clean Knowledge Base")
        print("Check the error messages above and try again.")