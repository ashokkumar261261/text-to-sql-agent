#!/usr/bin/env python3
"""
Update Lambda function to work with embedded schema instead of Knowledge Base
"""

import boto3
import json

def update_lambda_function():
    """Update the Lambda function with embedded schema"""
    
    # Read the current lambda function
    with open('lambda_function.py', 'r') as f:
        lambda_code = f.read()
    
    # Add the embedded schema function
    embedded_schema_function = '''
def get_embedded_schema_context():
    """Provide embedded schema context when Knowledge Base is not available"""
    
    schema_context = """
    DATABASE SCHEMA (VERIFIED):
    - Database: text_to_sql_demo
    - customers: customer_id (bigint), name (string), email (string), city (string), state (string), signup_date (date)
    - orders: order_id (bigint), customer_id (bigint), product_name (string), category (string), quantity (int), price (decimal), total_amount (decimal), order_date (date)
    
    WORKING QUERY PATTERNS:
    
    Top customers by revenue:
    SELECT c.name, c.email, c.city, SUM(o.total_amount) as total_revenue
    FROM text_to_sql_demo.customers c
    JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.email, c.city
    ORDER BY total_revenue DESC
    LIMIT 5;
    
    Sales by category:
    SELECT category, COUNT(order_id) as total_orders, SUM(total_amount) as total_revenue
    FROM text_to_sql_demo.orders
    GROUP BY category
    ORDER BY total_revenue DESC;
    
    CRITICAL RULES:
    1. NEVER use HAVING with column aliases
    2. NEVER use CASE statements in HAVING clauses  
    3. Use signup_date for customer dates (NOT registration_date)
    4. Keep queries simple with basic aggregations only
    5. Always use LIMIT for large result sets
    """
    
    return {
        'context': schema_context,
        'used': False,
        'explanation': "Using embedded schema (Knowledge Base disabled)",
        'insights': ["Simple patterns only", "No HAVING clauses", "Verified column names"]
    }

def generate_enhanced_sql_with_bedrock(bedrock_runtime, query, kb_context):
    """Generate SQL using Bedrock with embedded schema context"""
    
    schema_info = kb_context.get('context', '')
    
    prompt = f"""You are a SQL expert. Generate a SQL query for the following request using the provided database schema.

DATABASE SCHEMA:
{schema_info}

USER REQUEST: {query}

CRITICAL REQUIREMENTS:
1. NEVER use HAVING clauses with column aliases (Athena doesn't support this)
2. NEVER use CASE statements in HAVING clauses
3. Use simple aggregations only (SUM, COUNT, AVG)
4. Always include LIMIT for large result sets
5. Use signup_date for customer dates (NOT registration_date)
6. Keep queries simple and working

Generate ONLY the SQL query, no explanations:"""

    try:
        response = bedrock_runtime.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=json.dumps({
                'inputText': prompt,
                'textGenerationConfig': {
                    'maxTokenCount': 500,
                    'temperature': 0.1,
                    'topP': 0.9
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        sql_query = response_body['results'][0]['outputText'].strip()
        
        # Clean up the response
        if sql_query.startswith('```sql'):
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        return sql_query
        
    except Exception as e:
        print(f"Bedrock SQL generation failed: {str(e)}")
        # Return a simple fallback query
        return f"SELECT * FROM text_to_sql_demo.customers LIMIT 5; -- Error: {str(e)}"

'''
    
    # Add the functions to the lambda code if they don't exist
    if 'def get_embedded_schema_context' not in lambda_code:
        lambda_code += embedded_schema_function
    
    # Replace the kb_context call with embedded schema
    if 'kb_context = get_knowledge_base_context(bedrock_agent, query)' in lambda_code:
        lambda_code = lambda_code.replace(
            'kb_context = get_knowledge_base_context(bedrock_agent, query)',
            'kb_context = get_embedded_schema_context()'
        )
    
    # Write the updated lambda function
    with open('lambda_function_updated.py', 'w') as f:
        f.write(lambda_code)
    
    print("✅ Lambda function updated with embedded schema")
    print("📁 Updated file: lambda_function_updated.py")
    print("\nNext steps:")
    print("1. Review the updated file")
    print("2. Replace lambda_function.py with lambda_function_updated.py")
    print("3. Deploy to AWS Lambda")
    print("4. Test the query: 'Show me top 5 customers by revenue'")

if __name__ == "__main__":
    update_lambda_function()