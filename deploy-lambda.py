#!/usr/bin/env python3
"""
Deploy Text-to-SQL Agent to AWS Lambda (Serverless)
Alternative deployment without Docker
"""

import boto3
import zipfile
import os
import json
from pathlib import Path

def create_lambda_package():
    """Create deployment package for Lambda"""
    print("📦 Creating Lambda deployment package...")
    
    # Create deployment directory
    deploy_dir = Path("lambda-deploy")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy application files
    app_files = [
        "web_ui_enhanced.py",
        "src/",
        "requirements.txt",
        "requirements-web.txt",
        ".env.example",
        "business_glossary.md"
    ]
    
    for file_path in app_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                # Copy directory
                import shutil
                shutil.copytree(file_path, deploy_dir / file_path, dirs_exist_ok=True)
            else:
                # Copy file
                import shutil
                shutil.copy2(file_path, deploy_dir / file_path)
    
    # Create Lambda handler
    lambda_handler = '''
import json
import base64
import subprocess
import sys
import os

def lambda_handler(event, context):
    """AWS Lambda handler for Text-to-SQL Agent"""
    
    try:
        # Set environment variables
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
        
        # Import the enhanced agent
        sys.path.append('/var/task')
        from src.enhanced_agent import EnhancedTextToSQLAgent
        
        # Get query from event
        query = event.get('query', 'Show me sample data')
        
        # Initialize agent
        agent = EnhancedTextToSQLAgent(
            enable_knowledge_base=True,
            enable_cache=True
        )
        
        # Process query
        result = agent.query(query, execute=True, explain=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'query': query,
                'sql': result.get('sql_query', ''),
                'results': result.get('results', []),
                'explanation': result.get('explanation', ''),
                'success': True
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
                'error': str(e),
                'success': False
            })
        }
'''
    
    # Write Lambda handler
    with open(deploy_dir / "lambda_function.py", "w") as f:
        f.write(lambda_handler)
    
    # Create requirements for Lambda
    lambda_requirements = '''
boto3>=1.26.0
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
requests>=2.28.0
'''
    
    with open(deploy_dir / "requirements-lambda.txt", "w") as f:
        f.write(lambda_requirements)
    
    print("✅ Lambda package created in lambda-deploy/")
    return deploy_dir

def deploy_to_lambda():
    """Deploy to AWS Lambda"""
    print("🚀 Deploying to AWS Lambda...")
    
    # Create Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create deployment package
    deploy_dir = create_lambda_package()
    
    # Create ZIP file
    zip_path = "text-to-sql-lambda.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"📦 Created deployment package: {zip_path}")
    
    # Read ZIP file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    function_name = "text-to-sql-agent"
    
    try:
        # Try to update existing function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print("📝 Updated existing Lambda function")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role='arn:aws:iam::189796657651:role/lambda-execution-role',  # Update with your role
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Text-to-SQL Agent API',
            Timeout=300,
            MemorySize=1024,
            Environment={
                'Variables': {
                    'AWS_DEFAULT_REGION': 'us-east-1',
                    'STREAMLIT_SERVER_HEADLESS': 'true'
                }
            }
        )
        print("🆕 Created new Lambda function")
    
    # Create API Gateway (optional)
    try:
        apigateway = boto3.client('apigatewayv2', region_name='us-east-1')
        
        # Create HTTP API
        api_response = apigateway.create_api(
            Name='text-to-sql-api',
            ProtocolType='HTTP',
            Description='Text-to-SQL Agent API'
        )
        
        api_id = api_response['ApiId']
        
        # Create integration
        integration_response = apigateway.create_integration(
            ApiId=api_id,
            IntegrationType='AWS_PROXY',
            IntegrationUri=f"arn:aws:lambda:us-east-1:189796657651:function:{function_name}",
            PayloadFormatVersion='2.0'
        )
        
        # Create route
        route_response = apigateway.create_route(
            ApiId=api_id,
            RouteKey='POST /query',
            Target=f"integrations/{integration_response['IntegrationId']}"
        )
        
        # Create stage
        stage_response = apigateway.create_stage(
            ApiId=api_id,
            StageName='prod',
            AutoDeploy=True
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"🌐 API Gateway URL: {api_url}")
        
    except Exception as e:
        print(f"⚠️ API Gateway setup failed: {e}")
    
    print("✅ Lambda deployment completed!")
    print(f"📋 Function ARN: {response['FunctionArn']}")
    
    # Cleanup
    os.remove(zip_path)
    import shutil
    shutil.rmtree(deploy_dir)
    
    return response

if __name__ == "__main__":
    print("🚀 Text-to-SQL Agent - AWS Lambda Deployment")
    print("=" * 50)
    
    try:
        result = deploy_to_lambda()
        print("\n🎉 Deployment successful!")
        print("\n📋 Next steps:")
        print("1. Test the Lambda function in AWS Console")
        print("2. Configure API Gateway for public access")
        print("3. Set up proper IAM roles and permissions")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure AWS CLI is configured")
        print("2. Check IAM permissions")
        print("3. Verify Lambda execution role exists")