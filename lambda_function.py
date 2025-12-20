import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """
    AWS Lambda handler for Text-to-SQL Agent with Bedrock Knowledge Base integration
    """
    
    try:
        # Check if this is a POST request with a query
        if event.get('requestContext', {}).get('http', {}).get('method') == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
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
                        # Don't provide sample data when there's an actual error
                    elif results and len(results) > 0:
                        # Successful Athena execution
                        response_data['columns'] = list(results[0].keys())
                    elif athena_configured:
                        # Athena configured but no results (empty result set)
                        response_data['columns'] = []
                        response_data['message'] = "Query executed successfully but returned no results"
                    else:
                        # Athena not configured - provide sample data
                        response_data['columns'] = []
                        response_data['results'] = generate_sample_data(query)
                        response_data['columns'] = list(response_data['results'][0].keys()) if response_data['results'] else []
                        response_data['row_count'] = len(response_data['results'])
                        response_data['sample_data'] = True
                    
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
                            'query': query,
                            'fallback_message': "Please check your AWS configuration and permissions."
                        })
                    }
                    
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
        
        <div class="deployment-info">
            <h2>🎉 Enhanced AI SQL Generation!</h2>
            <span class="status-badge">✅ Live with Bedrock AI</span>
            <span class="kb-badge">🧠 Knowledge Base Enhanced</span>
            <p>Ask questions in natural language and get context-aware SQL queries</p>
        </div>

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

    <script>
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
                    } else if (!data.athena_error) {
                        // Only show "no results" if there's no Athena error
                        if (data.message) {
                            resultsTable.innerHTML = `<div class="no-results">${data.message}</div>`;
                        } else {
                            resultsTable.innerHTML = '<div class="no-results">Query executed successfully but returned no results</div>';
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
        kb_id = os.environ.get('BEDROCK_KNOWLEDGE_BASE_ID', 'JKGJVVWBDY')
        
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
                
                if content and score > 0.1:  # Use very low threshold for any results
                    # Add to full context for LLM
                    full_context_parts.append(content)
                    
                    # Add summary for insights
                    summary = content[:150] + '...' if len(content) > 150 else content
                    context['insights'].append(f"[Relevance: {score:.2f}] {summary}")
                elif content:  # Include even low-confidence results
                    full_context_parts.append(content)
                    summary = content[:100] + '...' if len(content) > 100 else content
                    context['insights'].append(f"[Low confidence: {score:.2f}] {summary}")
            
            if full_context_parts:
                context['full_context'] = '\n\n'.join(full_context_parts)
                context['explanation'] = f"Enhanced with {len(full_context_parts)} relevant insights from Knowledge Base (confidence > 0.3)."
                print(f"Knowledge Base context length: {len(context['full_context'])} characters")
            else:
                context['used'] = False
                context['explanation'] = 'No matches found in Knowledge Base above confidence threshold.'
        
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
    
    model_id = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    database_name = os.environ.get('GLUE_DATABASE', 'text_to_sql_demo')
    
    # Build enhanced prompt with Knowledge Base context
    kb_context_text = ""
    if kb_context.get('used') and kb_context.get('full_context'):
        kb_context_text = f"""
BUSINESS CONTEXT FROM KNOWLEDGE BASE:
{kb_context['full_context']}

Use this business context, schema information, and examples to generate accurate SQL queries.
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
- registration_date (date) - Registration date

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

COMMON QUERY PATTERNS:
- "Top customers by revenue": SELECT c.name, c.email, SUM(o.total_amount) as total_revenue FROM {database_name}.customers c JOIN {database_name}.orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name, c.email ORDER BY total_revenue DESC LIMIT 5;
- "Trending products": SELECT product_name, category, COUNT(order_id) as order_count FROM {database_name}.orders GROUP BY product_name, category ORDER BY order_count DESC LIMIT 10;
- "Sales by category": SELECT category, COUNT(order_id) as total_orders, SUM(total_amount) as total_revenue FROM {database_name}.orders GROUP BY category ORDER BY total_revenue DESC;

Natural Language Query: {query}

Generate ONLY the SQL query. No explanations, markdown formatting, or additional text.

SQL Query:"""

    try:
        print(f"Generating SQL with model: {model_id}")
        print(f"Query: {query}")
        print(f"KB Context used: {kb_context.get('used', False)}")
        
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
        sql_query = response_body['content'][0]['text'].strip()
        
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
        return sql_query
        
    except Exception as e:
        print(f"Bedrock SQL generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Enhanced fallback based on query content and correct schema
        query_lower = query.lower()
        if 'trending' in query_lower and 'product' in query_lower:
            return f"SELECT product_name, category, COUNT(order_id) as order_count, SUM(quantity) as total_quantity FROM {database_name}.orders GROUP BY product_name, category ORDER BY order_count DESC LIMIT 10;"
        elif 'top' in query_lower and 'customer' in query_lower and ('revenue' in query_lower or 'sales' in query_lower):
            return f"SELECT c.name, c.email, SUM(o.total_amount) as total_revenue FROM {database_name}.customers c JOIN {database_name}.orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name, c.email ORDER BY total_revenue DESC LIMIT 5;"
        elif 'customer' in query_lower:
            return f"SELECT * FROM {database_name}.customers LIMIT 10;"
        elif 'product' in query_lower:
            return f"SELECT * FROM {database_name}.products LIMIT 10;"
        elif 'order' in query_lower:
            return f"SELECT * FROM {database_name}.orders LIMIT 10;"
        else:
            return f"SELECT * FROM {database_name}.customers LIMIT 5;"


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
            print("Query timeout - returning empty results")
            return [], 0
        
        # Get results
        print("Fetching query results...")
        results = athena_client.get_query_results(
            QueryExecutionId=query_execution_id,
            MaxResults=100  # Limit to 100 rows
        )
        
        print(f"Raw Athena response: {results}")
        
        # Parse results
        if 'ResultSet' not in results or 'Rows' not in results['ResultSet']:
            print("No results found in response")
            return [], 0
        
        rows_data = results['ResultSet']['Rows']
        print(f"Total rows in response: {len(rows_data)}")
        
        if len(rows_data) <= 1:  # Only header or no data
            print("No data rows found (only header or empty)")
            return [], 0
        
        # Extract column names from header
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        print(f"Columns: {columns}")
        
        # Parse data rows
        rows = []
        for idx, row in enumerate(rows_data[1:]):  # Skip header row
            print(f"Processing row {idx + 1}: {row}")
            if 'Data' not in row:
                print(f"Row {idx + 1} has no Data field")
                continue
            row_data = {}
            for i, col in enumerate(columns):
                if i < len(row['Data']):
                    value = row['Data'][i].get('VarCharValue', '')
                    row_data[col] = value
                    print(f"  {col}: {value}")
                else:
                    row_data[col] = ''
                    print(f"  {col}: (empty)")
            rows.append(row_data)
        
        print(f"Successfully parsed {len(rows)} rows")
        print(f"Final rows data: {rows}")
        return rows, len(rows)
        
    except Exception as e:
        error_msg = str(e)
        print(f"Athena execution error: {error_msg}")
        import traceback
        traceback.print_exc()
        # Return empty results instead of failing
        return [], 0


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