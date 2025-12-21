#!/usr/bin/env python3
"""
Simple test script to verify the text-to-SQL system is working with Titan model
"""

import boto3
import json

def test_titan_model():
    """Test Titan model directly"""
    print("Testing Titan model access...")
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        body = json.dumps({
            "inputText": "Generate SQL to find top 5 customers by revenue",
            "textGenerationConfig": {
                "maxTokenCount": 200,
                "temperature": 0.1,
                "topP": 0.9
            }
        })
        
        response = bedrock_runtime.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=body,
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        print("✅ Titan model working!")
        print("Response:", response_body['results'][0]['outputText'][:200] + "...")
        return True
        
    except Exception as e:
        print(f"❌ Titan model error: {str(e)}")
        return False

def test_knowledge_base():
    """Test Knowledge Base access"""
    print("\nTesting Knowledge Base access...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        response = bedrock_agent.retrieve(
            knowledgeBaseId='MJ2GCTRK6Z',
            retrievalQuery={
                'text': 'top customers by revenue'
            }
        )
        
        results = response.get('retrievalResults', [])
        print(f"✅ Knowledge Base working! Retrieved {len(results)} results")
        return True
        
    except Exception as e:
        print(f"❌ Knowledge Base error: {str(e)}")
        return False

def main():
    print("=== Text-to-SQL System Test ===\n")
    
    titan_ok = test_titan_model()
    kb_ok = test_knowledge_base()
    
    print(f"\n=== Results ===")
    print(f"Titan Model: {'✅ Working' if titan_ok else '❌ Failed'}")
    print(f"Knowledge Base: {'✅ Working' if kb_ok else '❌ Failed'}")
    
    if titan_ok and kb_ok:
        print("\n🎉 System is ready! You can now test with:")
        print("Query: 'Show me top 5 customers by revenue'")
        print("\nExpected SQL:")
        print("""SELECT 
    c.customer_name,
    c.email,
    SUM(o.total_amount) as total_revenue,
    COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'delivered'
GROUP BY c.customer_id, c.customer_name, c.email
ORDER BY total_revenue DESC
LIMIT 5;""")

if __name__ == "__main__":
    main()