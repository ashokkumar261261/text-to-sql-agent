#!/usr/bin/env python3
"""
Check available Bedrock models and test access
"""

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()


def check_available_models():
    """Check which Bedrock models are available."""
    print("=" * 70)
    print("Checking Available Bedrock Models")
    print("=" * 70 + "\n")
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        bedrock = boto3.client('bedrock', region_name=region)
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # List foundation models
        response = bedrock.list_foundation_models()
        
        # Models we're interested in
        claude_models = []
        other_models = []
        
        for model in response.get('modelSummaries', []):
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', 'Unknown')
            provider = model.get('providerName', 'Unknown')
            
            if 'claude' in model_id.lower():
                claude_models.append((model_id, model_name, provider))
            elif any(x in model_id.lower() for x in ['titan', 'llama', 'mistral', 'cohere']):
                other_models.append((model_id, model_name, provider))
        
        print("Claude Models (Anthropic):")
        for model_id, name, provider in claude_models:
            # Test access
            status = test_model_access(bedrock_runtime, model_id)
            print(f"  {status} {name}")
            print(f"      ID: {model_id}")
        
        print("\nOther Available Models:")
        for model_id, name, provider in other_models:
            status = test_model_access(bedrock_runtime, model_id)
            print(f"  {status} {name} ({provider})")
            print(f"      ID: {model_id}")
        
        print("\n" + "=" * 70)
        print("Recommendations:")
        print("=" * 70)
        
        # Find working models
        working_models = []
        for model_id, name, provider in claude_models + other_models:
            if test_model_access(bedrock_runtime, model_id) == "✓":
                working_models.append((model_id, name))
        
        if working_models:
            print("\n✓ Working models found:")
            for model_id, name in working_models:
                print(f"  - {name}")
                print(f"    Update .env: BEDROCK_MODEL_ID={model_id}")
        else:
            print("\n⚠ No models are currently accessible.")
            print("\nPossible reasons:")
            print("  1. Payment method validation in progress (wait 10-15 minutes)")
            print("  2. Model access not enabled in Bedrock console")
            print("  3. AWS Marketplace subscription required")
            print("\nTry these models (usually no subscription needed):")
            print("  - amazon.titan-text-express-v1")
            print("  - anthropic.claude-instant-v1")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def test_model_access(bedrock_runtime, model_id):
    """Test if a model is accessible."""
    try:
        # Try a minimal invocation
        if 'claude' in model_id:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            })
        elif 'titan' in model_id:
            body = json.dumps({
                "inputText": "Hi",
                "textGenerationConfig": {"maxTokenCount": 10}
            })
        elif 'llama' in model_id or 'mistral' in model_id:
            body = json.dumps({
                "prompt": "Hi",
                "max_gen_len": 10
            })
        else:
            return "?"
        
        bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        return "✓"
        
    except Exception as e:
        error_str = str(e)
        if "AccessDeniedException" in error_str:
            if "INVALID_PAYMENT" in error_str:
                return "✗ (Payment)"
            elif "not enabled" in error_str or "not authorized" in error_str:
                return "✗ (Not enabled)"
            else:
                return "✗ (No access)"
        elif "ValidationException" in error_str:
            return "✓ (Accessible)"
        else:
            return "✗"


def suggest_alternative():
    """Suggest alternative models."""
    print("\n" + "=" * 70)
    print("Alternative Solutions")
    print("=" * 70 + "\n")
    
    print("Option 1: Wait for Payment Validation")
    print("  - AWS needs 10-15 minutes to validate payment")
    print("  - Check AWS Billing console for status")
    print("  - Try again after waiting")
    print()
    
    print("Option 2: Try Amazon Titan (Usually Free)")
    print("  - Model: amazon.titan-text-express-v1")
    print("  - Usually available immediately")
    print("  - No marketplace subscription needed")
    print("  - Update .env: BEDROCK_MODEL_ID=amazon.titan-text-express-v1")
    print("  - Note: You'll need to update agent.py for Titan API format")
    print()
    
    print("Option 3: Use Claude Instant (Cheaper)")
    print("  - Model: anthropic.claude-instant-v1")
    print("  - Faster and cheaper than Sonnet")
    print("  - Same API format")
    print("  - Update .env: BEDROCK_MODEL_ID=anthropic.claude-instant-v1")
    print()
    
    print("Option 4: Check Bedrock Console")
    print("  - Go to: https://console.aws.amazon.com/bedrock/")
    print("  - Click 'Model access' in sidebar")
    print("  - Verify Claude 3 Sonnet shows 'Access granted'")
    print("  - If not, request access again")
    print()


def main():
    print("\n" + "=" * 70)
    print("Bedrock Model Access Checker")
    print("=" * 70 + "\n")
    
    check_available_models()
    suggest_alternative()
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("\n1. Wait 10-15 minutes after adding payment method")
    print("2. Check AWS Billing console for payment status")
    print("3. Try a different model (Titan or Claude Instant)")
    print("4. Verify model access in Bedrock console")
    print("5. Run this script again to check status")
    print()


if __name__ == "__main__":
    main()
