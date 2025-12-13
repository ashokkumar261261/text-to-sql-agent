#!/usr/bin/env python3
"""
Setup script for creating and configuring Amazon Bedrock Knowledge Base
for the Text-to-SQL Agent project.
"""

import os
import json
import boto3
import argparse
from dotenv import load_dotenv
from src.knowledge_base import KnowledgeBaseManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def create_s3_bucket_if_not_exists(bucket_name: str, region: str) -> bool:
    """Create S3 bucket if it doesn't exist."""
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"S3 bucket {bucket_name} already exists")
        return True
    except:
        pass
    
    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        logger.info(f"Created S3 bucket: {bucket_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create S3 bucket {bucket_name}: {str(e)}")
        return False


def create_iam_role_for_knowledge_base(role_name: str) -> str:
    """Create IAM role for Bedrock Knowledge Base."""
    iam_client = boto3.client('iam')
    
    # Trust policy for Bedrock
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::*",
                    f"arn:aws:s3:::*/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "aoss:APIAccessAll"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create role
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Bedrock Knowledge Base access'
        )
        
        role_arn = response['Role']['Arn']
        
        # Attach inline policy
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockKnowledgeBasePolicy',
            PolicyDocument=json.dumps(permissions_policy)
        )
        
        logger.info(f"Created IAM role: {role_arn}")
        return role_arn
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        logger.info(f"IAM role already exists: {role_arn}")
        return role_arn
        
    except Exception as e:
        logger.error(f"Failed to create IAM role: {str(e)}")
        raise


def setup_knowledge_base(bucket_name: str, kb_name: str, role_name: str) -> str:
    """Set up the complete knowledge base infrastructure."""
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Step 1: Create S3 bucket
    logger.info("Step 1: Setting up S3 bucket...")
    if not create_s3_bucket_if_not_exists(bucket_name, region):
        raise Exception("Failed to create S3 bucket")
    
    # Step 2: Create IAM role
    logger.info("Step 2: Creating IAM role...")
    role_arn = create_iam_role_for_knowledge_base(role_name)
    
    # Step 3: Upload sample documents
    logger.info("Step 3: Creating and uploading knowledge base documents...")
    kb_manager = KnowledgeBaseManager()
    documents = kb_manager.create_sample_knowledge_base_content()
    uploaded_keys = kb_manager.upload_knowledge_base_documents(bucket_name, documents)
    
    logger.info(f"Uploaded {len(uploaded_keys)} documents to S3")
    
    # Step 4: Display next steps
    logger.info("\n" + "="*60)
    logger.info("KNOWLEDGE BASE SETUP COMPLETED!")
    logger.info("="*60)
    logger.info(f"S3 Bucket: {bucket_name}")
    logger.info(f"IAM Role ARN: {role_arn}")
    logger.info(f"Documents uploaded: {len(uploaded_keys)}")
    
    logger.info("\nNEXT STEPS:")
    logger.info("1. Create OpenSearch Serverless collection in AWS Console")
    logger.info("2. Create Bedrock Knowledge Base in AWS Console using:")
    logger.info(f"   - S3 bucket: s3://{bucket_name}/knowledge-base/")
    logger.info(f"   - IAM role: {role_arn}")
    logger.info("3. Update your .env file with BEDROCK_KNOWLEDGE_BASE_ID")
    logger.info("4. Test the knowledge base integration")
    
    # Generate CloudFormation template for easier setup
    cf_template = generate_cloudformation_template(bucket_name, role_name, kb_name)
    cf_file = "knowledge_base_infrastructure.yaml"
    
    with open(cf_file, 'w') as f:
        f.write(cf_template)
    
    logger.info(f"\nCloudFormation template saved to: {cf_file}")
    logger.info("You can use this template to create the complete infrastructure")
    
    return role_arn


def generate_cloudformation_template(bucket_name: str, role_name: str, kb_name: str) -> str:
    """Generate CloudFormation template for knowledge base infrastructure."""
    
    template = f"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'Infrastructure for Text-to-SQL Agent Knowledge Base'

Parameters:
  KnowledgeBaseName:
    Type: String
    Default: {kb_name}
    Description: Name for the Bedrock Knowledge Base
  
  S3BucketName:
    Type: String
    Default: {bucket_name}
    Description: S3 bucket for knowledge base documents

