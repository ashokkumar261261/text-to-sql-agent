#!/usr/bin/env python3
"""
Simple check if the database exists and is accessible.
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def check_database_exists():
    """Check if the Glue database exists."""
    
    print("🔍 Checking Database Configuration")
    print("=" * 40)
    
    try:
        # Get configuration
        region = os.getenv('AWS_REGION', 'us-east-1')
        database = os.getenv('GLUE_DATABASE', 'text_to_sql_demo')
        
        print(f"Region: {region}")
        print(f"Database: {database}")
        
        # Check Glue client
        glue_client = boto3.client('glue', region_name=region)
        
        print(f"\n📋 Checking if database '{database}' exists...")
        
        try:
            response = glue_client.get_database(Name=database)
            print(f"✅ Database found: {response['Database']['Name']}")
            print(f"   Description: {response['Database'].get('Description', 'No description')}")
            
            # List tables
            print(f"\n📊 Checking tables in database...")
            tables_response = glue_client.get_tables(DatabaseName=database)
            tables = [table['Name'] for table in tables_response['TableList']]
            
            if tables:
                print(f"✅ Found {len(tables)} tables: {tables}")
                
                # Check if customers table exists
                if 'customers' in tables:
                    print(f"✅ 'customers' table found - this is what we need!")
                else:
                    print(f"⚠️  'customers' table not found. Available tables: {tables}")
            else:
                print(f"⚠️  No tables found in database '{database}'")
            
            return True
            
        except glue_client.exceptions.EntityNotFoundException:
            print(f"❌ Database '{database}' does not exist")
            print(f"\n💡 Solutions:")
            print(f"1. Create the database in AWS Glue Catalog")
            print(f"2. Or change GLUE_DATABASE in .env to an existing database")
            print(f"3. Or run the sample data setup script")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def suggest_solutions():
    """Suggest solutions for database issues."""
    
    print(f"\n🛠️  Possible Solutions:")
    print(f"=" * 30)
    
    print(f"1. 📊 Create sample data:")
    print(f"   python setup_glue_sample.py")
    
    print(f"\n2. 🔧 Use existing database:")
    print(f"   - Check AWS Glue Catalog for existing databases")
    print(f"   - Update GLUE_DATABASE in .env file")
    
    print(f"\n3. 🎯 For testing without real data:")
    print(f"   - Use execute=False in queries (SQL generation only)")
    print(f"   - Focus on Knowledge Base and SQL generation features")

if __name__ == "__main__":
    exists = check_database_exists()
    
    if not exists:
        suggest_solutions()
    else:
        print(f"\n🎉 Database configuration looks good!")
        print(f"The issue might be with Athena permissions or query execution.")