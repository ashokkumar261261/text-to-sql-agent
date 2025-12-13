#!/usr/bin/env python3
"""
Re-index the Knowledge Base documents.
"""

import boto3
import time

def reindex_knowledge_base():
    """Trigger a new ingestion job to re-index documents."""
    
    print("🔄 Re-indexing Knowledge Base")
    print("=" * 40)
    
    session = boto3.Session(region_name='us-east-1')
    bedrock_agent = session.client('bedrock-agent')
    
    kb_id = "JKGJVVWBDY"
    
    try:
        # Get data source ID
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        data_source_id = data_sources['dataSourceSummaries'][0]['dataSourceId']
        
        print(f"✅ Found data source: {data_source_id}")
        
        # Start new ingestion job
        print("🔄 Starting new ingestion job...")
        
        response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=data_source_id,
            description='Re-indexing knowledge base documents for better search'
        )
        
        job_id = response['ingestionJob']['ingestionJobId']
        print(f"✅ Ingestion job started: {job_id}")
        
        # Wait for completion
        print("⏳ Waiting for ingestion to complete...")
        
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            job_response = bedrock_agent.get_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id,
                ingestionJobId=job_id
            )
            
            status = job_response['ingestionJob']['status']
            print(f"   Status: {status}")
            
            if status == 'COMPLETE':
                print("✅ Re-indexing completed successfully!")
                
                # Test immediately
                print("\n🧪 Testing Knowledge Base after re-indexing...")
                test_after_reindex(kb_id)
                break
                
            elif status == 'FAILED':
                print("❌ Re-indexing failed")
                failure_reasons = job_response['ingestionJob'].get('failureReasons', [])
                for reason in failure_reasons:
                    print(f"   Reason: {reason}")
                break
            
            time.sleep(15)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_after_reindex(kb_id):
    """Test the Knowledge Base after re-indexing."""
    
    session = boto3.Session(region_name='us-east-1')
    bedrock_agent_runtime = session.client('bedrock-agent-runtime')
    
    test_queries = [
        "customer business rules",
        "order status",
        "revenue calculation",
        "SQL examples"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        try:
            response = bedrock_agent_runtime.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            )
            
            results = response.get('retrievalResults', [])
            
            if results:
                print(f"   ✅ Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    confidence = int(result.get('score', 0) * 100)
                    content_preview = result['content']['text'][:60] + "..."
                    print(f"     {i}. {confidence}% - {content_preview}")
            else:
                print(f"   ⚠️  No results")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    reindex_knowledge_base()