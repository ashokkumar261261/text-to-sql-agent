#!/usr/bin/env python3
"""
Test enhanced agent with Titan model and Knowledge Base.
"""

from src.enhanced_agent import EnhancedTextToSQLAgent

def test_enhanced_agent_with_titan():
    """Test enhanced agent with Titan model."""
    
    print("🧪 Testing Enhanced Agent with Titan + Knowledge Base")
    print("=" * 60)
    
    try:
        # Initialize enhanced agent
        agent = EnhancedTextToSQLAgent(
            session_id="test_titan_session",
            enable_knowledge_base=True
        )
        
        print("✅ Enhanced agent initialized")
        
        # Check KB status
        kb_status = agent.get_knowledge_base_status()
        print(f"📚 KB Status: {kb_status['enabled']}")
        print(f"📚 KB ID: {kb_status.get('knowledge_base_id', 'None')}")
        
        # Test the main query
        query = "show me all customers from texas who ordered electronics"
        print(f"\n🔍 Query: '{query}'")
        
        result = agent.query(
            query,
            execute=False,  # Don't execute, just generate SQL
            use_knowledge_base=True,
            explain=True
        )
        
        print(f"\n📋 Result:")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ SQL Generated: {result['sql_query']}")
            
            if 'knowledge_base_insights' in result:
                insights = result['knowledge_base_insights']
                context_count = len(insights.get('relevant_context', []))
                print(f"📚 KB Context: {context_count} relevant entries found")
                
                if insights.get('relevant_context'):
                    print("📚 Business Context:")
                    for i, context in enumerate(insights['relevant_context'][:2], 1):
                        confidence = int(context['confidence'] * 100)
                        content_preview = context['content'][:80] + "..."
                        print(f"   {i}. {confidence}% - {content_preview}")
            
            if 'explanation' in result:
                print(f"📝 Explanation: {result['explanation'][:150]}...")
            
            if 'validation' in result:
                validation = result['validation']
                status = "✅ Valid" if validation['is_valid'] else "❌ Invalid"
                print(f"🔍 Validation: {status}")
        
        # Test query suggestions
        print(f"\n💡 Testing Query Suggestions:")
        try:
            suggestions = agent.get_query_suggestions("customer analysis")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion}")
        except Exception as e:
            print(f"   ⚠️  Suggestion error: {e}")
        
        return result
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_enhanced_agent_with_titan()