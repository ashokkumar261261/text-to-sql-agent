#!/usr/bin/env python3
"""
Enhanced example demonstrating all new features:
- Query validation
- Result caching
- Query explanations
- Conversation history
"""

from src.agent import TextToSQLAgent
from src.schema import SchemaManager
import time


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_basic_query():
    """Example 1: Basic query with validation and explanation."""
    print_section("Example 1: Basic Query with Validation & Explanation")
    
    agent = TextToSQLAgent()
    
    query = "Show me all customers from Texas"
    print(f"Question: {query}\n")
    
    result = agent.query(
        query,
        execute=False,
        explain=True,
        validate=True
    )
    
    # Check for errors
    if 'error' in result:
        print(f"❌ Error: {result['error']}\n")
        return
    
    print(f"Generated SQL:\n{result['sql_query']}\n")
    
    # Show validation results
    if 'validation' in result:
        validation = result['validation']
        print(f"✓ Validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")
        if validation.get('warnings'):
            print("  Warnings:")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        print()
    
    # Show query info
    if 'query_info' in result:
        info = result['query_info']
        print(f"Query Info:")
        print(f"  - Tables: {', '.join(info['tables'])}")
        print(f"  - Complexity: {info['estimated_complexity']}")
        print(f"  - Has Joins: {info['has_joins']}")
        print(f"  - Has Aggregation: {info['has_aggregation']}")
        print()
    
    # Show explanation
    if 'explanation' in result:
        print(f"Explanation:\n{result['explanation']}\n")


def example_caching():
    """Example 2: Demonstrate query caching."""
    print_section("Example 2: Query Caching")
    
    agent = TextToSQLAgent()
    
    query = "Count all orders"
    print(f"Question: {query}\n")
    
    # First execution
    print("First execution (no cache)...")
    start = time.time()
    result1 = agent.query(query, execute=True, use_cache=True)
    time1 = time.time() - start
    
    if 'error' in result1:
        print(f"❌ Error: {result1['error']}\n")
        return
    
    print(f"SQL: {result1['sql_query']}")
    print(f"Results: {result1.get('row_count', 0)} rows")
    print(f"Cached: {result1.get('cached', False)}")
    print(f"Time: {time1:.2f}s\n")
    
    # Second execution (should use cache)
    print("Second execution (with cache)...")
    start = time.time()
    result2 = agent.query(query, execute=True, use_cache=True)
    time2 = time.time() - start
    
    if 'error' in result2:
        print(f"❌ Error: {result2['error']}\n")
        return
    
    print(f"Results: {result2.get('row_count', 0)} rows")
    print(f"Cached: {result2.get('cached', False)}")
    print(f"Time: {time2:.2f}s")
    print(f"Speedup: {time1/time2:.1f}x faster!\n")
    
    # Show cache stats
    cache_stats = agent.get_cache_stats()
    print(f"Cache Stats:")
    print(f"  - Memory entries: {cache_stats.get('memory_entries', 0)}")
    print(f"  - Total hits: {cache_stats.get('total_hits', 0)}")


def example_conversation():
    """Example 3: Conversation with follow-up questions."""
    print_section("Example 3: Conversation with Follow-up Questions")
    
    agent = TextToSQLAgent(session_id="demo_session")
    
    queries = [
        "Show me all products in the Electronics category",
        "What about Furniture?",  # Follow-up
        "Show me the most expensive one",  # Follow-up
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"Question {i}: {query}")
        
        result = agent.query(query, execute=False, validate=True)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}\n")
            continue
        
        print(f"SQL: {result['sql_query']}")
        
        if 'validation' in result and result['validation']['is_valid']:
            print("✓ Valid query")
        
        print()
    
    # Show conversation summary
    summary = agent.get_conversation_summary()
    print(f"Conversation Summary:")
    print(f"  - Session ID: {summary['session_id']}")
    print(f"  - Total messages: {summary['message_count']}")
    print(f"  - Queries executed: {summary['queries_executed']}")


