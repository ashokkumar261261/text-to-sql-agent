#!/usr/bin/env python3
"""
Detailed test of Knowledge Base functionality.
"""

import boto3
from src.knowledge_base import BedrockKnowledgeBase

def test_knowledge_base_detailed():
    """Test Knowledge Base with detailed diagnostics."""
    
    print("🧪 Detailed Knowledge Base Test")
    print("=" * 50)
    
    # Test 1: Check Knowledge Base status
    print("1. Checking Knowledge Base status...")
    try:
        session = boto3.Session(region_name='us-east-1')
        bedrock_agent = session.client('bedrock-agent')
        
        kb_id = "JKGJVVWBDY"
        kb_details = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        
        print(f"✅ Knowledge Base found: {kb_details['knowledgeBase']['name']}")
        print(f"   Status: {kb_details['knowledgeBase']['status']}")
        print(f"   Created: {kb_details['knowledgeBase']['createdAt']}")
        
    except Exception as e:
        print(f"❌ Error getting KB details: {e}")
        return False
    
    # Test 2: Check data sources
    print("\n2. Checking data sources...")
    try:
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"✅ Data Source: {ds['name']}")
            print(f"   Status: {ds['status']}")
            print(f"   Updated: {ds['updatedAt']}")
            
            # Check ingestion jobs
            jobs = bedrock_agent.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=ds['dataSourceId']
            )
            
            print(f"   Ingestion Jobs: {len(jobs['ingestionJobSummaries'])}")
            for job in jobs['ingestionJobSummaries'][:3]:  # Show last 3 jobs
                print(f"     - {job['status']} ({job['updatedAt']})")
        
    except Exception as e:
        print(f"❌ Error checking data sources: {e}")
    
    # Test 3: Test Knowledge Base queries
    print("\n3. Testing Knowledge Base queries...")
    try:
        kb = BedrockKnowledgeBase()
        
        test_queries = [
            "customer",
            "business rules",
            "order status",
            "revenue",
            "SQL patterns",
            "electronics"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = kb.query_knowledge_base(query)
            
            if results:
                print(f"   ✅ Found {len(results)} results")
                for i, result in enumerate(results[:2], 1):  # Show top 2
                    confidence = int(result['confidence'] * 100)
                    content_preview = result['content'][:80] + "..."
                    print(f"     {i}. {confidence}% - {content_preview}")
            else:
                print(f"   ⚠️  No results")
        
    except Exception as e:
        print(f"❌ Error testing queries: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test direct Bedrock Agent Runtime
    print("\n4. Testing direct Bedrock Agent Runtime...")
    try:
        bedrock_agent_runtime = session.client('bedrock-agent-runtime')
        
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': 'customer business rules'},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        
        results = response.get('retrievalResults', [])
        print(f"✅ Direct API call returned {len(results)} results")
        
        for i, result in enumerate(results[:2], 1):
            confidence = int(result.get('score', 0) * 100)
            content_preview = result['content']['text'][:80] + "..."
            print(f"   {i}. {confidence}% - {content_preview}")
        
    except Exception as e:
        print(f"❌ Error with direct API: {e}")
    
    return True

if __name__ == "__main__":
    test_knowledge_base_detailed()