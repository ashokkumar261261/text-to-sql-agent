#!/usr/bin/env python3
"""
Offline demonstration of Knowledge Base features for Text-to-SQL Agent.
This demo shows the knowledge base functionality without requiring AWS setup.
"""

import os
import json
from src.knowledge_base import KnowledgeBaseManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_knowledge_base_documents():
    """Demonstrate knowledge base document creation and content."""
    print("🚀 Knowledge Base Integration Demo (Offline)")
    print("=" * 60)
    
    print("\n📚 Creating Knowledge Base Documents...")
    print("-" * 50)
    
    try:
        kb_manager = KnowledgeBaseManager()
        documents = kb_manager.create_sample_knowledge_base_content()
        
        print(f"✅ Successfully created {len(documents)} knowledge base documents:")
        
        for filename, content in documents.items():
            print(f"\n📄 {filename}")
            print(f"   Size: {len(content)} characters")
            
            # Show key sections
            lines = content.split('\n')
            headers = [line for line in lines if line.startswith('#')]
            if headers:
                print(f"   Sections: {len(headers)} main sections")
                for header in headers[:3]:  # Show first 3 headers
                    print(f"     • {header.strip()}")
            
            # Show sample content
            print(f"   Preview:")
            preview_lines = content.split('\n')[:5]
            for line in preview_lines:
                if line.strip():
                    print(f"     {line[:80]}{'...' if len(line) > 80 else ''}")
            
            if filename == 'common_queries.md':
                # Extract SQL examples
                sql_examples = []
                in_sql_block = False
                for line in lines:
                    if '```sql' in line:
                        in_sql_block = True
                        continue
                    elif '```' in line and in_sql_block:
                        in_sql_block = False
                        continue
                    elif in_sql_block and line.strip():
                        sql_examples.append(line.strip())
                
                if sql_examples:
                    print(f"   SQL Examples found: {len([ex for ex in sql_examples if 'SELECT' in ex.upper()])}")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error creating documents: {str(e)}")
        return None


def demo_business_context_analysis():
    """Demonstrate business context analysis capabilities."""
    print(f"\n🎯 Business Context Analysis Demo")
    print("-" * 50)
    
    # Sample queries and their business context
    sample_queries = [
        {
            'query': 'Show me all customers from California',
            'business_context': [
                'Should filter for active customers by default',
                'Customer data is sensitive - limit personal information',
                'Consider customer tier for premium analysis'
            ],
            'sql_pattern': 'SELECT customer_id, name, city, state FROM customers WHERE state = ? AND status = ?'
        },
        {
            'query': 'Calculate total revenue by category',
            'business_context': [
                'Revenue calculations should exclude cancelled orders',
                'Use delivered orders for accurate revenue',
                'Consider date ranges for trending analysis'
            ],
            'sql_pattern': 'SELECT category, SUM(total_amount) FROM orders WHERE status = ? GROUP BY category'
        },
        {
            'query': 'Find premium customers who spent over $1000',
            'business_context': [
                'Premium customers are defined as >$1000 annual spend',
                'Filter for active customers unless historical analysis',
                'Consider customer tier classification'
            ],
            'sql_pattern': 'SELECT c.*, SUM(o.total_amount) FROM customers c JOIN orders o WHERE ... HAVING SUM(...) > 1000'
        }
    ]
    
    for i, example in enumerate(sample_queries, 1):
        print(f"\n{i}. Query: '{example['query']}'")
        print(f"   Business Context:")
        for context in example['business_context']:
            print(f"     • {context}")
        print(f"   SQL Pattern: {example['sql_pattern']}")
        
        # Simulate intent analysis
        query_lower = example['query'].lower()
        if 'show' in query_lower or 'list' in query_lower:
            intent = 'retrieval'
        elif 'calculate' in query_lower or 'total' in query_lower:
            intent = 'aggregation'
        elif 'find' in query_lower:
            intent = 'search'
        else:
            intent = 'analysis'
        
        complexity = 'high' if 'premium' in query_lower or 'category' in query_lower else 'medium'
        
        print(f"   Intent: {intent} | Complexity: {complexity}")


def demo_query_validation_rules():
    """Demonstrate business rule validation."""
    print(f"\n📋 Business Rule Validation Demo")
    print("-" * 50)
    
    validation_examples = [
        {
            'sql': 'SELECT * FROM customers WHERE state = "CA"',
            'issues': ['Missing active customer filter', 'SELECT * exposes sensitive data'],
            'suggestions': ['Add WHERE status = "active"', 'Limit columns to necessary fields']
        },
        {
            'sql': 'SELECT SUM(total_amount) FROM orders',
            'issues': ['Includes cancelled orders in revenue calculation'],
            'suggestions': ['Add WHERE status != "cancelled"', 'Consider date range filter']
        },
        {
            'sql': 'SELECT customer_id, name FROM customers WHERE status = "active" LIMIT 100',
            'issues': [],
            'suggestions': ['Query follows business rules', 'Good use of LIMIT for performance']
        }
    ]
    
    for i, example in enumerate(validation_examples, 1):
        print(f"\n{i}. SQL: {example['sql']}")
        
        if example['issues']:
            print(f"   ⚠️  Issues Found:")
            for issue in example['issues']:
                print(f"     • {issue}")
        else:
            print(f"   ✅ No issues found")
        
        print(f"   💡 Suggestions:")
        for suggestion in example['suggestions']:
            print(f"     • {suggestion}")


