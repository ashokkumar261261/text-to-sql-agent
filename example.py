#!/usr/bin/env python3
"""
Example usage of the Text-to-SQL Agent with Athena and Glue Catalog
"""

from src.agent import TextToSQLAgent
from src.schema import SchemaManager


def example_schema_inspection():
    """Example: Inspect Glue Catalog schema"""
    print("="*60)
    print("Example 1: Inspecting Glue Catalog Schema")
    print("="*60 + "\n")
    
    schema_manager = SchemaManager()
    
    # List all tables
    tables = schema_manager.list_tables()
    print(f"Available tables: {', '.join(tables)}\n")
    
    # Get detailed schema
    schema_context = schema_manager.get_schema_context()
    print("Schema Context:")
    print(schema_context)
    print("\n")


def example_generate_sql():
    """Example: Generate SQL without execution"""
    print("="*60)
    print("Example 2: Generate SQL Queries")
    print("="*60 + "\n")
    
    agent = TextToSQLAgent()
    
    queries = [
        "Show me all records from the sales table",
        "What are the top 10 products by revenue?",
        "Count the number of transactions per day in the last month",
        "Find customers who made purchases over $1000"
    ]
    
    for query in queries:
        print(f"Natural Language: {query}")
        
        result = agent.query(query, execute=False)
        
        if 'error' in result:
            print(f"Error: {result['error']}\n")
        else:
            print(f"Generated SQL:\n{result['sql_query']}")
            print(f"Database: {result['database']}\n")
        
        print("-" * 60 + "\n")


def example_execute_query():
    """Example: Generate and execute SQL query"""
    print("="*60)
    print("Example 3: Execute Query on Athena")
    print("="*60 + "\n")
    
    agent = TextToSQLAgent()
    
    query = "Select * from my_table limit 5"
    print(f"Natural Language: {query}\n")
    
    # Execute the query
    result = agent.query(query, execute=True)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Generated SQL:\n{result['sql_query']}\n")
        print(f"Results ({result['row_count']} rows):")
        for i, row in enumerate(result['results'][:5], 1):
            print(f"  Row {i}: {row}")
    
    print("\n")


def example_async_query():
    """Example: Execute query asynchronously"""
    print("="*60)
    print("Example 4: Async Query Execution")
    print("="*60 + "\n")
    
    agent = TextToSQLAgent()
    
    query = "Count all records in my_table"
    print(f"Natural Language: {query}\n")
    
    # Start async query
    result = agent.query_async(query)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Generated SQL:\n{result['sql_query']}")
        print(f"Query Execution ID: {result['query_execution_id']}\n")
        
        # Get results
        print("Fetching results...")
        results = agent.get_query_results(result['query_execution_id'])
        
        if 'error' in results:
            print(f"Error: {results['error']}")
        else:
            print(f"Results ({results['row_count']} rows):")
            for i, row in enumerate(results['results'][:5], 1):
                print(f"  Row {i}: {row}")
    
    print("\n")


def main():
    print("\n" + "="*60)
    print("Text-to-SQL Agent with AWS Athena & Glue Catalog")
    print("="*60 + "\n")
    
    try:
        # Run examples
        example_schema_inspection()
        example_generate_sql()
        
        # Uncomment to run execution examples (requires valid AWS setup)
        # example_execute_query()
        # example_async_query()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Configured AWS credentials")
        print("2. Set up .env file with GLUE_DATABASE and ATHENA_OUTPUT_LOCATION")
        print("3. Have access to Bedrock and Athena services")


if __name__ == "__main__":
    main()
