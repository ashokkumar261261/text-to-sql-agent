#!/usr/bin/env python3
"""
Simple test of the enhanced agent with a basic query.
"""

from src.enhanced_agent import EnhancedTextToSQLAgent

def test_simple_query():
    """Test a simple query to debug the issue."""
    
    print("🧪 Testing Enhanced Agent with Simple Query")
    print("=" * 50)
    
    try:
        # Initialize agent
        agent = EnhancedTextToSQLAgent(
            session_id="test_session",
            enable_knowledge_base=True
        )
        
        print("✅ Agent initialized successfully")
        
        # Test query
        query = "show me all customers from texas who ordered electronics"
        print(f"\n🔍 Testing query: '{query}'")
        
        result = agent.query(
            query,
            execute=False,  # Don't execute, just generate SQL
            use_knowledge_base=True,
            explain=True
        )
        
        print(f"\n📋 Result keys: {list(result.keys())}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success!")
            if 'sql_query' in result:
                print(f"SQL: {result['sql_query']}")
            if 'explanation' in result:
                print(f"Explanation: {result['explanation'][:100]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_simple_query()