def demo_intelligent_suggestions():
    """Demonstrate intelligent query suggestions."""
    print(f"\n💡 Intelligent Query Suggestions Demo")
    print("-" * 50)
    
    suggestion_categories = {
        'Customer Analysis': [
            'Show me all premium customers from Texas',
            'List customers who haven\'t ordered in 6 months',
            'Find customers with highest lifetime value',
            'Show customer distribution by state'
        ],
        'Sales Analysis': [
            'Calculate monthly revenue trends',
            'Show top 10 products by sales volume',
            'Compare revenue by category this quarter',
            'Find best performing sales regions'
        ],
        'Order Analysis': [
            'Show orders with status "pending" older than 7 days',
            'Calculate average order value by customer tier',
            'List orders above $500 from last month',
            'Find orders with delivery delays'
        ]
    }
    
    for category, suggestions in suggestion_categories.items():
        print(f"\n📊 {category}:")
        for j, suggestion in enumerate(suggestions, 1):
            print(f"   {j}. {suggestion}")


def demo_schema_intelligence():
    """Demonstrate schema relationship intelligence."""
    print(f"\n🔍 Schema Relationship Intelligence Demo")
    print("-" * 50)
    
    schema_insights = {
        'customers': {
            'primary_key': 'customer_id',
            'important_fields': ['name', 'email', 'state', 'status', 'tier'],
            'relationships': ['orders (one-to-many)'],
            'business_rules': ['Filter by status="active" by default', 'Mask PII in reports']
        },
        'orders': {
            'primary_key': 'order_id',
            'important_fields': ['customer_id', 'product_id', 'total_amount', 'status', 'order_date'],
            'relationships': ['customers (many-to-one)', 'products (many-to-one)'],
            'business_rules': ['Exclude cancelled orders from revenue', 'Use order_date for trends']
        },
        'products': {
            'primary_key': 'product_id',
            'important_fields': ['product_name', 'category', 'price'],
            'relationships': ['orders (one-to-many)'],
            'business_rules': ['Group by category for analysis', 'Consider price ranges']
        }
    }
    
    for table, info in schema_insights.items():
        print(f"\n📋 Table: {table}")
        print(f"   Primary Key: {info['primary_key']}")
        print(f"   Key Fields: {', '.join(info['important_fields'])}")
        print(f"   Relationships: {', '.join(info['relationships'])}")
        print(f"   Business Rules:")
        for rule in info['business_rules']:
            print(f"     • {rule}")


def main():
    """Main demonstration function."""
    
    # Create knowledge base documents
    documents = demo_knowledge_base_documents()
    
    if not documents:
        print("❌ Failed to create knowledge base documents")
        return 1
    
    # Demonstrate various capabilities
    demo_business_context_analysis()
    demo_query_validation_rules()
    demo_intelligent_suggestions()
    demo_schema_intelligence()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("🎉 Knowledge Base Integration Demo Complete!")
    print("=" * 60)
    
    print(f"\n📊 What you've seen:")
    print(f"✅ Knowledge base document creation ({len(documents)} documents)")
    print(f"✅ Business context analysis and intent recognition")
    print(f"✅ Business rule validation and compliance checking")
    print(f"✅ Intelligent query suggestions by category")
    print(f"✅ Schema relationship intelligence")
    
    print(f"\n🚀 Next Steps to Enable Full Integration:")
    print(f"1. Install AWS CLI: https://aws.amazon.com/cli/")
    print(f"2. Configure AWS credentials: aws configure")
    print(f"3. Run setup: python setup_knowledge_base.py --bucket-name your-kb-bucket")
    print(f"4. Create Bedrock Knowledge Base in AWS Console")
    print(f"5. Update .env with BEDROCK_KNOWLEDGE_BASE_ID")
    print(f"6. Test with: python test_knowledge_base.py")
    print(f"7. Launch enhanced UI: streamlit run web_ui_enhanced.py")
    
    print(f"\n💡 Key Benefits:")
    print(f"• 🧠 Domain-aware SQL generation with business context")
    print(f"• 📋 Automated compliance with business rules")
    print(f"• 🎯 Intelligent query suggestions and patterns")
    print(f"• 🔍 Enhanced validation and error prevention")
    print(f"• 💬 Context-aware conversation and follow-ups")
    
    return 0


if __name__ == "__main__":
    exit(main())