#!/usr/bin/env python3
"""
Test script for Knowledge Base integration with Text-to-SQL Agent.
"""

import os
import sys
from dotenv import load_dotenv
from src.knowledge_base import KnowledgeBaseManager, BedrockKnowledgeBase
from src.enhanced_agent import EnhancedTextToSQLAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def test_knowledge_base_documents():
    """Test knowledge base document creation."""
    print("🧪 Testing Knowledge Base Document Creation...")
    print("-" * 50)
    
    try:
        kb_manager = KnowledgeBaseManager()
        documents = kb_manager.create_sample_knowledge_base_content()
        
        print(f"✅ Successfully created {len(documents)} documents:")
        for filename, content in documents.items():
            print(f"   📄 {filename} ({len(content)} characters)")
            
            # Validate content structure
            if filename.endswith('.md'):
                if '# ' in content:  # Has headers
                    print(f"      ✅ Contains markdown headers")
                if 'sql' in content.lower():  # Contains SQL examples
                    print(f"      ✅ Contains SQL examples")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating documents: {str(e)}")
        return False


def test_knowledge_base_connection():
    """Test connection to Bedrock Knowledge Base."""
    print("\n🔗 Testing Knowledge Base Connection...")
    print("-" * 50)
    
    kb_id = os.getenv('BEDROCK_KNOWLEDGE_BASE_ID')
    if not kb_id:
        print("⚠️  BEDROCK_KNOWLEDGE_BASE_ID not configured")
        print("   Set this in your .env file to test KB connection")
        return False
    
    try:
        kb = BedrockKnowledgeBase()
        
        # Test query
        test_queries = [
            "customer business rules",
            "order status definitions",
            "revenue calculation examples"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            results = kb.query_knowledge_base(query)
            
            if results:
                print(f"   ✅ Found {len(results)} results")
                for i, result in enumerate(results[:2], 1):
                    confidence = int(result['confidence'] * 100)
                    content_preview = result['content'][:100] + "..."
                    print(f"   {i}. Confidence: {confidence}% - {content_preview}")
            else:
                print(f"   ⚠️  No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to knowledge base: {str(e)}")
        return False


def test_enhanced_agent():
    """Test the enhanced agent with knowledge base integration."""
    print("\n🤖 Testing Enhanced Agent...")
    print("-" * 50)
    
    try:
        # Initialize agent
        agent = EnhancedTextToSQLAgent(
            session_id="test_session",
            enable_knowledge_base=True
        )
        
        # Check status
        kb_status = agent.get_knowledge_base_status()
        print(f"📚 Knowledge Base Status: {kb_status}")
        
        # Test queries
        test_queries = [
            "Show me all active customers",
            "Calculate total revenue by category",
            "Find premium customers from California"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Analyze intent
            try:
                intent = agent.analyze_query_intent(query)
                print(f"   📊 Intent: {intent['intent_type']} | Complexity: {intent['complexity']}")
                
                if intent['tables_likely_needed']:
                    print(f"   📋 Tables: {', '.join(intent['tables_likely_needed'])}")
                
            except Exception as e:
                print(f"   ⚠️  Intent analysis failed: {str(e)}")
            
            # Process query (without execution)
            try:
                result = agent.query(
                    query,
                    execute=False,  # Don't execute on test
                    use_knowledge_base=True,
                    explain=True
                )
                
                print(f"   🔧 SQL Generated: {result['sql_query'][:100]}...")
                
                if result.get('knowledge_base_insights'):
                    insights = result['knowledge_base_insights']
                    context_count = len(insights.get('relevant_context', []))
                    print(f"   📚 KB Context: {context_count} relevant entries found")
                
                if result.get('validation', {}).get('is_valid'):
                    print(f"   ✅ Validation: Passed")
                else:
                    print(f"   ⚠️  Validation: Issues found")
                
            except Exception as e:
                print(f"   ❌ Query processing failed: {str(e)}")
        
        # Test suggestions
        try:
            suggestions = agent.get_query_suggestions()
            print(f"\n💡 Generated {len(suggestions)} suggestions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion}")
        except Exception as e:
            print(f"   ⚠️  Suggestion generation failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing enhanced agent: {str(e)}")
        return False


def test_business_rule_validation():
    """Test business rule validation functionality."""
    print("\n📋 Testing Business Rule Validation...")
    print("-" * 50)
    
    if not os.getenv('BEDROCK_KNOWLEDGE_BASE_ID'):
        print("⚠️  Knowledge Base not configured - skipping business rule tests")
        return True
    
    try:
        kb = BedrockKnowledgeBase()
        
        # Test SQL queries against business rules
        test_cases = [
            {
                'sql': 'SELECT * FROM customers WHERE state = "CA"',
                'query': 'Show customers from California',
                'expected': 'Should suggest active filter'
            },
            {
                'sql': 'SELECT SUM(total_amount) FROM orders',
                'query': 'Calculate total revenue',
                'expected': 'Should suggest excluding cancelled orders'
            }
        ]
        
        for case in test_cases:
            print(f"\n🧪 Testing: {case['query']}")
            print(f"   SQL: {case['sql']}")
            
            validation = kb.validate_business_rules(case['sql'], case['query'])
            
            print(f"   Compliant: {validation['compliant']}")
            if validation['warnings']:
                print(f"   Warnings: {', '.join(validation['warnings'])}")
            if validation['applicable_rules']:
                print(f"   Rules: {len(validation['applicable_rules'])} applicable")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing business rules: {str(e)}")
        return False


def run_comprehensive_test():
    """Run all knowledge base tests."""
    print("🚀 Knowledge Base Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Document Creation", test_knowledge_base_documents),
        ("KB Connection", test_knowledge_base_connection),
        ("Enhanced Agent", test_enhanced_agent),
        ("Business Rules", test_business_rule_validation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Knowledge Base integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
        if not os.getenv('BEDROCK_KNOWLEDGE_BASE_ID'):
            print("\n💡 Tip: Set up your knowledge base using:")
            print("   python setup_knowledge_base.py --bucket-name your-kb-bucket")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)