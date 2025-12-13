#!/usr/bin/env python3
"""
Simple test to check if query execution is working in the agent.
"""

from src.enhanced_agent import EnhancedTextToSQLAgent

def test_query_execution():
    """Test query execution with a simple query."""
    
    print("🧪 Testing Query Execution")
    print("=" * 40)
    
    try:
        # Initialize agent
        agent = EnhancedTextToSQLAgent(
            session_id="execution_test",
            enable_knowledge_base=True
        )
        
        print("✅ Agent initialized")
        
        # Test 1: Generate SQL only (no execution)
        print("\n1️⃣ Testing SQL generation only...")
        result1 = agent.query(
            "give me email of Eve Davis",
            execute=False  # Don't execute
        )
        
        if 'sql_query' in result1:
            print(f"✅ SQL Generated: {result1['sql_query']}")
        else:
            print(f"❌ No SQL generated: {result1}")
        
        # Test 2: Try to execute the query
        print("\n2️⃣ Testing SQL execution...")
        result2 = agent.query(
            "give me email of Eve Davis",
            execute=True  # Try to execute
        )
        
        print(f"📋 Result keys: {list(result2.keys())}")
        
        if 'error' in result2:
            print(f"❌ Execution Error: {result2['error']}")
        elif 'results' in result2:
            print(f"✅ Query executed successfully!")
            print(f"   Results: {result2['results']}")
            print(f"   Row count: {result2.get('row_count', 0)}")
        else:
            print(f"⚠️  Query generated but not executed")
            if 'sql_query' in result2:
                print(f"   SQL: {result2['sql_query']}")
        
        return result2
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_web_ui_execution():
    """Check if the web UI is configured to execute queries."""
    
    print(f"\n🌐 Web UI Execution Check")
    print("-" * 30)
    
    print("In the web UI, make sure to:")
    print("1. ✅ Check the 'Execute Query' checkbox in the sidebar")
    print("2. ✅ Verify your database configuration in .env:")
    print(f"   - GLUE_DATABASE=text_to_sql_demo")
    print(f"   - ATHENA_OUTPUT_LOCATION=s3://text-to-sql-kb-demo-2024/athena-results/")
    print("3. ✅ Ensure you have proper AWS permissions for Athena")

if __name__ == "__main__":
    result = test_query_execution()
    check_web_ui_execution()
    
    if result and 'results' in result:
        print(f"\n🎉 SUCCESS! Query execution is working.")
    else:
        print(f"\n⚠️  Query execution may not be enabled or configured properly.")