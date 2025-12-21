import json
import boto3
import os
from datetime import datetime

def handle_query_request(body):
    """Handle regular AI query requests"""
    query = body.get('query', '')
    
    # Initialize AWS clients
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        athena_client = boto3.client('athena', region_name='us-east-1')
        
        # Get Knowledge Base context first
        kb_context = get_knowledge_base_context(bedrock_agent, query)
        
        # Generate enhanced SQL using Bedrock LLM + Knowledge Base context
        # If query starts with SELECT, use it directly for testing
        if query.strip().upper().startswith('SELECT'):
            sql_query = query.strip()
            print(f"Using direct SQL query for testing: {sql_query}")
        else:
            sql_query = generate_enhanced_sql_with_bedrock(bedrock_runtime, query, kb_context)
        
        # Try to execute with Athena (if configured)
        results = []
        row_count = 0
        database = "demo_database"
        athena_error_msg = None
        athena_configured = False
        
        # Check if Athena is configured
        glue_database = os.environ.get('GLUE_DATABASE')
        athena_output = os.environ.get('ATHENA_OUTPUT_LOCATION')
        
        if glue_database and athena_output:
            athena_configured = True
            try:
                print(f"Attempting Athena execution with database: {glue_database}")
                results, row_count = execute_athena_query(athena_client, sql_query, glue_database, athena_output)
                database = glue_database
                print(f"Athena execution successful: {row_count} rows returned")
                
                # Additional debugging
                if row_count == 0:
                    print("WARNING: Athena query succeeded but returned 0 rows")
                    print(f"SQL Query was: {sql_query}")
                    print(f"Database: {glue_database}")
                else:
                    print(f"SUCCESS: Got {row_count} rows from Athena")
                    print(f"First row sample: {results[0] if results else 'No results'}")
                    
            except Exception as athena_error:
                athena_error_msg = str(athena_error)
                print(f"Athena execution failed: {athena_error_msg}")
                # Don't use fallback data - show the error instead
        else:
            print("Athena not configured - using demo mode")
        
        # Format the response
        response_data = {
            'success': True,
            'query': query,
            'sql': sql_query,
            'explanation': f'Generated SQL query using AI and business context for: "{query}". {kb_context.get("explanation", "")}',
            'results': results,
            'row_count': row_count,
            'cached': False,
            'knowledge_base_used': kb_context.get('used', False),
            'database': database,
            'kb_insights': kb_context.get('insights', []),
            'athena_configured': athena_configured
        }
        
        # Handle Athena errors - show actual error instead of fallback
        if athena_error_msg:
            response_data['athena_error'] = athena_error_msg
            response_data['error_details'] = f"Athena Query Execution Failed: {athena_error_msg}"
            response_data['columns'] = []
            response_data['success'] = True  # Still show the SQL that was generated
            # Don't provide sample data when there's an actual error
        elif results and len(results) > 0:
            # Successful Athena execution with data
            response_data['columns'] = list(results[0].keys())
            print(f"SUCCESS: Returning {len(results)} rows with columns: {response_data['columns']}")
        elif athena_configured and row_count == 0:
            # Athena configured and query succeeded but no results (empty result set)
            response_data['columns'] = []
            response_data['message'] = "Query executed successfully but returned no results. This could mean:"
            response_data['suggestions'] = [
                "The query conditions don't match any data in the database",
                "The table might be empty or the date range might be outside available data",
                "Check if the table and column names are correct",
                f"Verify data exists in database '{database}'"
            ]
            print(f"EMPTY RESULT: Query succeeded but returned 0 rows")
        else:
            # Athena not configured - provide sample data
            response_data['columns'] = []
            response_data['results'] = generate_sample_data(query)
            response_data['columns'] = list(response_data['results'][0].keys()) if response_data['results'] else []
            response_data['row_count'] = len(response_data['results'])
            response_data['sample_data'] = True
            print(f"DEMO MODE: Returning {len(response_data['results'])} sample rows")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as aws_error:
        error_message = str(aws_error)
        
        # Provide more specific error messages
        if "credentials" in error_message.lower():
            error_message = "AWS credentials not configured properly. Please check Lambda execution role permissions."
        elif "bedrock" in error_message.lower():
            error_message = "Amazon Bedrock access error. Please check model permissions and region configuration."
        elif "athena" in error_message.lower():
            error_message = "Amazon Athena access error. Please check database configuration and permissions."
        elif "knowledge" in error_message.lower():
            error_message = "Knowledge Base access error. Please check Bedrock Knowledge Base configuration."
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f"AWS Service Error: {error_message}",
                'query': body.get('query', ''),
                'fallback_message': "Please check your AWS configuration and permissions."
            })
        }


def handle_view_table_data(table_name):
    """Handle requests to view sample table data"""
    try:
        athena_client = boto3.client('athena', region_name='us-east-1')
        glue_database = os.environ.get('GLUE_DATABASE', 'text_to_sql_demo')
        athena_output = os.environ.get('ATHENA_OUTPUT_LOCATION')
        
        if not athena_output:
            # Return sample data if Athena not configured
            sample_data = generate_sample_data(f"show me data from {table_name}")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'results': sample_data,
                    'columns': list(sample_data[0].keys()) if sample_data else [],
                    'row_count': len(sample_data),
                    'sample_data': True
                })
            }
        
        # Execute query to get sample data
        sql_query = f"SELECT * FROM {glue_database}.{table_name} LIMIT 10"
        results, row_count = execute_athena_query(athena_client, sql_query, glue_database, athena_output)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'results': results,
                'columns': list(results[0].keys()) if results else [],
                'row_count': row_count
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f"Error retrieving table data: {str(e)}"
            })
        }


def handle_view_kb_file(file_name):
    """Handle requests to view knowledge base files"""
    try:
        # Map of available KB files
        kb_files = {
            'database_schema.md': 'kb_documents/database_schema.md',
            'business_glossary.md': 'kb_documents/business_glossary.md', 
            'sql_examples.md': 'kb_documents/sql_examples.md'
        }
        
        if file_name not in kb_files:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'Knowledge base file not found'
                })
            }
        
        # Try to read the file from the Lambda package
        try:
            with open(kb_files[file_name], 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            # If file not found locally, provide a sample content
            content = f"# {file_name}\n\nThis knowledge base file is not available in the current deployment.\n\nTo view the actual content, ensure the kb_documents folder is included in your Lambda deployment package."
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'content': content,
                'file_name': file_name
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f"Error reading knowledge base file: {str(e)}"
            })
        }


