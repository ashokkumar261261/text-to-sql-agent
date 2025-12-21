import boto3
import json

# Create Bedrock Agent client
bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')

# Create Knowledge Base
response = bedrock_agent.create_knowledge_base(
    name='text-to-sql-kb-clean',
    description='Clean Knowledge Base with simple working patterns only',
    roleArn='arn:aws:iam::189796657651:role/BedrockKnowledgeBaseRole',
    knowledgeBaseConfiguration={
        'type': 'VECTOR',
        'vectorKnowledgeBaseConfiguration': {
            'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1'
        }
    },
    storageConfiguration={
        'type': 'OPENSEARCH_SERVERLESS',
        'opensearchServerlessConfiguration': {
            'collectionArn': 'arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445',
            'vectorIndexName': 'bedrock-knowledge-base-clean-index',
            'fieldMapping': {
                'vectorField': 'bedrock-knowledge-base-clean-vector',
                'textField': 'AMAZON_BEDROCK_TEXT_CHUNK',
                'metadataField': 'AMAZON_BEDROCK_METADATA'
            }
        }
    }
)

kb_id = response['knowledgeBase']['knowledgeBaseId']
print(f"Knowledge Base created: {kb_id}")

# Create Data Source
ds_response = bedrock_agent.create_data_source(
    knowledgeBaseId=kb_id,
    name='text-to-sql-s3-clean',
    description='S3 data source with clean simple patterns',
    dataSourceConfiguration={
        'type': 'S3',
        's3Configuration': {
            'bucketArn': 'arn:aws:s3:::text-to-sql-kb-demo-2024'
        }
    }
)

ds_id = ds_response['dataSource']['dataSourceId']
print(f"Data Source created: {ds_id}")

# Start ingestion
ing_response = bedrock_agent.start_ingestion_job(
    knowledgeBaseId=kb_id,
    dataSourceId=ds_id
)

print(f"Ingestion job started: {ing_response['ingestionJob']['ingestionJobId']}")
print(f"\nUpdate Lambda environment variable:")
print(f"BEDROCK_KNOWLEDGE_BASE_ID={kb_id}")
