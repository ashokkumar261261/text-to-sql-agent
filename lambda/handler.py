import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import TextToSQLAgent


def lambda_handler(event, context):
    """
    AWS Lambda handler for Text-to-SQL Agent with Athena.
    
    Expected event format:
    {
        "query": "natural language query",
        "execute": true/false,
        "async": true/false,
        "query_execution_id": "optional - for getting async results"
    }
    """
    try:
        # Parse input
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
        
        query = body.get('query')
        execute = body.get('execute', False)
        async_mode = body.get('async', False)
        query_execution_id = body.get('query_execution_id')
        
        # Initialize agent
        agent = TextToSQLAgent()
        
        # Handle different operation modes
        if query_execution_id:
            # Get results from async query
            result = agent.get_query_results(query_execution_id)
        elif query:
            if async_mode:
                # Execute query asynchronously
                result = agent.query_async(query)
            else:
                # Execute query synchronously
                result = agent.query(query, execute=execute)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: query or query_execution_id'
                })
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