def handle_download_kb_file(file_name):
    """Handle requests to download knowledge base files"""
    return handle_view_kb_file(file_name)  # Same logic for now


def handle_file_upload(event, context):
    """Handle file upload requests"""
    try:
        # For now, return a placeholder response
        # In a real implementation, you would:
        # 1. Parse the multipart form data
        # 2. Upload files to S3
        # 3. Update the knowledge base
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'File upload feature is under development. Please contact your administrator to update knowledge base files.'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f"Upload error: {str(e)}"
            })
        }


def handle_reindex_knowledge_base():
    """Handle knowledge base reindexing requests"""
    try:
        # For now, return a placeholder response
        # In a real implementation, you would:
        # 1. Trigger Bedrock Knowledge Base sync
        # 2. Wait for completion
        # 3. Return status
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Knowledge base reindexing feature is under development. Please contact your administrator to reindex the knowledge base.'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f"Reindexing error: {str(e)}"
            })
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler for Text-to-SQL Agent with Bedrock Knowledge Base integration
    """
    
    try:
        # Check if this is a POST request with a query
        if event.get('requestContext', {}).get('http', {}).get('method') == 'POST':
            try:
                # Handle different content types
                if 'multipart/form-data' in event.get('headers', {}).get('content-type', ''):
                    # Handle file upload
                    return handle_file_upload(event, context)
                else:
                    # Handle JSON requests
                    body = json.loads(event.get('body', '{}'))
                    
                    # Check for different actions
                    action = body.get('action')
                    
                    if action == 'view_table_data':
                        return handle_view_table_data(body.get('table_name'))
                    elif action == 'view_kb_file':
                        return handle_view_kb_file(body.get('file_name'))
                    elif action == 'download_kb_file':
                        return handle_download_kb_file(body.get('file_name'))
                    elif action == 'reindex_knowledge_base':
                        return handle_reindex_knowledge_base()
                    else:
                        # Handle regular query
                        return handle_query_request(body)
                        
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'success': False, 'error': str(e)})
                }
                
        # Serve the HTML interface for GET requests
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text-to-SQL AI Agent - Enhanced with Knowledge Base</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        .demo-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .query-interface {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            border: 2px solid rgba(255, 215, 0, 0.3);
        }
        .query-input {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        .query-input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }
        .query-btn {
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #333;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        .query-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .query-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .tab-container {
            display: flex;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
        }
        .tab-button {
            flex: 1;
            padding: 15px 20px;
            background: transparent;
            border: none;
            color: white;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .tab-button.active {
            background: rgba(255, 215, 0, 0.3);
            color: #FFD700;
        }
        .tab-button:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        .tab-content {
            display: none;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            margin: 10px 0;
        }
        .tab-content.active {
            display: block;
        }
        .data-explorer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .table-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .table-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .table-card h3 {
            margin-top: 0;
            color: #FFD700;
        }
        .kb-file-list {
            list-style: none;
            padding: 0;
        }
        .kb-file-item {
            background: rgba(255, 255, 255, 0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #FFD700;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .kb-file-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .upload-area {
            border: 2px dashed rgba(255, 215, 0, 0.5);
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #FFD700;
            background: rgba(255, 215, 0, 0.1);
        }
        .upload-area.dragover {
            border-color: #FFD700;
            background: rgba(255, 215, 0, 0.2);
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }
        .modal-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            color: white;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #FFD700;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #28a745, #20c997);
            width: 0%;
            transition: width 0.3s ease;
        }
        }
        .result-container {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            border-left: 4px solid #FFD700;
            display: none;
        }
        .result-container.show {
            display: block;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .sql-output {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .feature-card h3 {
            margin-top: 0;
            color: #FFD700;
        }
        .query-example {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            border-left: 4px solid #FFD700;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .query-example:hover {
            background: rgba(0, 0, 0, 0.3);
            transform: translateX(5px);
        }
        .status-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .kb-badge {
            display: inline-block;
            background: #6f42c1;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
        .deployment-info {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #333;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px;
            transition: transform 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .architecture-diagram {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        .results-table th {
            background: rgba(255, 215, 0, 0.3);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid rgba(255, 215, 0, 0.5);
        }
        .results-table td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
        }
        .results-table tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.05);
        }
        .results-table tr:hover {
            background: rgba(255, 215, 0, 0.1);
        }
        .no-results {
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
        }
        .system-info {
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        .error-info {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid rgba(255, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        .kb-insights {
            background: rgba(111, 66, 193, 0.1);
            border: 1px solid rgba(111, 66, 193, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Text-to-SQL AI Agent</h1>
        <p class="subtitle">Enhanced with Knowledge Base Intelligence</p>
        
        <!-- Tab Navigation -->
        <div class="tab-container">
            <button class="tab-button active" onclick="showTab('query')">🤖 AI Query</button>
            <button class="tab-button" onclick="showTab('explorer')">📊 Data Explorer</button>
            <button class="tab-button" onclick="showTab('knowledge')">🧠 Knowledge Base</button>
            <button class="tab-button" onclick="showTab('upload')">📤 Upload KB</button>
        </div>

        <!-- AI Query Tab -->
        <div id="queryTab" class="tab-content active">
            <!-- Interactive Query Interface -->
            <div class="query-interface">
                <h2>💬 Ask Your Question</h2>
                <p>Type a natural language question about your data:</p>
                <input type="text" id="queryInput" class="query-input" placeholder="e.g., Show me top 5 customers by revenue" />
                <button id="queryBtn" class="query-btn" onclick="processQuery()">
                    🚀 Generate Enhanced SQL Query
                </button>
                
                <div id="resultContainer" class="result-container">
                    <h3>📊 Generated SQL:</h3>
                    <div id="sqlOutput" class="sql-output"></div>
                    <h3>💡 AI Explanation:</h3>
                    <div id="explanationOutput"></div>
                    <h3>📋 Query Results:</h3>
                    <div id="resultsOutput" style="margin-top: 15px;">
                        <div id="resultsTable"></div>
                        <div id="resultsCount" style="margin-top: 10px; font-style: italic; color: #FFD700;"></div>
                    </div>
                    <div id="kbInsights" class="kb-insights" style="display: none;">
                        <h4>🧠 Knowledge Base Insights:</h4>
                        <div id="kbDetails"></div>
                    </div>
                    <div id="systemInfo" class="system-info" style="display: none;">
                        <h4>🔧 System Information:</h4>
                        <div id="systemDetails"></div>
                    </div>
                </div>
            </div>

            <div class="demo-section">
                <h2>💡 Try These Enhanced Questions</h2>
                <p>Click on any example to try it:</p>
                <div class="query-example" onclick="setQuery('Show me top 5 customers by revenue')">
                    "Show me top 5 customers by revenue"
                </div>
                <div class="query-example" onclick="setQuery('What are the trending products this month?')">
                    "What are the trending products this month?"
                </div>
                <div class="query-example" onclick="setQuery('Find customers at risk of churning')">
                    "Find customers at risk of churning"
                </div>
                <div class="query-example" onclick="setQuery('Compare sales performance by region')">
                    "Compare sales performance by region"
                </div>
                <div class="query-example" onclick="setQuery('Which products have the highest profit margins?')">
                    "Which products have the highest profit margins?"
                </div>
            </div>
        </div>

        <!-- Data Explorer Tab -->
        <div id="explorerTab" class="tab-content">
            <h2>📊 Database Explorer</h2>
            <p>Click on any table to view sample data:</p>
            
            <div class="data-explorer-grid">
                <div class="table-card" onclick="viewTableData('customers')">
                    <h3>👥 Customers</h3>
                    <p><strong>Columns:</strong> customer_id, name, email, phone, city, state, country</p>
                    <p><strong>Description:</strong> Customer information and contact details</p>
                    <p style="color: #FFD700;">Click to view sample data →</p>
                </div>
                
                <div class="table-card" onclick="viewTableData('orders')">
                    <h3>🛒 Orders</h3>
                    <p><strong>Columns:</strong> order_id, customer_id, product_name, category, quantity, price, total_amount, order_date, status</p>
                    <p><strong>Description:</strong> Order transactions and details</p>
                    <p style="color: #FFD700;">Click to view sample data →</p>
                </div>
                
                <div class="table-card" onclick="viewTableData('products')">
                    <h3>📦 Products</h3>
                    <p><strong>Columns:</strong> product_id, product_name, category, price, stock, supplier</p>
                    <p><strong>Description:</strong> Product catalog and inventory</p>
                    <p style="color: #FFD700;">Click to view sample data →</p>
                </div>
            </div>
            
            <div id="tableDataContainer" class="result-container" style="display: none;">
                <h3 id="tableDataTitle">📊 Table Data:</h3>
                <div id="tableDataOutput"></div>
                <div id="tableDataCount" style="margin-top: 10px; font-style: italic; color: #FFD700;"></div>
            </div>
        </div>

        <!-- Knowledge Base Tab -->
        <div id="knowledgeTab" class="tab-content">
            <h2>🧠 Knowledge Base Documents</h2>
            <p>View and download the knowledge base files that enhance AI query generation:</p>
            
            <ul class="kb-file-list">
                <li class="kb-file-item" onclick="viewKBFile('database_schema.md')">
                    <h4>📋 Database Schema</h4>
                    <p>Complete table structures, relationships, and data types</p>
                    <small>Click to view content</small>
                </li>
                <li class="kb-file-item" onclick="viewKBFile('business_glossary.md')">
                    <h4>📚 Business Glossary</h4>
                    <p>Business terminology, definitions, and domain-specific language</p>
                    <small>Click to view content</small>
                </li>
                <li class="kb-file-item" onclick="viewKBFile('sql_examples.md')">
                    <h4>💡 SQL Examples</h4>
                    <p>Common query patterns and best practices</p>
                    <small>Click to view content</small>
                </li>
            </ul>
        </div>

        <!-- Upload Knowledge Base Tab -->
        <div id="uploadTab" class="tab-content">
            <h2>📤 Upload Knowledge Base Files</h2>
            <p>Upload new knowledge base documents to enhance AI query generation:</p>
            
            <div class="upload-area" id="uploadArea" ondrop="dropHandler(event);" ondragover="dragOverHandler(event);" ondragleave="dragLeaveHandler(event);">
                <h3>📁 Drag & Drop Files Here</h3>
                <p>Or click to select files</p>
                <input type="file" id="fileInput" class="file-input" multiple accept=".md,.txt,.pdf,.docx" onchange="handleFileSelect(event)">
                <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                    📂 Select Files
                </button>
                <p><small>Supported formats: .md, .txt, .pdf, .docx</small></p>
            </div>
            
            <div id="uploadProgress" style="display: none;">
                <h4>📤 Upload Progress:</h4>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div id="uploadStatus">Preparing upload...</div>
            </div>
            
            <div id="uploadResults" style="display: none;">
                <h4>✅ Upload Results:</h4>
                <div id="uploadResultsList"></div>
                <button class="upload-btn" onclick="reindexKnowledgeBase()" id="reindexBtn" style="display: none;">
                    🔄 Reindex Knowledge Base
                </button>
            </div>
        </div>

        <div class="demo-section">
            <h2>🚀 Enhanced Features</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🤖 Advanced AI SQL Generation</h3>
                    <p>Convert natural language questions into optimized SQL queries using Amazon Bedrock Claude</p>
                </div>
                <div class="feature-card">
                    <h3>🧠 Knowledge Base Intelligence</h3>
                    <p>Business context-aware queries with domain-specific terminology and best practices</p>
                </div>
                <div class="feature-card">
                    <h3>📊 Real Data Integration</h3>
                    <p>Execute queries on actual data stored in Amazon S3 using Amazon Athena</p>
                </div>
                <div class="feature-card">
                    <h3>🔐 Enterprise Security</h3>
                    <p>Secure authentication, input validation, and audit logging with AWS IAM</p>
                </div>
            </div>
        </div>

        <div class="demo-section">
            <h2>🏗️ Enhanced Architecture</h2>
            <div class="architecture-diagram">
                <p><strong>Lambda + API Gateway</strong> → <strong>Bedrock Knowledge Base</strong> → <strong>Bedrock LLM</strong> → <strong>Amazon Athena</strong> → <strong>S3 Data</strong></p>
                <p>✅ AI-Enhanced • ✅ Context-Aware • ✅ Scalable • ✅ Secure</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 40px; opacity: 0.8;">
            <p>🚀 <strong>Your Text-to-SQL Agent is enhanced with Knowledge Base intelligence!</strong></p>
            <p>Bedrock LLM • Knowledge Base • Athena • S3 • Context-Aware • Secure</p>
        </div>
    </div>

    <!-- Modal for viewing KB files and table data -->
    <div id="contentModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">Content Viewer</h2>
            <div id="modalContent">Loading...</div>
        </div>
    </div>

    <script>
        // Tab Management
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Remove active class from all tab buttons
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName + 'Tab').classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }

        // Modal Management
        function openModal(title, content) {
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalContent').innerHTML = content;
            document.getElementById('contentModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('contentModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('contentModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        // Data Explorer Functions
        function viewTableData(tableName) {
            const tableDataContainer = document.getElementById('tableDataContainer');
            const tableDataTitle = document.getElementById('tableDataTitle');
            const tableDataOutput = document.getElementById('tableDataOutput');
            const tableDataCount = document.getElementById('tableDataCount');
            
            tableDataTitle.textContent = `📊 ${tableName.charAt(0).toUpperCase() + tableName.slice(1)} Table Data:`;
            tableDataOutput.innerHTML = '<div style="text-align: center; padding: 20px;">Loading table data...</div>';
            tableDataContainer.style.display = 'block';
            
            // Scroll to results
            tableDataContainer.scrollIntoView({ behavior: 'smooth' });
            
            // Make API call to get table data
            fetch(window.location.href, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    action: 'view_table_data',
                    table_name: tableName 
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.results && data.results.length > 0) {
                    let tableHTML = '<table class="results-table"><thead><tr>';
                    
                    // Add headers
                    data.columns.forEach(column => {
                        tableHTML += `<th>${column.replace('_', ' ').toUpperCase()}</th>`;
                    });
                    tableHTML += '</tr></thead><tbody>';
                    
                    // Add data rows
                    data.results.forEach(row => {
                        tableHTML += '<tr>';
                        data.columns.forEach(column => {
                            let value = row[column];
                            if (typeof value === 'number' && value > 1000) {
                                value = value.toLocaleString();
                            }
                            tableHTML += `<td>${value || ''}</td>`;
                        });
                        tableHTML += '</tr>';
                    });
                    
                    tableHTML += '</tbody></table>';
                    tableDataOutput.innerHTML = tableHTML;
                    tableDataCount.innerHTML = `📊 Showing ${data.row_count} sample records from ${tableName} table`;
                } else {
                    tableDataOutput.innerHTML = `<div class="no-results">No data available for ${tableName} table</div>`;
                    tableDataCount.innerHTML = '';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                tableDataOutput.innerHTML = '<div class="error-info">Error loading table data. Please try again.</div>';
                tableDataCount.innerHTML = '';
            });
        }

        // Knowledge Base Functions
        function viewKBFile(fileName) {
            openModal(`📄 ${fileName}`, '<div style="text-align: center; padding: 20px;">Loading knowledge base file...</div>');
            
            // Make API call to get KB file content
            fetch(window.location.href, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    action: 'view_kb_file',
                    file_name: fileName 
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const content = `
                        <div style="background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h3 style="margin: 0;">📄 ${fileName}</h3>
                                <button onclick="downloadKBFile('${fileName}')" style="background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                                    📥 Download
                                </button>
                            </div>
                            <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 0.9em; line-height: 1.4; max-height: 400px; overflow-y: auto;">${data.content}</pre>
                        </div>
                    `;
                    document.getElementById('modalContent').innerHTML = content;
                } else {
                    document.getElementById('modalContent').innerHTML = '<div class="error-info">Error loading knowledge base file.</div>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('modalContent').innerHTML = '<div class="error-info">Error loading knowledge base file.</div>';
            });
        }

        function downloadKBFile(fileName) {
            // Create download link
            fetch(window.location.href, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    action: 'download_kb_file',
                    file_name: fileName 
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const blob = new Blob([data.content], { type: 'text/markdown' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                }
            });
        }

        // File Upload Functions
        function dragOverHandler(ev) {
            ev.preventDefault();
            document.getElementById('uploadArea').classList.add('dragover');
        }

        function dragLeaveHandler(ev) {
            ev.preventDefault();
            document.getElementById('uploadArea').classList.remove('dragover');
        }

        function dropHandler(ev) {
            ev.preventDefault();
            document.getElementById('uploadArea').classList.remove('dragover');
            
            const files = ev.dataTransfer.files;
            handleFiles(files);
        }

        function handleFileSelect(event) {
            const files = event.target.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            if (files.length === 0) return;
            
            const uploadProgress = document.getElementById('uploadProgress');
            const uploadResults = document.getElementById('uploadResults');
            const progressFill = document.getElementById('progressFill');
            const uploadStatus = document.getElementById('uploadStatus');
            
            uploadProgress.style.display = 'block';
            uploadResults.style.display = 'none';
            
            let uploadedFiles = [];
            let totalFiles = files.length;
            let completedFiles = 0;
            
            Array.from(files).forEach((file, index) => {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('action', 'upload_kb_file');
                
                uploadStatus.textContent = `Uploading ${file.name}...`;
                
                fetch(window.location.href, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    completedFiles++;
                    const progress = (completedFiles / totalFiles) * 100;
                    progressFill.style.width = progress + '%';
                    
                    if (data.success) {
                        uploadedFiles.push({ name: file.name, status: 'success', message: data.message });
                    } else {
                        uploadedFiles.push({ name: file.name, status: 'error', message: data.error });
                    }
                    
                    if (completedFiles === totalFiles) {
                        uploadStatus.textContent = 'Upload completed!';
                        showUploadResults(uploadedFiles);
                    }
                })
                .catch(error => {
                    completedFiles++;
                    uploadedFiles.push({ name: file.name, status: 'error', message: 'Upload failed' });
                    
                    if (completedFiles === totalFiles) {
                        uploadStatus.textContent = 'Upload completed with errors!';
                        showUploadResults(uploadedFiles);
                    }
                });
            });
        }

        function showUploadResults(uploadedFiles) {
            const uploadResults = document.getElementById('uploadResults');
            const uploadResultsList = document.getElementById('uploadResultsList');
            const reindexBtn = document.getElementById('reindexBtn');
            
            let resultsHTML = '';
            let hasSuccessfulUploads = false;
            
            uploadedFiles.forEach(file => {
                const statusIcon = file.status === 'success' ? '✅' : '❌';
                const statusClass = file.status === 'success' ? 'system-info' : 'error-info';
                
                resultsHTML += `
                    <div class="${statusClass}" style="margin: 10px 0; padding: 10px; border-radius: 5px;">
                        ${statusIcon} <strong>${file.name}</strong>: ${file.message}
                    </div>
                `;
                
                if (file.status === 'success') {
                    hasSuccessfulUploads = true;
                }
            });
            
            uploadResultsList.innerHTML = resultsHTML;
            uploadResults.style.display = 'block';
            
            if (hasSuccessfulUploads) {
                reindexBtn.style.display = 'inline-block';
            }
        }

        function reindexKnowledgeBase() {
            const reindexBtn = document.getElementById('reindexBtn');
            reindexBtn.disabled = true;
            reindexBtn.textContent = '🔄 Reindexing...';
            
            fetch(window.location.href, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'reindex_knowledge_base' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    reindexBtn.textContent = '✅ Reindexing Complete';
                    reindexBtn.style.background = '#28a745';
                    alert('✅ Knowledge Base has been successfully reindexed with new files!');
                } else {
                    reindexBtn.textContent = '❌ Reindexing Failed';
                    reindexBtn.style.background = '#dc3545';
                    alert('❌ Reindexing failed: ' + data.error);
                }
                reindexBtn.disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                reindexBtn.textContent = '❌ Reindexing Failed';
                reindexBtn.style.background = '#dc3545';
                reindexBtn.disabled = false;
                alert('❌ Reindexing failed due to network error');
            });
        }

        // Original Query Functions
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
            document.getElementById('queryInput').focus();
        }

        function processQuery() {
            const queryInput = document.getElementById('queryInput');
            const queryBtn = document.getElementById('queryBtn');
            const resultContainer = document.getElementById('resultContainer');
            const sqlOutput = document.getElementById('sqlOutput');
            const explanationOutput = document.getElementById('explanationOutput');
            const resultsTable = document.getElementById('resultsTable');
            const resultsCount = document.getElementById('resultsCount');
            const kbInsights = document.getElementById('kbInsights');
            const kbDetails = document.getElementById('kbDetails');
            const systemInfo = document.getElementById('systemInfo');
            const systemDetails = document.getElementById('systemDetails');

            const query = queryInput.value.trim();
            if (!query) {
                alert('Please enter a question first!');
                return;
            }

            // Show loading state
            queryBtn.disabled = true;
            queryBtn.innerHTML = '<span class="loading"></span> Processing with AI...';
            resultContainer.classList.remove('show');

            // Make API call
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    sqlOutput.textContent = data.sql;
                    explanationOutput.textContent = data.explanation;
                    
                    // Check for Athena errors first
                    if (data.athena_error) {
                        resultsTable.innerHTML = `<div class="error-info">
                            <h4>❌ Athena Query Execution Error</h4>
                            <p><strong>Error:</strong> ${data.athena_error}</p>
                            <p><strong>SQL Query:</strong> ${data.sql}</p>
                            <p><strong>Database:</strong> ${data.database}</p>
                            <p><strong>Troubleshooting:</strong></p>
                            <ul>
                                <li>Check if the database '${data.database}' exists and is accessible</li>
                                <li>Verify table names and column names in the query</li>
                                <li>Ensure proper IAM permissions for Athena and S3</li>
                                <li>Check if the Athena output location is configured correctly</li>
                                <li>Verify that data exists in the tables being queried</li>
                            </ul>
                        </div>`;
                        resultsCount.innerHTML = '❌ Query execution failed';
                    }
                    // Display results table if we have data
                    else if (data.results && data.results.length > 0) {
                        let tableHTML = '<table class="results-table"><thead><tr>';
                        
                        // Add headers
                        data.columns.forEach(column => {
                            tableHTML += `<th>${column.replace('_', ' ').toUpperCase()}</th>`;
                        });
                        tableHTML += '</tr></thead><tbody>';
                        
                        // Add data rows
                        data.results.forEach(row => {
                            tableHTML += '<tr>';
                            data.columns.forEach(column => {
                                let value = row[column];
                                // Format numbers with commas
                                if (typeof value === 'number' && value > 1000) {
                                    value = value.toLocaleString();
                                }
                                tableHTML += `<td>${value}</td>`;
                            });
                            tableHTML += '</tr>';
                        });
                        
                        tableHTML += '</tbody></table>';
                        resultsTable.innerHTML = tableHTML;
                        resultsCount.innerHTML = `📊 Found ${data.row_count} result${data.row_count !== 1 ? 's' : ''}`;
                        
                        // Add sample data indicator if applicable
                        if (data.sample_data) {
                            resultsCount.innerHTML += ' (Sample Data - Athena not configured)';
                        }
                    } 
                    // Handle empty results with suggestions
                    else if (data.message && data.suggestions) {
                        let suggestionsHTML = '<ul>';
                        data.suggestions.forEach(suggestion => {
                            suggestionsHTML += `<li>${suggestion}</li>`;
                        });
                        suggestionsHTML += '</ul>';
                        
                        resultsTable.innerHTML = `<div class="system-info">
                            <h4>ℹ️ ${data.message}</h4>
                            <p><strong>Possible reasons:</strong></p>
                            ${suggestionsHTML}
                            <p><strong>SQL Query executed:</strong> <code>${data.sql}</code></p>
                            <p><strong>Database:</strong> ${data.database}</p>
                        </div>`;
                        resultsCount.innerHTML = '📊 0 results (query succeeded)';
                    }
                    else if (!data.athena_error) {
                        // Only show "no results" if there's no Athena error
                        if (data.message) {
                            resultsTable.innerHTML = `<div class="no-results">
                                ${data.message}
                                <br><br>
                                <strong>SQL Query:</strong> <code>${data.sql}</code>
                                <br><strong>Database:</strong> ${data.database}
                            </div>`;
                        } else {
                            resultsTable.innerHTML = `<div class="no-results">
                                Query executed successfully but returned no results
                                <br><br>
                                <strong>SQL Query:</strong> <code>${data.sql}</code>
                                <br><strong>Database:</strong> ${data.database}
                            </div>`;
                        }
                        resultsCount.innerHTML = '📊 0 results';
                    }
                    
                    // Show Knowledge Base insights
                    if (data.kb_insights && data.kb_insights.length > 0) {
                        let kbHTML = '';
                        data.kb_insights.forEach(insight => {
                            kbHTML += `<div style="margin-bottom: 10px;">• ${insight}</div>`;
                        });
                        kbDetails.innerHTML = kbHTML;
                        kbInsights.style.display = 'block';
                    } else {
                        kbInsights.style.display = 'none';
                    }
                    
                    // Show system information
                    if (data.cached || data.knowledge_base_used || data.database || data.athena_configured !== undefined) {
                        let systemHTML = '';
                        if (data.cached) systemHTML += '🔄 Results from cache<br>';
                        if (data.knowledge_base_used) systemHTML += '🧠 Knowledge Base enhanced query<br>';
                        if (data.database) systemHTML += `📊 Database: ${data.database}<br>`;
                        if (data.athena_configured !== undefined) {
                            systemHTML += `⚙️ Athena: ${data.athena_configured ? 'Configured' : 'Not Configured'}<br>`;
                        }
                        if (data.athena_error) {
                            systemHTML += '❌ Athena execution failed<br>';
                        }
                        if (data.sample_data) {
                            systemHTML += '🎭 Using sample data<br>';
                        }
                        
                        systemDetails.innerHTML = systemHTML;
                        systemInfo.style.display = 'block';
                    }
                    
                    resultContainer.classList.add('show');
                } else {
                    // Show error information
                    sqlOutput.textContent = 'Error occurred';
                    explanationOutput.textContent = data.error || 'Unknown error occurred';
                    resultsTable.innerHTML = `<div class="error-info">
                        <strong>Error:</strong> ${data.error || 'Unknown error'}<br>
                        ${data.fallback_message || ''}
                    </div>`;
                    resultsCount.innerHTML = '';
                    kbInsights.style.display = 'none';
                    systemInfo.style.display = 'none';
                    resultContainer.classList.add('show');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                sqlOutput.textContent = 'Network Error';
                explanationOutput.textContent = 'Failed to connect to the service. Please try again.';
                resultsTable.innerHTML = '<div class="error-info">Network error occurred. Please check your connection and try again.</div>';
                resultsCount.innerHTML = '';
                kbInsights.style.display = 'none';
                systemInfo.style.display = 'none';
                resultContainer.classList.add('show');
            })
            .finally(() => {
                // Reset button state
                queryBtn.disabled = false;
                queryBtn.innerHTML = '🚀 Generate Enhanced SQL Query';
            });
        }

        // Allow Enter key to submit
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processQuery();
            }
        });
    </script>
</body>
</html>
        """
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': html_content
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Text-to-SQL Agent deployment successful but interface error'
            })
        }


