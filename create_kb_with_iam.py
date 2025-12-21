#!/usr/bin/env python3
"""
Create Knowledge Base using AWS CLI with IAM credentials
"""

import subprocess
import json
import time

def run_aws_command(command):
    """Run AWS CLI command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout.strip() else {}
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Command failed: {e}")
        return None

def create_knowledge_base():
    """Create Knowledge Base using AWS CLI"""
    
    print("🚀 Creating Knowledge Base with IAM credentials...")
    
    # Step 1: Create Knowledge Base with auto-generated index
    kb_config = {
        "name": "text-to-sql-kb-clean",
        "description": "Clean Knowledge Base with simple SQL patterns",
        "roleArn": "arn:aws:iam::189796657651:role/BedrockKnowledgeBaseRole",
        "knowledgeBaseConfiguration": {
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {
                "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
            }
        },
        "storageConfiguration": {
            "type": "OPENSEARCH_SERVERLESS",
            "opensearchServerlessConfiguration": {
                "collectionArn": "arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445",
                "vectorIndexName": f"kb-clean-{int(time.time())}",  # Unique index name
                "fieldMapping": {
                    "vectorField": "vector",
                    "textField": "text",
                    "metadataField": "metadata"
                }
            }
        }
    }
    
    # Write config to file
    with open('kb_final_config.json', 'w') as f:
        json.dump(kb_config, f, indent=2)
    
    print("📝 Created KB configuration file: kb_final_config.json")
    
    # Create Knowledge Base
    print("🔨 Creating Knowledge Base...")
    kb_result = run_aws_command('aws bedrock-agent create-knowledge-base --cli-input-json file://kb_final_config.json')
    
    if not kb_result:
        print("❌ Failed to create Knowledge Base")
        return None
    
    kb_id = kb_result['knowledgeBase']['knowledgeBaseId']
    print(f"✅ Knowledge Base created: {kb_id}")
    
    # Step 2: Create Data Source
    print("📂 Creating Data Source...")
    ds_config = {
        "knowledgeBaseId": kb_id,
        "name": "s3-clean-source",
        "description": "S3 source with clean SQL patterns",
        "dataSourceConfiguration": {
            "type": "S3",
            "s3Configuration": {
                "bucketArn": "arn:aws:s3:::text-to-sql-kb-demo-2024"
            }
        }
    }
    
    with open('ds_config.json', 'w') as f:
        json.dump(ds_config, f, indent=2)
    
    ds_result = run_aws_command('aws bedrock-agent create-data-source --cli-input-json file://ds_config.json')
    
    if not ds_result:
        print("❌ Failed to create Data Source")
        return None
    
    ds_id = ds_result['dataSource']['dataSourceId']
    print(f"✅ Data Source created: {ds_id}")
    
    # Step 3: Start Ingestion
    print("🔄 Starting ingestion job...")
    ingestion_result = run_aws_command(f'aws bedrock-agent start-ingestion-job --knowledge-base-id {kb_id} --data-source-id {ds_id}')
    
    if ingestion_result:
        job_id = ingestion_result['ingestionJob']['ingestionJobId']
        print(f"✅ Ingestion job started: {job_id}")
        
        # Wait for ingestion to complete
        print("⏳ Waiting for ingestion to complete...")
        for i in range(30):  # Wait up to 5 minutes
            time.sleep(10)
            status_result = run_aws_command(f'aws bedrock-agent get-ingestion-job --knowledge-base-id {kb_id} --data-source-id {ds_id} --ingestion-job-id {job_id}')
            
            if status_result:
                status = status_result['ingestionJob']['status']
                print(f"📊 Ingestion status: {status}")
                
                if status == 'COMPLETE':
                    print("✅ Ingestion completed successfully!")
                    break
                elif status == 'FAILED':
                    print("❌ Ingestion failed!")
                    return None
    
    # Step 4: Update Lambda Environment
    print("🔧 Updating Lambda environment...")
    lambda_result = run_aws_command(f'''aws lambda update-function-configuration --function-name text-to-sql-agent-demo --environment "Variables={{BEDROCK_KNOWLEDGE_BASE_ID={kb_id},GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}}"''')
    
    if lambda_result:
        print("✅ Lambda environment updated!")
    
    print(f"""
🎉 SUCCESS! Knowledge Base setup complete:

📋 Details:
- Knowledge Base ID: {kb_id}
- Data Source ID: {ds_id}
- Lambda Function: Updated with new KB ID

🧪 Test Query:
Now you can test: "Show me top 5 customers by revenue"

Expected SQL:
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
""")
    
    return kb_id

if __name__ == "__main__":
    create_knowledge_base()