Resources:
  # OpenSearch Serverless Collection
  OpenSearchCollection:
    Type: AWS::OpenSearchServerless::Collection
    Properties:
      Name: !Sub '${{KnowledgeBaseName}}-collection'
      Type: VECTORSEARCH
      Description: 'Vector collection for Text-to-SQL Knowledge Base'

  # OpenSearch Serverless Security Policy
  OpenSearchSecurityPolicy:
    Type: AWS::OpenSearchServerless::SecurityPolicy
    Properties:
      Name: !Sub '${{KnowledgeBaseName}}-security-policy'
      Type: encryption
      Policy: !Sub |
        {{
          "Rules": [
            {{
              "ResourceType": "collection",
              "Resource": ["collection/${{KnowledgeBaseName}}-collection"]
            }}
          ],
          "AWSOwnedKey": true
        }}

  # OpenSearch Network Policy
  OpenSearchNetworkPolicy:
    Type: AWS::OpenSearchServerless::SecurityPolicy
    Properties:
      Name: !Sub '${{KnowledgeBaseName}}-network-policy'
      Type: network
      Policy: !Sub |
        [
          {{
            "Rules": [
              {{
                "ResourceType": "collection",
                "Resource": ["collection/${{KnowledgeBaseName}}-collection"]
              }},
              {{
                "ResourceType": "dashboard",
                "Resource": ["collection/${{KnowledgeBaseName}}-collection"]
              }}
            ],
            "AllowFromPublic": true
          }}
        ]

  # OpenSearch Data Access Policy
  OpenSearchDataAccessPolicy:
    Type: AWS::OpenSearchServerless::AccessPolicy
    Properties:
      Name: !Sub '${{KnowledgeBaseName}}-data-access-policy'
      Type: data
      Policy: !Sub |
        [
          {{
            "Rules": [
              {{
                "ResourceType": "collection",
                "Resource": ["collection/${{KnowledgeBaseName}}-collection"],
                "Permission": [
                  "aoss:CreateCollectionItems",
                  "aoss:DeleteCollectionItems",
                  "aoss:UpdateCollectionItems",
                  "aoss:DescribeCollectionItems"
                ]
              }},
              {{
                "ResourceType": "index",
                "Resource": ["index/${{KnowledgeBaseName}}-collection/*"],
                "Permission": [
                  "aoss:CreateIndex",
                  "aoss:DeleteIndex",
                  "aoss:UpdateIndex",
                  "aoss:DescribeIndex",
                  "aoss:ReadDocument",
                  "aoss:WriteDocument"
                ]
              }}
            ],
            "Principal": [
              "arn:aws:iam::${{AWS::AccountId}}:role/{role_name}",
              "arn:aws:iam::${{AWS::AccountId}}:root"
            ]
          }}
        ]

Outputs:
  OpenSearchCollectionArn:
    Description: 'ARN of the OpenSearch Serverless collection'
    Value: !GetAtt OpenSearchCollection.Arn
    Export:
      Name: !Sub '${{AWS::StackName}}-OpenSearchCollectionArn'
  
  OpenSearchCollectionEndpoint:
    Description: 'Endpoint of the OpenSearch Serverless collection'
    Value: !GetAtt OpenSearchCollection.CollectionEndpoint
    Export:
      Name: !Sub '${{AWS::StackName}}-OpenSearchCollectionEndpoint'
  
  S3BucketName:
    Description: 'S3 bucket for knowledge base documents'
    Value: !Ref S3BucketName
    Export:
      Name: !Sub '${{AWS::StackName}}-S3BucketName'
"""
    
    return template


def main():
    parser = argparse.ArgumentParser(description='Setup Bedrock Knowledge Base for Text-to-SQL Agent')
    parser.add_argument('--bucket-name', required=True, help='S3 bucket name for knowledge base documents')
    parser.add_argument('--kb-name', default='text-to-sql-kb', help='Knowledge base name')
    parser.add_argument('--role-name', default='BedrockKnowledgeBaseRole', help='IAM role name')
    
    args = parser.parse_args()
    
    try:
        setup_knowledge_base(args.bucket_name, args.kb_name, args.role_name)
        logger.info("Knowledge base setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())