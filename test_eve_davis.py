#!/usr/bin/env python3
"""
Direct test of the Eve Davis query.
"""

from src.enhanced_agent import EnhancedTextToSQLAgent

def test_eve_davis_query():
    """Test the specific Eve Davis query."""
    
    print("🧪 Testing Eve Davis Query")
    print("=" * 40)
    
    try:
        agent = EnhancedTextToSQLAgent(
            session_id="eve_test",
            enable_knowledge_base=True
        )
        
        print("✅ Agent initialized")
        
        # Test the exact query
        query = "give me email of Eve Davis"
        print(f"\n🔍 Query: '{query}'")
        
        # Execute the query
        result = agent.query(
            query,
            execute=True,  # IMPORTANT: Execute the query
            explain=True
        )
        
        print(f"\n📋 Results:")
        print(f"   Keys: {list(result.keys())}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ SQL: {result['sql_query']}")
            
            if 'results' in result:
                print(f"✅ Execution successful!")
                print(f"   Results: {result['results']}")
                print(f"   Row count: {result.get('row_count', 0)}")
                
                # Show the actual email
                if result['results']:
                    email = result['results'][0].get('email', 'No email found')
                    print(f"🎯 Eve Davis's email: {email}")
                else:
                    print(f"⚠️  No results returned (Eve Davis might not exist in the data)")
            else:
                print(f"⚠️  Query generated but not executed")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_eve_davis_query()
    
    print(f"\n💡 Web UI Instructions:")
    print(f"1. Go to http://localhost:8501")
    print(f"2. In the sidebar, CHECK the 'Execute Query' checkbox")
    print(f"3. Enter: 'give me email of Eve Davis'")
    print(f"4. Click 'Process Query'")
    print(f"5. You should see both the SQL AND the actual email result")