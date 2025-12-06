#!/usr/bin/env python3
"""
Helper script to configure AWS credentials without using AWS CLI
"""

import os
from pathlib import Path


def configure_aws_credentials():
    """Configure AWS credentials by creating/updating credentials file."""
    
    print("AWS Credentials Configuration")
    print("=" * 50)
    print()
    
    # Get credentials from user
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    region = input("Default region name [us-east-1]: ").strip() or "us-east-1"
    
    # Create .aws directory if it doesn't exist
    aws_dir = Path.home() / ".aws"
    aws_dir.mkdir(exist_ok=True)
    
    # Write credentials file
    credentials_file = aws_dir / "credentials"
    with open(credentials_file, "w") as f:
        f.write("[default]\n")
        f.write(f"aws_access_key_id = {access_key}\n")
        f.write(f"aws_secret_access_key = {secret_key}\n")
    
    print(f"\n✓ Credentials saved to: {credentials_file}")
    
    # Write config file
    config_file = aws_dir / "config"
    with open(config_file, "w") as f:
        f.write("[default]\n")
        f.write(f"region = {region}\n")
        f.write("output = json\n")
    
    print(f"✓ Config saved to: {config_file}")
    
    print("\n" + "=" * 50)
    print("AWS credentials configured successfully!")
    print("\nYou can now use boto3 to access AWS services.")
    print("\nNext steps:")
    print("1. Edit .env file with your Glue database and Athena settings")
    print("2. Run: py example.py")


def test_credentials():
    """Test if AWS credentials are working."""
    try:
        import boto3
        
        print("\nTesting AWS credentials...")
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"\n✓ Credentials are valid!")
        print(f"  Account: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing credentials: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        configure_aws_credentials()
        
        # Ask if user wants to test
        test = input("\nTest credentials now? (y/n): ").strip().lower()
        if test == 'y':
            test_credentials()
            
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