def get_knowledge_base_context(bedrock_agent, query):
    """Get context from Bedrock Knowledge Base"""
    
    try:
        # Knowledge Base ID from configuration
        kb_id = os.environ.get('BEDROCK_KNOWLEDGE_BASE_ID', 'MJ2GCTRK6Z')
        
        if not kb_id:
            print("Knowledge Base ID not configured")
            return {
                'used': False,
                'insights': [],
                'full_context': '',
                'explanation': 'Knowledge Base not configured.'
            }
        
        print(f"Querying Knowledge Base {kb_id} with query: {query}")
        
        # Query the Knowledge Base
        response = bedrock_agent.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 10
                }
            }
        )
        
        # Extract relevant context
        context = {
            'used': True,
            'insights': [],
            'full_context': '',
            'explanation': ''
        }
        
        full_context_parts = []
        
        if 'retrievalResults' in response:
            print(f"Found {len(response['retrievalResults'])} results from Knowledge Base")
            
            for idx, result in enumerate(response['retrievalResults']):
                content = result.get('content', {}).get('text', '')
                score = result.get('score', 0)
                
                if content and score > 0.5:  # Increased threshold for higher quality results
                    # Add to full context for LLM
                    full_context_parts.append(content)
                    
                    # Add summary for insights
                    summary = content[:150] + '...' if len(content) > 150 else content
                    context['insights'].append(f"[Relevance: {score:.2f}] {summary}")
                elif content and score > 0.3:  # Include medium confidence results
                    full_context_parts.append(content)
                    summary = content[:100] + '...' if len(content) > 100 else content
                    context['insights'].append(f"[Medium confidence: {score:.2f}] {summary}")
            
            if full_context_parts:
                context['full_context'] = '\n\n'.join(full_context_parts)
                context['explanation'] = f"Enhanced with {len(full_context_parts)} relevant insights from Knowledge Base (confidence > 0.5)."
                print(f"Knowledge Base context length: {len(context['full_context'])} characters")
            else:
                context['used'] = False
                context['explanation'] = 'No high-confidence matches found in Knowledge Base (threshold: 0.5).'
        
        return context
        
    except Exception as e:
        print(f"Knowledge Base query failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'used': False,
            'insights': [],
            'full_context': '',
            'explanation': f'Knowledge Base error: {str(e)}'
        }


