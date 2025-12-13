#!/usr/bin/env python3
"""
Example usage of the Enhanced Text-to-SQL Agent with Bedrock Knowledge Base integration.
"""

import os
import json
from dotenv import load_dotenv
from src.enhanced_agent import EnhancedTextToSQLAgent
from src.knowledge_base import KnowledgeBaseManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def demonstrate_knowledge_base_features():
    """Demonstrate the enhanced features with knowledge base integration."""
    
    print("🚀 Enhanced Text-to-SQL Agent with Knowledge Base Demo")
    print("=" * 60)
    
    # Initialize the enhanced agent
    try:
        agent = EnhancedTextToSQLAgent(
            session_id="demo_kb_session",
            enable_cache=True,
            enable_knowledge_base=True
        )
        print("✅ Enhanced agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return
    
    # Check knowledge base status
    kb_status = agent.get_knowledge_base_status()
    print(f"\n📚 Knowledge Base Status: {kb_status}")
    
    # Example queries to demonstrate enhanced capabilities
    example_queries = [
        "Show me all active customers from California",
        "What are the top 5 products by revenue this month?",
        "Find customers who spent more than $1000 on Electronics",
        "Calculate total revenue by category for delivered orders",
        "Show me monthly sales trends for the last 6 months"
    ]
    
    print("\n🔍 Testing Enhanced Query Processing...")
    print("-" * 50)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Analyze query intent first
        intent_analysis = agent.analyze_query_intent(query)
        print(f"   Intent: {intent_analysis['intent_type']} (Complexity: {intent_analysis['complexity']})")
        
        if intent_analysis['tables_likely_needed']:
            print(f"   Tables needed: {', '.join(intent_analysis['tables_likely_needed'])}")
        
        # Process the query
        try:
            result = agent.query(
                query,
                execute=False,  # Set to True if you have actual data
                explain=True,
                use_knowledge_base=True
            )
            
            print(f"   SQL: {result['sql_query']}")
            
            # Show knowledge base insights if available
            if 'knowledge_base_insights' in result:
                insights = result['knowledge_base_insights']
                if insights['relevant_context']:
                    print(f"   KB Context: Found {len(insights['relevant_context'])} relevant entries")
                if insights['business_rules']:
                    print(f"   Business Rules: {len(insights['business_rules'])} applicable")
            
            # Show validation results
            if 'validation' in result:
                validation = result['validation']
                status = "✅ Valid" if validation['is_valid'] else "❌ Invalid"
                print(f"   Validation: {status}")
                
                if validation.get('warnings'):
                    print(f"   Warnings: {', '.join(validation['warnings'])}")
            
            # Show explanation
            if 'explanation' in result:
                print(f"   Explanation: {result['explanation'][:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Demonstrate query suggestions
    print(f"\n💡 Intelligent Query Suggestions:")
    print("-" * 40)
    suggestions = agent.get_query_suggestions()
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"{i}. {suggestion}")
    
    # Demonstrate conversation context
    print(f"\n💬 Conversation Summary:")
    print("-" * 30)
    conversation_summary = agent.get_conversation_summary()
    print(f"Total queries: {conversation_summary.get('total_queries', 0)}")
    print(f"Session duration: {conversation_summary.get('session_duration', 'N/A')}")
    
    # Show cache statistics
    cache_stats = agent.get_cache_stats()
    if cache_stats.get('enabled'):
        print(f"\n⚡ Cache Statistics:")
        print(f"   Hits: {cache_stats.get('hits', 0)}")
        print(f"   Misses: {cache_stats.get('misses', 0)}")
        print(f"   Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")


def test_knowledge_base_setup():
    """Test knowledge base document creation and upload."""
    
    print("\n📝 Testing Knowledge Base Document Creation...")
    print("-" * 50)
    
    try:
        kb_manager = KnowledgeBaseManager()
        documents = kb_manager.create_sample_knowledge_base_content()
        
        print(f"✅ Created {len(documents)} knowledge base documents:")
        for filename in documents.keys():
            print(f"   - {filename}")
        
        # Show sample content
        print(f"\n📄 Sample Content from business_glossary.md:")
        print("-" * 40)
        sample_content = documents['business_glossary.md'][:300] + "..."
        print(sample_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create knowledge base documents: {str(e)}")
        return False


def interactive_demo():
    """Interactive demo allowing user to input queries."""
    
    print("\n🎯 Interactive Knowledge Base Demo")
    print("=" * 40)
    print("Enter natural language queries (type 'quit' to exit)")
    
    try:
        agent = EnhancedTextToSQLAgent(
            session_id="interactive_session",
            enable_knowledge_base=True
        )
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        return
    
    while True:
        try:
            query = input("\n🔍 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            # Analyze intent
            intent = agent.analyze_query_intent(query)
            print(f"📊 Intent: {intent['intent_type']} | Complexity: {intent['complexity']}")
            
            # Process query
            result = agent.query(
                query,
                execute=False,
                explain=True,
                use_knowledge_base=True
            )
            
            print(f"🔧 SQL: {result['sql_query']}")
            
            if 'explanation' in result:
                print(f"💭 Explanation: {result['explanation']}")
            
            # Show knowledge base insights
            if result.get('knowledge_base_insights', {}).get('relevant_context'):
                print("📚 Knowledge Base provided relevant business context")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n👋 Thanks for trying the Enhanced Text-to-SQL Agent!")


def main():
    """Main demo function."""
    
    # Test knowledge base document creation
    if not test_knowledge_base_setup():
        return 1
    
    # Demonstrate enhanced features
    demonstrate_knowledge_base_features()
    
    # Ask if user wants interactive demo
    print(f"\n" + "=" * 60)
    response = input("Would you like to try the interactive demo? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        interactive_demo()
    
    print(f"\n🎉 Demo completed!")
    print(f"\nTo set up your own knowledge base:")
    print(f"1. Run: python setup_knowledge_base.py --bucket-name your-kb-bucket")
    print(f"2. Follow the setup instructions")
    print(f"3. Update your .env file with BEDROCK_KNOWLEDGE_BASE_ID")
    
    return 0


if __name__ == "__main__":
    exit(main())