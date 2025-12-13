#!/usr/bin/env python3
"""
Test simple SQL generation without Knowledge Base first.
"""

from src.agent import TextToSQLAgent

def test_simple_sql_generation():
    """Test basic SQL generation without Knowledge Base."""
    
    print("🧪 Testing Simple SQL Generation (No KB)")
    print("=" * 50)
    
    try:
        # Use the basic agent first
        agent = TextToSQLAgent()
        
        print("✅ Basic agent initialized")
        
        # Test query
        query = "show me all customers from texas who ordered electronics"
        print(f"\n🔍 Query: '{query}'")
        
        result = agent.query(
            query,
            execute=False  # Don't execute, just generate SQL
        )
        
        print(f"\n📋 Result:")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ SQL Generated: {result['sql_query']}")
            if 'explanation' in result:
                print(f"📝 Explanation: {result['explanation']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_simple_sql_generation()