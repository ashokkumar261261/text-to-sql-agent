#!/usr/bin/env python3
"""
Create OpenSearch Serverless policies and collection for Knowledge Base.
"""

import boto3
import json
import time

def create_opensearch_infrastructure():
    """Create OpenSearch Serverless collection with required policies."""
    
    client = boto3.client('opensearchserverless', region_name='us-east-1')
    
    collection_name = "text-to-sql-collection"
    policy_prefix = "text-sql-kb"  # Shorter prefix for policy names
    
    # 1. Create encryption policy
    encryption_policy = {
        "Rules": [
            {
                "ResourceType": "collection",
                "Resource": [f"collection/{collection_name}"]
            }
        ],
        "AWSOwnedKey": True
    }
    
    try:
        print("Creating encryption policy...")
        client.create_security_policy(
            name=f"{policy_prefix}-encrypt",
            type='encryption',
            policy=json.dumps(encryption_policy)
        )
        print("✅ Encryption policy created")
    except client.exceptions.ConflictException:
        print("✅ Encryption policy already exists")
    except Exception as e:
        print(f"❌ Error creating encryption policy: {e}")
        return False
    
    # 2. Create network policy
    network_policy = [
        {
            "Rules": [
                {
                    "ResourceType": "collection",
                    "Resource": [f"collection/{collection_name}"]
                },
                {
                    "ResourceType": "dashboard",
                    "Resource": [f"collection/{collection_name}"]
                }
            ],
            "AllowFromPublic": True
        }
    ]
    
    try:
        print("Creating network policy...")
        client.create_security_policy(
            name=f"{policy_prefix}-network",
            type='network',
            policy=json.dumps(network_policy)
        )
        print("✅ Network policy created")
    except client.exceptions.ConflictException:
        print("✅ Network policy already exists")
    except Exception as e:
        print(f"❌ Error creating network policy: {e}")
        return False
    
    # 3. Create data access policy
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()['Account']
    
    data_access_policy = [
        {
            "Rules": [
                {
                    "ResourceType": "collection",
                    "Resource": [f"collection/{collection_name}"],
                    "Permission": [
                        "aoss:CreateCollectionItems",
                        "aoss:DeleteCollectionItems", 
                        "aoss:UpdateCollectionItems",
                        "aoss:DescribeCollectionItems"
                    ]
                },
                {
                    "ResourceType": "index",
                    "Resource": [f"index/{collection_name}/*"],
                    "Permission": [
                        "aoss:CreateIndex",
                        "aoss:DeleteIndex",
                        "aoss:UpdateIndex", 
                        "aoss:DescribeIndex",
                        "aoss:ReadDocument",
                        "aoss:WriteDocument"
                    ]
                }
            ],
            "Principal": [
                f"arn:aws:iam::{account_id}:role/BedrockKnowledgeBaseRole",
                f"arn:aws:iam::{account_id}:root"
            ]
        }
    ]
    
    try:
        print("Creating data access policy...")
        client.create_access_policy(
            name=f"{policy_prefix}-data",
            type='data',
            policy=json.dumps(data_access_policy)
        )
        print("✅ Data access policy created")
    except client.exceptions.ConflictException:
        print("✅ Data access policy already exists")
    except Exception as e:
        print(f"❌ Error creating data access policy: {e}")
        return False
    
    # 4. Create collection
    try:
        print("Creating OpenSearch Serverless collection...")
        response = client.create_collection(
            name=collection_name,
            type='VECTORSEARCH',
            description='Vector collection for Text-to-SQL Knowledge Base'
        )
        
        collection_id = response['createCollectionDetail']['id']
        collection_arn = response['createCollectionDetail']['arn']
        
        print(f"✅ Collection created: {collection_name}")
        print(f"   ID: {collection_id}")
        print(f"   ARN: {collection_arn}")
        
        # Wait for collection to be active
        print("Waiting for collection to become active...")
        while True:
            status_response = client.batch_get_collection(names=[collection_name])
            status = status_response['collectionDetails'][0]['status']
            print(f"   Status: {status}")
            
            if status == 'ACTIVE':
                break
            elif status == 'FAILED':
                print("❌ Collection creation failed")
                return False
            
            time.sleep(10)
        
        print("✅ Collection is now active!")
        return collection_arn
        
    except client.exceptions.ConflictException:
        print("✅ Collection already exists")
        # Get existing collection info
        response = client.batch_get_collection(names=[collection_name])
        collection_arn = response['collectionDetails'][0]['arn']
        return collection_arn
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return False

if __name__ == "__main__":
    collection_arn = create_opensearch_infrastructure()
    if collection_arn:
        print(f"\n🎉 OpenSearch infrastructure ready!")
        print(f"Collection ARN: {collection_arn}")
        print(f"\nNext: Create Bedrock Knowledge Base using this collection")
    else:
        print("❌ Failed to create OpenSearch infrastructure")