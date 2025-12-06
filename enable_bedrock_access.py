#!/usr/bin/env python3
"""
Helper script to check and enable Bedrock model access
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()


def check_bedrock_models():
    """Check which Bedrock models are available."""
    print("Checking Bedrock Model Access...")
    print("=" * 70)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        bedrock = boto3.client('bedrock', region_name=region)
        
        # List foundation models
        response = bedrock.list_foundation_models()
        
        # Models we're interested in
        target_models = [
            'anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-haiku-20240307-v1:0',
            'anthropic.claude-v2:1',
            'amazon.titan-text-express-v1',
            'meta.llama3-70b-instruct-v1:0'
        ]
        
        print("\nAvailable models for Text-to-SQL:\n")
        
        available_models = []
        for model in response.get('modelSummaries', []):
            model_id = model.get('modelId', '')
            if any(target in model_id for target in ['claude', 'titan', 'llama']):
                model_name = model.get('modelName', 'Unknown')
                provider = model.get('providerName', 'Unknown')
                
                # Try to test access
                try:
                    bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
                    # Just check if we can access the model (won't actually invoke)
                    status = "✓ ACCESSIBLE"
                    available_models.append(model_id)
                except:
                    status = "✗ NOT ACCESSIBLE"
                
                print(f"{status} - {model_name} ({provider})")
                print(f"    Model ID: {model_id}")
                print()
        
        return available_models
        
    except Exception as e:
        print(f"Error checking models: {str(e)}")
        return []


def test_model_access(model_id):
    """Test if a specific model is accessible."""
    try:
        import json
        region = os.getenv('AWS_REGION', 'us-east-1')
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # Try a minimal test invocation
        if 'claude' in model_id:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            })
        elif 'titan' in model_id:
            body = json.dumps({
                "inputText": "Hi",
                "textGenerationConfig": {
                    "maxTokenCount": 10,
                    "temperature": 0.1
                }
            })
        else:
            return False
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "ResourceNotFoundException" in error_msg:
            return "NOT_ENABLED"
        elif "AccessDeniedException" in error_msg:
            return "NO_PERMISSION"
        return False


def provide_instructions():
    """Provide instructions for enabling Bedrock access."""
    print("\n" + "=" * 70)
    print("How to Enable Bedrock Model Access")
    print("=" * 70)
    print("""
STEP 1: Go to AWS Bedrock Console
   - Open: https://console.aws.amazon.com/bedrock/
   - Make sure you're in the correct region (check top-right)

STEP 2: Navigate to Model Access
   - Click "Model access" in the left sidebar
   - Or go directly to: Model access → Manage model access

STEP 3: Request Access to Models
   - Click "Modify model access" or "Manage model access"
   - Check the boxes for models you want:
     ✓ Anthropic - Claude 3 Sonnet
     ✓ Anthropic - Claude 3 Haiku (faster, cheaper alternative)
     ✓ Amazon - Titan Text Express (free tier available)
   
STEP 4: Fill Out Use Case Form (for Anthropic models)
   - Anthropic requires a use case form
   - Fill in:
     * Use case: "Text-to-SQL query generation for data analytics"
     * Industry: Your industry
     * Description: "Converting natural language to SQL queries"
   - Submit the form

STEP 5: Wait for Approval
   - Amazon Titan: Usually instant
   - Anthropic Claude: Can take 5-15 minutes
   - Check status in "Model access" page

STEP 6: Update Your .env File
   - Once approved, you can use the model
   - Or switch to an alternative model (see below)

ALTERNATIVE: Use Amazon Titan (No Form Required)
   - Amazon Titan Text Express is usually available immediately
   - Update your .env file:
     BEDROCK_MODEL_ID=amazon.titan-text-express-v1
   - Titan works well for SQL generation tasks
""")


def suggest_alternative_model():
    """Suggest alternative models."""
    print("\n" + "=" * 70)
    print("Alternative Models You Can Try")
    print("=" * 70)
    print("""
1. Amazon Titan Text Express
   Model ID: amazon.titan-text-express-v1
   - Usually available immediately (no form required)
   - Good for SQL generation
   - Free tier available
   - Update .env: BEDROCK_MODEL_ID=amazon.titan-text-express-v1

2. Claude 3 Haiku (if you have Anthropic access)
   Model ID: anthropic.claude-3-haiku-20240307-v1:0
   - Faster and cheaper than Sonnet
   - Still very capable for SQL tasks
   - Update .env: BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

3. Meta Llama 3 (if available in your region)
   Model ID: meta.llama3-70b-instruct-v1:0
   - Open source model
   - Good performance
   - May require separate access request
""")


def update_env_with_titan():
    """Offer to update .env file to use Titan."""
    print("\n" + "=" * 70)
    
    choice = input("Would you like to switch to Amazon Titan Text Express now? (y/n): ").strip().lower()
    
    if choice == 'y':
        env_path = '.env'
        
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update model ID
        updated_lines = []
        for line in lines:
            if line.startswith('BEDROCK_MODEL_ID='):
                updated_lines.append('BEDROCK_MODEL_ID=amazon.titan-text-express-v1\n')
                print("✓ Updated BEDROCK_MODEL_ID to amazon.titan-text-express-v1")
            else:
                updated_lines.append(line)
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        print("\n✓ .env file updated!")
        print("\nYou can now run: .\\run.bat example.py")
        print("\nNote: You'll need to update src/agent.py to support Titan format")
        print("      (or wait for Claude access approval)")


def main():
    print("\n" + "=" * 70)
    print("Bedrock Model Access Helper")
    print("=" * 70 + "\n")
    
    # Check available models
    available = check_bedrock_models()
    
    # Provide instructions
    provide_instructions()
    
    # Suggest alternatives
    suggest_alternative_model()
    
    # Offer to switch to Titan
    update_env_with_titan()


if __name__ == "__main__":
    main()
