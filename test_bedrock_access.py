import boto3
import json

def test_bedrock_models():
    """Test which Bedrock models are accessible"""
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # List of models to test
    models_to_test = [
        'anthropic.claude-3-5-haiku-20241022-v1:0',
        'anthropic.claude-3-haiku-20240307-v1:0',
        'amazon.titan-text-express-v1',
        'amazon.titan-text-lite-v1'
    ]
    
    for model_id in models_to_test:
        try:
            print(f"Testing model: {model_id}")
            
            # Simple test prompt
            if 'claude' in model_id.lower():
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 100,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello, can you respond with 'Model working'?"
                        }
                    ],
                    "temperature": 0.1
                })
            else:  # Titan
                body = json.dumps({
                    "inputText": "Hello, can you respond with 'Model working'?",
                    "textGenerationConfig": {
                        "maxTokenCount": 100,
                        "temperature": 0.1
                    }
                })
            
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=body,
                contentType='application/json'
            )
            
            print(f"✅ {model_id} - SUCCESS")
            
        except Exception as e:
            print(f"❌ {model_id} - ERROR: {str(e)}")
    
if __name__ == "__main__":
    test_bedrock_models()