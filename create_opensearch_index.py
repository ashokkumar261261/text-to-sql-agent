#!/usr/bin/env python3
"""
Create OpenSearch index for Bedrock Knowledge Base.
"""

import requests
import json
from requests.auth import HTTPBasicAuth
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

def create_opensearch_index():
    """Create the required index in OpenSearch Serverless."""
    
    # Collection details
    collection_endpoint = "https://e9ex0v2xiya5ccb91445.us-east-1.aoss.amazonaws.com"
    index_name = "bedrock-knowledge-base-default-index"
    
    # Create index mapping
    index_mapping = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 512
            }
        },
        "mappings": {
            "properties": {
                "bedrock-knowledge-base-default-vector": {
                    "type": "knn_vector",
                    "dimension": 1536,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": 512,
                            "m": 16
                        }
                    }
                },
                "AMAZON_BEDROCK_TEXT_CHUNK": {
                    "type": "text"
                },
                "AMAZON_BEDROCK_METADATA": {
                    "type": "text"
                }
            }
        }
    }
    
    # Create authenticated request
    session = boto3.Session()
    credentials = session.get_credentials()
    region = 'us-east-1'
    service = 'aoss'
    
    url = f"{collection_endpoint}/{index_name}"
    
    # Create the request
    request = AWSRequest(method='PUT', url=url, data=json.dumps(index_mapping))
    request.headers['Content-Type'] = 'application/json'
    
    # Sign the request
    SigV4Auth(credentials, service, region).add_auth(request)
    
    try:
        # Make the request
        response = requests.put(
            url,
            data=json.dumps(index_mapping),
            headers=dict(request.headers)
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Index '{index_name}' created successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to create index. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return False

if __name__ == "__main__":
    success = create_opensearch_index()
    if success:
        print("\n🎉 OpenSearch index is ready!")
        print("Now you can create the Bedrock Knowledge Base")
    else:
        print("❌ Failed to create OpenSearch index")