#!/usr/bin/env python3
"""
Test only the Knowledge Base functionality without database connection.
"""

import os
from src.knowledge_base import BedrockKnowledgeBase

def test_knowledge_base_only():
    """Test just the Knowledge Base retrieval."""
    
    print("🧪 Testing Knowledge Base Only")
    print("=" * 40)
    
    try:
        # Test Knowledge Base directly
        kb = BedrockKnowledgeBase()
        
        print(f"✅ Knowledge Base initialized")
        print(f"KB ID: {kb.knowledge_base_id}")
        
        # Test query
        test_query = "show me business rules for customer data"
        print(f"\n🔍 Testing query: '{test_query}'")
        
        results = kb.query_knowledge_base(test_query)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                confidence = int(result['confidence'] * 100)
                content_preview = result['content'][:100] + "..."
                print(f"   {i}. Confidence: {confidence}% - {content_preview}")
        else:
            print("⚠️  No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_knowledge_base_only()