def example_validation():
    """Example 4: Query validation catching dangerous queries."""
    print_section("Example 4: Query Validation")
    
    agent = TextToSQLAgent()
    
    # Try a dangerous query (this should be blocked)
    dangerous_queries = [
        "Delete all customers",
        "Drop the orders table",
        "Update all prices to 0"
    ]
    
    print("Testing dangerous queries (should be blocked):\n")
    
    for query in dangerous_queries:
        print(f"Question: {query}")
        result = agent.query(query, execute=False, validate=True)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}\n")
            continue
        
        if 'validation' in result:
            validation = result['validation']
            if not validation['is_valid']:
                print(f"✓ BLOCKED: {validation['error']}")
            else:
                print(f"✗ WARNING: Query was not blocked!")
        print()


def example_complex_query():
    """Example 5: Complex query with joins and aggregations."""
    print_section("Example 5: Complex Query Analysis")
    
    agent = TextToSQLAgent()
    
    query = "Show me the total revenue by product category and count of orders"
    print(f"Question: {query}\n")
    
    result = agent.query(
        query,
        execute=True,
        explain=True,
        validate=True
    )
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}\n")
        return
    
    print(f"Generated SQL:\n{result['sql_query']}\n")
    
    # Show query complexity
    if 'query_info' in result:
        info = result['query_info']
        print(f"Query Analysis:")
        print(f"  - Complexity: {info['estimated_complexity']}")
        print(f"  - Tables used: {', '.join(info['tables'])}")
        print(f"  - Has joins: {info['has_joins']}")
        print(f"  - Has aggregation: {info['has_aggregation']}")
        print(f"  - Has GROUP BY: {info['has_groupby']}")
        print()
    
    # Show explanation
    if 'explanation' in result:
        print(f"Explanation:\n{result['explanation']}\n")
    
    # Show results
    if result.get('executed') and 'results' in result:
        print(f"Results ({result['row_count']} rows):")
        for i, row in enumerate(result['results'][:5], 1):
            print(f"  {i}. {row}")
        if result['row_count'] > 5:
            print(f"  ... and {result['row_count'] - 5} more rows")


def example_session_management():
    """Example 6: Managing multiple sessions."""
    print_section("Example 6: Session Management")
    
    # Create two different sessions
    session1 = TextToSQLAgent(session_id="user_alice")
    session2 = TextToSQLAgent(session_id="user_bob")
    
    # Alice's queries
    print("Alice's session:")
    try:
        session1.query("Show me all customers", execute=False)
        session1.query("Count the orders", execute=False)
    except Exception as e:
        print(f"  Error: {e}")
    
    summary1 = session1.get_conversation_summary()
    print(f"  - Session: {summary1['session_id']}")
    print(f"  - Queries: {summary1['queries_executed']}")
    print()
    
    # Bob's queries
    print("Bob's session:")
    try:
        session2.query("List all products", execute=False)
    except Exception as e:
        print(f"  Error: {e}")
    
    summary2 = session2.get_conversation_summary()
    print(f"  - Session: {summary2['session_id']}")
    print(f"  - Queries: {summary2['queries_executed']}")
    print()
    
    # List all sessions
    from src.conversation import ConversationHistory
    sessions = ConversationHistory.list_sessions()
    print(f"Total sessions: {len(sessions)}")
    for session in sessions[:5]:
        print(f"  - {session['session_id']}: {session['message_count']} messages")


def main():
    print("\n" + "=" * 70)
    print("  Enhanced Text-to-SQL Agent Examples")
    print("  Demonstrating: Validation, Caching, Explanations, Conversations")
    print("=" * 70)
    
    try:
        # Run examples
        example_basic_query()
        example_caching()
        example_conversation()
        example_validation()
        example_complex_query()
        example_session_management()
        
        print("\n" + "=" * 70)
        print("  ✅ All examples completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Try the web UI: .\\run.bat -m streamlit run web_ui.py")
        print("  2. Explore conversation history in .history/ folder")
        print("  3. Check query cache in .cache/ folder")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("  - Configured AWS credentials")
        print("  - Set up Glue database and tables")
        print("  - Enabled Bedrock model access")


if __name__ == "__main__":
    main()
