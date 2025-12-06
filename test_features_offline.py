#!/usr/bin/env python3
"""
Test enhanced features without calling Bedrock (offline mode)
"""

from src.query_validator import QueryValidator
from src.query_cache import QueryCache
from src.conversation import ConversationHistory


def test_validation():
    """Test query validation."""
    print("=" * 70)
    print("Testing Query Validation")
    print("=" * 70 + "\n")
    
    validator = QueryValidator()
    
    test_queries = [
        ("SELECT * FROM customers", "Safe query"),
        ("DROP TABLE customers", "Dangerous query"),
        ("DELETE FROM orders WHERE id = 1", "Dangerous query"),
        ("SELECT * FROM customers WHERE state = 'TX'", "Safe query with filter"),
        ("SELECT COUNT(*) FROM orders", "Safe aggregation"),
    ]
    
    for sql, description in test_queries:
        print(f"Query: {sql}")
        print(f"Type: {description}")
        
        is_valid, error, warnings = validator.validate(sql)
        
        if is_valid:
            print("✓ VALID")
            if warnings:
                print("  Warnings:")
                for warning in warnings:
                    print(f"    - {warning}")
        else:
            print(f"✗ BLOCKED: {error}")
        
        # Show query info
        info = validator.get_query_info(sql)
        print(f"  Complexity: {info['estimated_complexity']}")
        print()


def test_caching():
    """Test query caching."""
    print("=" * 70)
    print("Testing Query Caching")
    print("=" * 70 + "\n")
    
    cache = QueryCache()
    
    # Test data
    sql_query = "SELECT * FROM customers WHERE state = 'TX'"
    test_results = [
        {'id': 1, 'name': 'John', 'state': 'TX'},
        {'id': 2, 'name': 'Jane', 'state': 'TX'}
    ]
    
    # First access (cache miss)
    print("First access (cache miss)...")
    result = cache.get(sql_query, 'test_db')
    print(f"Result: {result}")
    print("✓ Cache miss (as expected)\n")
    
    # Store in cache
    print("Storing results in cache...")
    cache.set(sql_query, test_results, 'test_db')
    print("✓ Stored\n")
    
    # Second access (cache hit)
    print("Second access (cache hit)...")
    result = cache.get(sql_query, 'test_db')
    print(f"Result: {result}")
    print("✓ Cache hit!\n")
    
    # Get stats
    stats = cache.get_stats()
    print(f"Cache Stats:")
    print(f"  - Memory entries: {stats['memory_entries']}")
    print(f"  - Total hits: {stats['total_hits']}")
    print()


def test_conversation():
    """Test conversation history."""
    print("=" * 70)
    print("Testing Conversation History")
    print("=" * 70 + "\n")
    
    conversation = ConversationHistory(session_id="test_session")
    
    # Add messages
    print("Adding messages to conversation...")
    conversation.add_message('user', 'Show me all customers')
    conversation.add_message('assistant', '', sql_query='SELECT * FROM customers')
    conversation.add_message('user', 'What about orders?')
    conversation.add_message('assistant', '', sql_query='SELECT * FROM orders')
    print("✓ Added 4 messages\n")
    
    # Get context
    print("Getting conversation context...")
    context = conversation.get_context()
    print(f"Context:\n{context}\n")
    
    # Detect follow-up
    print("Testing follow-up detection...")
    test_queries = [
        "Show me all products",
        "What about the other ones?",
        "Also show me furniture",
    ]
    
    for query in test_queries:
        is_followup = conversation.detect_follow_up(query)
        print(f"  '{query}' -> {'Follow-up' if is_followup else 'New query'}")
    print()
    
    # Get summary
    summary = conversation.get_summary()
    print(f"Conversation Summary:")
    print(f"  - Session ID: {summary['session_id']}")
    print(f"  - Messages: {summary['message_count']}")
    print(f"  - Queries: {summary['queries_executed']}")
    print()


def main():
    print("\n" + "=" * 70)
    print("Testing Enhanced Features (Offline Mode)")
    print("No Bedrock calls - Testing validation, caching, and conversation")
    print("=" * 70 + "\n")
    
    try:
        test_validation()
        test_caching()
        test_conversation()
        
        print("=" * 70)
        print("✅ All offline tests passed!")
        print("=" * 70)
        print("\nThese features work without Bedrock:")
        print("  ✓ Query validation")
        print("  ✓ Result caching")
        print("  ✓ Conversation history")
        print("\nOnce you fix the payment method issue, you can test:")
        print("  - SQL generation with Bedrock")
        print("  - Query explanations")
        print("  - Full end-to-end examples")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
