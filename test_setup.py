#!/usr/bin/env python3
"""
Test script to verify your AWS setup and configuration
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """Check if environment variables are set."""
    print("Checking Environment Variables...")
    print("=" * 60)
    
    required_vars = {
        'AWS_REGION': os.getenv('AWS_REGION'),
        'GLUE_DATABASE': os.getenv('GLUE_DATABASE'),
        'ATHENA_OUTPUT_LOCATION': os.getenv('ATHENA_OUTPUT_LOCATION'),
        'BEDROCK_MODEL_ID': os.getenv('BEDROCK_MODEL_ID')
    }
    
    all_set = True
    for var, value in required_vars.items():
        status = "✓" if value else "✗"
        print(f"{status} {var}: {value or 'NOT SET'}")
        if not value:
            all_set = False
    
    print()
    return all_set


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("Checking AWS Credentials...")
    print("=" * 60)
    
    try:
        import boto3
        
        sts = boto3.client('sts', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        identity = sts.get_caller_identity()
        
        print(f"✓ AWS credentials are valid")
        print(f"  Account: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        print()
        return True
        
    except Exception as e:
        print(f"✗ AWS credentials error: {str(e)}")
        print()
        return False


def check_glue_database():
    """Check if Glue database exists."""
    print("Checking Glue Database...")
    print("=" * 60)
    
    try:
        import boto3
        
        database = os.getenv('GLUE_DATABASE')
        if not database:
            print("✗ GLUE_DATABASE not set in .env file")
            print()
            return False
        
        glue = boto3.client('glue', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        try:
            response = glue.get_database(Name=database)
            print(f"✓ Glue database '{database}' exists")
            
            # List tables
            tables_response = glue.get_tables(DatabaseName=database)
            tables = [t['Name'] for t in tables_response.get('TableList', [])]
            
            if tables:
                print(f"  Tables found: {', '.join(tables)}")
            else:
                print("  ⚠ No tables found in database")
            
            print()
            return True
            
        except glue.exceptions.EntityNotFoundException:
            print(f"✗ Glue database '{database}' not found")
            print("  Create it using: py setup_glue_sample.py")
            print()
            return False
            
    except Exception as e:
        print(f"✗ Error checking Glue database: {str(e)}")
        print()
        return False


def check_bedrock_access():
    """Check if Bedrock model is accessible."""
    print("Checking Bedrock Access...")
    print("=" * 60)
    
    try:
        import boto3
        
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Try a simple test invocation
        import json
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        })
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body
        )
        
        print(f"✓ Bedrock model '{model_id}' is accessible")
        print()
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "AccessDeniedException" in error_msg or "access" in error_msg.lower():
            print(f"✗ Bedrock access denied")
            print("  Enable model access in AWS Bedrock console:")
            print("  1. Go to AWS Bedrock console")
            print("  2. Navigate to 'Model access'")
            print("  3. Request access to 'Anthropic Claude 3 Sonnet'")
        else:
            print(f"✗ Error accessing Bedrock: {error_msg}")
        print()
        return False


def check_athena_output():
    """Check if Athena output location is accessible."""
    print("Checking Athena Output Location...")
    print("=" * 60)
    
    try:
        import boto3
        
        output_location = os.getenv('ATHENA_OUTPUT_LOCATION')
        if not output_location:
            print("✗ ATHENA_OUTPUT_LOCATION not set in .env file")
            print()
            return False
        
        # Extract bucket name
        if output_location.startswith('s3://'):
            bucket_name = output_location.replace('s3://', '').split('/')[0]
        else:
            print("✗ ATHENA_OUTPUT_LOCATION must start with 's3://'")
            print()
            return False
        
        s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✓ S3 bucket '{bucket_name}' is accessible")
            print(f"  Output location: {output_location}")
            print()
            return True
        except:
            print(f"✗ S3 bucket '{bucket_name}' not accessible")
            print("  Make sure the bucket exists and you have permissions")
            print()
            return False
            
    except Exception as e:
        print(f"✗ Error checking Athena output location: {str(e)}")
        print()
        return False


def main():
    print("\n" + "=" * 60)
    print("Text-to-SQL Agent Setup Verification")
    print("=" * 60 + "\n")
    
    checks = [
        ("Environment Variables", check_environment),
        ("AWS Credentials", check_aws_credentials),
        ("Glue Database", check_glue_database),
        ("Athena Output Location", check_athena_output),
        ("Bedrock Access", check_bedrock_access),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Unexpected error in {name}: {str(e)}\n")
            results[name] = False
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to use the agent.")
        print("\nRun: py example.py")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Edit .env file with correct values")
        print("- Run: py configure_aws.py (to set AWS credentials)")
        print("- Enable Bedrock model access in AWS Console")
        print("- Create Glue database: py setup_glue_sample.py")
    
    print()


if __name__ == "__main__":
    main()