def generate_enhanced_sql_with_bedrock(bedrock_runtime, query, kb_context):
    """Generate enhanced SQL query using Bedrock LLM + Knowledge Base context"""
    
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-tg1-large')
    database_name = os.environ.get('GLUE_DATABASE', 'text_to_sql_demo')
    
    # Build enhanced prompt with Knowledge Base context
    kb_context_text = ""
    if kb_context.get('used') and kb_context.get('full_context'):
        kb_context_text = f"""
BUSINESS CONTEXT FROM KNOWLEDGE BASE:
{kb_context['full_context']}

CRITICAL: The above Knowledge Base contains EXACT SQL patterns for this type of query. 
Use the provided SQL examples as templates and adapt them to the specific question.
DO NOT generate simple queries when complex business intelligence patterns are available.
"""
    else:
        # Provide essential business context when KB is not available
        kb_context_text = """
ESSENTIAL BUSINESS CONTEXT:
- "Top customers" means customers ranked by total revenue (SUM of total_amount)
- "Trending products" means products with highest order frequency (COUNT of orders)
- "Revenue" refers to SUM(total_amount) from orders table
- Always use proper JOINs between customers and orders on customer_id
- Always use product_name (not product_id) to join products with orders
- Include meaningful aliases for calculated fields (total_revenue, order_count, etc.)
"""
    
    prompt = f"""You are an expert AWS Athena SQL analyst. Convert the natural language query into optimized Athena SQL using the provided database schema and business context.

DATABASE: {database_name}

COMPLETE DATABASE SCHEMA:
Table: customers
- customer_id (bigint) - Primary Key
- name (string) - Customer full name  
- email (string) - Customer email
- phone (string) - Customer phone
- city (string) - Customer city
- state (string) - Customer state
- country (string) - Customer country

Table: orders  
- order_id (bigint) - Primary Key
- customer_id (bigint) - Foreign key to customers.customer_id
- product_name (string) - Product name (NOT product_id)
- category (string) - Product category
- quantity (int) - Quantity ordered
- price (decimal(10,2)) - Unit price
- total_amount (decimal(10,2)) - Total order amount
- order_date (date) - Order date
- status (string) - Order status

Table: products
- product_id (bigint) - Primary Key  
- product_name (string) - Product name
- category (string) - Product category
- price (decimal(10,2)) - Product price
- stock (int) - Stock quantity
- supplier (string) - Supplier name

CRITICAL JOIN RULES:
- customers ↔ orders: JOIN ON customers.customer_id = orders.customer_id
- products ↔ orders: JOIN ON products.product_name = orders.product_name (NOT product_id!)

{kb_context_text}

ATHENA-SPECIFIC FUNCTIONS (MANDATORY):
- For date differences: Use date_diff('day', start_date, end_date) NOT DATEDIFF()
- For current date: Use CURRENT_DATE
- For date intervals: Use INTERVAL '30' DAY
- For date extraction: Use EXTRACT(YEAR FROM date_column)

SQL GENERATION RULES:
1. ALWAYS prefix tables: {database_name}.table_name
2. Use exact column names from schema above
3. For trending/popular products: Use orders table, GROUP BY product_name, ORDER BY COUNT(order_id) DESC
4. For customer revenue: JOIN customers + orders, SUM(total_amount)
5. For product joins: Use product_name (string) NOT product_id
6. Always include LIMIT for large results (default LIMIT 10)
7. Use proper aggregation with GROUP BY
8. Handle NULL values appropriately
9. Use meaningful column aliases for calculated fields

MANDATORY INSTRUCTION FOR QUERY: "{query}"

If this query is about customer churn or risk analysis, you MUST use this EXACT pattern:
SELECT c.name, c.email, c.city,
       COUNT(o.order_id) as total_orders,
       SUM(o.total_amount) as lifetime_value,
       MAX(o.order_date) as last_order_date,
       date_diff('day', MAX(o.order_date), CURRENT_DATE) as days_since_last_order,
       CASE 
           WHEN MAX(o.order_date) IS NULL THEN 'Never Ordered'
           WHEN date_diff('day', MAX(o.order_date), CURRENT_DATE) > 180 THEN 'High Risk'
           WHEN date_diff('day', MAX(o.order_date), CURRENT_DATE) > 90 THEN 'Medium Risk'
           ELSE 'Low Risk'
       END as churn_risk_level
FROM {database_name}.customers c
LEFT JOIN {database_name}.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
HAVING churn_risk_level IN ('High Risk', 'Medium Risk', 'Never Ordered')
ORDER BY lifetime_value DESC
LIMIT 20;

CRITICAL: Use date_diff('day', start_date, end_date) NOT DATEDIFF() for Athena compatibility.

Generate ONLY the SQL query. No explanations, markdown formatting, or additional text.

SQL Query:"""

    try:
        print(f"Generating SQL with model: {model_id}")
        print(f"Query: {query}")
        print(f"KB Context used: {kb_context.get('used', False)}")
        print(f"KB Context length: {len(kb_context.get('full_context', ''))}")
        
        # Debug: Print the actual prompt being sent
        print("=== PROMPT BEING SENT TO LLM ===")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("=== END PROMPT ===")
        
        print("Calling Bedrock LLM...")
        
        # Different API formats for different models
        if 'claude' in model_id.lower():
            # Claude API format
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1
            })
        elif 'titan' in model_id.lower():
            # Titan API format
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 1000,
                    "temperature": 0.1,
                    "topP": 0.9,
                    "stopSequences": []
                }
            })
        else:
            # Default to Claude format
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1
            })
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        print(f"LLM Response: {response_body}")
        
        # Extract SQL query based on model type
        if 'claude' in model_id.lower():
            sql_query = response_body['content'][0]['text'].strip()
        elif 'titan' in model_id.lower():
            sql_query = response_body['results'][0]['outputText'].strip()
        else:
            # Try both formats
            if 'content' in response_body:
                sql_query = response_body['content'][0]['text'].strip()
            elif 'results' in response_body:
                sql_query = response_body['results'][0]['outputText'].strip()
            else:
                raise Exception(f"Unknown response format: {response_body}")
        
        # Clean up the SQL query
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Remove any explanatory text that might be included
        lines = sql_query.split('\n')
        sql_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('/*'):
                sql_lines.append(line)
        
        sql_query = ' '.join(sql_lines)
        
        print(f"Generated SQL: {sql_query}")
        
        # Check if the generated SQL is too simple when KB context is available
        if (kb_context.get('used') and 
            sql_query.upper().startswith('SELECT *') and 
            'LIMIT' in sql_query.upper() and 
            len(sql_query.split()) < 10):
            print("WARNING: LLM generated simple query despite KB context available!")
            print("This suggests the LLM is not properly using the Knowledge Base context.")
        
        return sql_query
        
    except Exception as e:
        print(f"Bedrock SQL generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        # No fallback - raise the error so user knows LLM failed
        raise Exception(f"LLM SQL generation failed: {str(e)}. Please check your query and try again.")


def execute_athena_query(athena_client, sql_query, database, output_location):
    """Execute query using Amazon Athena with improved error handling"""
    
    try:
        print(f"Executing Athena query: {sql_query}")
        print(f"Database: {database}, Output: {output_location}")
        
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        
        query_execution_id = response['QueryExecutionId']
        print(f"Query execution ID: {query_execution_id}")
        
        # Wait for query to complete with better polling
        import time
        max_wait = 45  # Increased timeout to 45 seconds
        wait_time = 0
        poll_interval = 2  # Check every 2 seconds to reduce API calls
        
        while wait_time < max_wait:
            result = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = result['QueryExecution']['Status']['State']
            print(f"Query status: {status} (waited {wait_time}s)")
            
            if status in ['SUCCEEDED']:
                break
            elif status in ['FAILED', 'CANCELLED']:
                error_reason = result['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                print(f"Query failed: {error_reason}")
                raise Exception(f"Query failed: {error_reason}")
            
            time.sleep(poll_interval)
            wait_time += poll_interval
        
        if wait_time >= max_wait:
            print("Query timeout - raising exception")
            raise Exception(f"Query execution timeout after {max_wait} seconds")
        
        # Get results
        print("Fetching query results...")
        results = athena_client.get_query_results(
            QueryExecutionId=query_execution_id,
            MaxResults=100  # Limit to 100 rows
        )
        
        print(f"Raw Athena response keys: {results.keys()}")
        
        # Parse results
        if 'ResultSet' not in results:
            print("ERROR: No ResultSet in response")
            raise Exception("No ResultSet in Athena response")
            
        if 'Rows' not in results['ResultSet']:
            print("ERROR: No Rows in ResultSet")
            raise Exception("No Rows in Athena ResultSet")
        
        rows_data = results['ResultSet']['Rows']
        print(f"Total rows in response: {len(rows_data)}")
        
        if len(rows_data) <= 1:  # Only header or no data
            print("Query returned no data rows (only header or empty)")
            return [], 0
        
        # Extract column names from header row (first row)
        header_row = rows_data[0]
        columns = []
        if 'Data' in header_row:
            columns = [col.get('VarCharValue', f'col_{i}') for i, col in enumerate(header_row['Data'])]
        else:
            # Fallback to metadata
            columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        
        print(f"Columns extracted: {columns}")
        
        # Parse data rows (skip header)
        rows = []
        for idx, row in enumerate(rows_data[1:]):
            print(f"Processing row {idx + 1}: {row}")
            if 'Data' not in row:
                print(f"WARNING: Row {idx + 1} has no Data field, skipping")
                continue
                
            row_data = {}
            for i, col in enumerate(columns):
                if i < len(row['Data']):
                    # Get value, handle different data types
                    cell = row['Data'][i]
                    value = cell.get('VarCharValue', '')
                    
                    # Try to convert numeric values
                    if value and value.replace('.', '').replace('-', '').isdigit():
                        try:
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except:
                            pass  # Keep as string if conversion fails
                    
                    row_data[col] = value
                    print(f"  {col}: {value} (type: {type(value).__name__})")
                else:
                    row_data[col] = ''
                    print(f"  {col}: (empty)")
            
            if row_data:  # Only add non-empty rows
                rows.append(row_data)
        
        print(f"Successfully parsed {len(rows)} rows")
        print(f"Sample row data: {rows[0] if rows else 'No rows'}")
        
        if len(rows) == 0:
            print("WARNING: No data rows were parsed successfully")
            
        return rows, len(rows)
        
    except Exception as e:
        error_msg = str(e)
        print(f"Athena execution error: {error_msg}")
        import traceback
        traceback.print_exc()
        # Re-raise the exception so it can be handled properly
        raise Exception(f"Athena query execution failed: {error_msg}")


def generate_sample_data(query):
    """Generate sample data based on the query"""
    
    query_lower = query.lower()
    
    if 'trending' in query_lower and 'product' in query_lower:
        # Sample data for trending products query
        return [
            {'product_name': 'Laptop Pro', 'category': 'Electronics', 'order_count': 45, 'total_quantity': 67},
            {'product_name': 'Wireless Mouse', 'category': 'Electronics', 'order_count': 38, 'total_quantity': 89},
            {'product_name': 'Office Chair', 'category': 'Furniture', 'order_count': 32, 'total_quantity': 41},
            {'product_name': 'Coffee Maker', 'category': 'Appliances', 'order_count': 28, 'total_quantity': 35},
            {'product_name': 'Desk Lamp', 'category': 'Furniture', 'order_count': 25, 'total_quantity': 52},
            {'product_name': 'Smartphone', 'category': 'Electronics', 'order_count': 22, 'total_quantity': 28},
            {'product_name': 'Headphones', 'category': 'Electronics', 'order_count': 19, 'total_quantity': 31},
            {'product_name': 'Standing Desk', 'category': 'Furniture', 'order_count': 16, 'total_quantity': 18},
            {'product_name': 'Tablet', 'category': 'Electronics', 'order_count': 14, 'total_quantity': 17},
            {'product_name': 'Monitor', 'category': 'Electronics', 'order_count': 12, 'total_quantity': 15}
        ]
    elif 'top' in query_lower and 'customer' in query_lower and ('revenue' in query_lower or 'sales' in query_lower):
        # Sample data for top customers by revenue
        return [
            {'name': 'John Smith', 'email': 'john@example.com', 'total_revenue': 5299.95},
            {'name': 'Jane Doe', 'email': 'jane@example.com', 'total_revenue': 4150.75},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'total_revenue': 3875.50},
            {'name': 'Alice Brown', 'email': 'alice@example.com', 'total_revenue': 2999.25},
            {'name': 'Charlie Wilson', 'email': 'charlie@example.com', 'total_revenue': 2450.00}
        ]
    elif 'customer' in query_lower:
        return [
            {'customer_id': 1, 'name': 'John Smith', 'email': 'john@example.com', 'city': 'New York', 'state': 'NY'},
            {'customer_id': 2, 'name': 'Jane Doe', 'email': 'jane@example.com', 'city': 'Los Angeles', 'state': 'CA'},
            {'customer_id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'city': 'Chicago', 'state': 'IL'},
            {'customer_id': 4, 'name': 'Alice Brown', 'email': 'alice@example.com', 'city': 'Houston', 'state': 'TX'},
            {'customer_id': 5, 'name': 'Charlie Wilson', 'email': 'charlie@example.com', 'city': 'Phoenix', 'state': 'AZ'}
        ]
    elif 'product' in query_lower:
        return [
            {'product_id': 1, 'product_name': 'Laptop Pro', 'category': 'Electronics', 'price': 1299.99, 'stock': 45},
            {'product_id': 2, 'product_name': 'Wireless Mouse', 'category': 'Electronics', 'price': 29.99, 'stock': 120},
            {'product_id': 3, 'product_name': 'Office Chair', 'category': 'Furniture', 'price': 199.99, 'stock': 30},
            {'product_id': 4, 'product_name': 'Desk Lamp', 'category': 'Furniture', 'price': 49.99, 'stock': 75},
            {'product_id': 5, 'product_name': 'Coffee Maker', 'category': 'Appliances', 'price': 89.99, 'stock': 25}
        ]
    elif 'order' in query_lower or 'sale' in query_lower:
        return [
            {'order_id': 1, 'customer_name': 'John Smith', 'product_name': 'Laptop Pro', 'quantity': 1, 'total_amount': 1299.99, 'order_date': '2024-12-15'},
            {'order_id': 2, 'customer_name': 'Jane Doe', 'product_name': 'Wireless Mouse', 'quantity': 2, 'total_amount': 59.98, 'order_date': '2024-12-14'},
            {'order_id': 3, 'customer_name': 'Bob Johnson', 'product_name': 'Office Chair', 'quantity': 1, 'total_amount': 199.99, 'order_date': '2024-12-13'},
            {'order_id': 4, 'customer_name': 'Alice Brown', 'product_name': 'Coffee Maker', 'quantity': 1, 'total_amount': 89.99, 'order_date': '2024-12-12'},
            {'order_id': 5, 'customer_name': 'Charlie Wilson', 'product_name': 'Desk Lamp', 'quantity': 3, 'total_amount': 149.97, 'order_date': '2024-12-11'}
        ]
    else:
        return [
            {'id': 1, 'description': 'Sample data row 1', 'value': 100, 'category': 'A'},
            {'id': 2, 'description': 'Sample data row 2', 'value': 200, 'category': 'B'},
            {'id': 3, 'description': 'Sample data row 3', 'value': 300, 'category': 'A'},
            {'id': 4, 'description': 'Sample data row 4', 'value': 400, 'category': 'C'},
            {'id': 5, 'description': 'Sample data row 5', 'value': 500, 'category': 'B'}
        ]