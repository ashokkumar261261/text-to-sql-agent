#!/usr/bin/env python3
"""
Complete setup script to create a Glue Catalog database with sample tables and data
for testing the Text-to-SQL agent.
"""

import boto3
import os
import csv
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def get_or_create_s3_bucket():
    """Get S3 bucket name or create one if needed."""
    s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    
    # Try to get bucket from env
    athena_location = os.getenv('ATHENA_OUTPUT_LOCATION', '')
    if athena_location.startswith('s3://'):
        bucket_name = athena_location.replace('s3://', '').split('/')[0]
        
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✓ Using existing S3 bucket: {bucket_name}")
            return bucket_name
        except:
            pass
    
    # Create a new bucket
    account_id = boto3.client('sts').get_caller_identity()['Account']
    bucket_name = f"text-to-sql-agent-{account_id}"
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"✓ Created S3 bucket: {bucket_name}")
        return bucket_name
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"✓ Using existing S3 bucket: {bucket_name}")
        return bucket_name
    except Exception as e:
        print(f"✗ Error creating bucket: {str(e)}")
        raise


def generate_sample_data():
    """Generate sample CSV data for testing."""
    
    # Sample customers data
    customers_data = [
        ['customer_id', 'name', 'email', 'city', 'state', 'signup_date'],
        [1, 'John Smith', 'john.smith@email.com', 'New York', 'NY', '2023-01-15'],
        [2, 'Jane Doe', 'jane.doe@email.com', 'Los Angeles', 'CA', '2023-02-20'],
        [3, 'Bob Johnson', 'bob.j@email.com', 'Chicago', 'IL', '2023-03-10'],
        [4, 'Alice Williams', 'alice.w@email.com', 'Houston', 'TX', '2023-04-05'],
        [5, 'Charlie Brown', 'charlie.b@email.com', 'Phoenix', 'AZ', '2023-05-12'],
        [6, 'Diana Prince', 'diana.p@email.com', 'Philadelphia', 'PA', '2023-06-18'],
        [7, 'Eve Davis', 'eve.d@email.com', 'San Antonio', 'TX', '2023-07-22'],
        [8, 'Frank Miller', 'frank.m@email.com', 'San Diego', 'CA', '2023-08-30'],
        [9, 'Grace Lee', 'grace.l@email.com', 'Dallas', 'TX', '2023-09-14'],
        [10, 'Henry Wilson', 'henry.w@email.com', 'San Jose', 'CA', '2023-10-25']
    ]
    
    # Sample orders data
    orders_data = [
        ['order_id', 'customer_id', 'product_name', 'category', 'quantity', 'price', 'total_amount', 'order_date', 'status'],
        [1001, 1, 'Laptop Pro', 'Electronics', 1, 1299.99, 1299.99, '2024-01-10', 'Delivered'],
        [1002, 2, 'Wireless Mouse', 'Electronics', 2, 29.99, 59.98, '2024-01-12', 'Delivered'],
        [1003, 3, 'Office Chair', 'Furniture', 1, 299.99, 299.99, '2024-01-15', 'Delivered'],
        [1004, 1, 'USB-C Cable', 'Electronics', 3, 12.99, 38.97, '2024-01-18', 'Delivered'],
        [1005, 4, 'Standing Desk', 'Furniture', 1, 599.99, 599.99, '2024-01-20', 'Shipped'],
        [1006, 5, 'Mechanical Keyboard', 'Electronics', 1, 149.99, 149.99, '2024-01-22', 'Delivered'],
        [1007, 2, 'Monitor 27inch', 'Electronics', 2, 349.99, 699.98, '2024-01-25', 'Delivered'],
        [1008, 6, 'Desk Lamp', 'Furniture', 1, 45.99, 45.99, '2024-01-28', 'Delivered'],
        [1009, 7, 'Webcam HD', 'Electronics', 1, 89.99, 89.99, '2024-02-01', 'Processing'],
        [1010, 3, 'Ergonomic Mouse Pad', 'Electronics', 2, 19.99, 39.98, '2024-02-03', 'Delivered'],
        [1011, 8, 'Laptop Stand', 'Electronics', 1, 39.99, 39.99, '2024-02-05', 'Delivered'],
        [1012, 9, 'Bookshelf', 'Furniture', 1, 179.99, 179.99, '2024-02-08', 'Shipped'],
        [1013, 4, 'Headphones', 'Electronics', 1, 199.99, 199.99, '2024-02-10', 'Delivered'],
        [1014, 10, 'Desk Organizer', 'Furniture', 3, 24.99, 74.97, '2024-02-12', 'Delivered'],
        [1015, 5, 'External SSD 1TB', 'Electronics', 1, 129.99, 129.99, '2024-02-15', 'Delivered']
    ]
    
    # Sample products data
    products_data = [
        ['product_id', 'product_name', 'category', 'price', 'stock', 'supplier'],
        [101, 'Laptop Pro', 'Electronics', 1299.99, 45, 'TechCorp'],
        [102, 'Wireless Mouse', 'Electronics', 29.99, 200, 'TechCorp'],
        [103, 'Office Chair', 'Furniture', 299.99, 30, 'FurniturePlus'],
        [104, 'USB-C Cable', 'Electronics', 12.99, 500, 'TechCorp'],
        [105, 'Standing Desk', 'Furniture', 599.99, 15, 'FurniturePlus'],
        [106, 'Mechanical Keyboard', 'Electronics', 149.99, 80, 'TechCorp'],
        [107, 'Monitor 27inch', 'Electronics', 349.99, 60, 'TechCorp'],
        [108, 'Desk Lamp', 'Furniture', 45.99, 100, 'FurniturePlus'],
        [109, 'Webcam HD', 'Electronics', 89.99, 75, 'TechCorp'],
        [110, 'Ergonomic Mouse Pad', 'Electronics', 19.99, 150, 'TechCorp'],
        [111, 'Laptop Stand', 'Electronics', 39.99, 90, 'TechCorp'],
        [112, 'Bookshelf', 'Furniture', 179.99, 25, 'FurniturePlus'],
        [113, 'Headphones', 'Electronics', 199.99, 65, 'TechCorp'],
        [114, 'Desk Organizer', 'Furniture', 24.99, 120, 'FurniturePlus'],
        [115, 'External SSD 1TB', 'Electronics', 129.99, 55, 'TechCorp']
    ]
    
    return {
        'customers': customers_data,
        'orders': orders_data,
        'products': products_data
    }


def upload_sample_data_to_s3(bucket_name):
    """Upload sample CSV data to S3."""
    s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    
    sample_data = generate_sample_data()
    
    for table_name, data in sample_data.items():
        # Convert to CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(data)
        
        # Upload to S3
        key = f'sample-data/{table_name}/{table_name}.csv'
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        print(f"✓ Uploaded sample data: s3://{bucket_name}/{key}")
    
    return bucket_name


def create_glue_database():
    """Create a Glue database."""
    glue = boto3.client('glue', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    database_name = 'text_to_sql_demo'
    
    try:
        glue.create_database(
            DatabaseInput={
                'Name': database_name,
                'Description': 'Demo database for Text-to-SQL agent with sample e-commerce data'
            }
        )
        print(f"✓ Created Glue database: {database_name}")
    except glue.exceptions.AlreadyExistsException:
        print(f"✓ Glue database already exists: {database_name}")
    except Exception as e:
        print(f"✗ Error creating database: {str(e)}")
        raise
    
    return database_name


def create_glue_tables(database_name, bucket_name):
    """Create Glue tables for sample data."""
    glue = boto3.client('glue', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    
    tables = {
        'customers': {
            'Description': 'Customer information',
            'Columns': [
                {'Name': 'customer_id', 'Type': 'bigint', 'Comment': 'Unique customer identifier'},
                {'Name': 'name', 'Type': 'string', 'Comment': 'Customer full name'},
                {'Name': 'email', 'Type': 'string', 'Comment': 'Customer email address'},
                {'Name': 'city', 'Type': 'string', 'Comment': 'Customer city'},
                {'Name': 'state', 'Type': 'string', 'Comment': 'Customer state'},
                {'Name': 'signup_date', 'Type': 'date', 'Comment': 'Account signup date'}
            ],
            'Location': f's3://{bucket_name}/sample-data/customers/'
        },
        'orders': {
            'Description': 'Order transactions',
            'Columns': [
                {'Name': 'order_id', 'Type': 'bigint', 'Comment': 'Unique order identifier'},
                {'Name': 'customer_id', 'Type': 'bigint', 'Comment': 'Customer who placed the order'},
                {'Name': 'product_name', 'Type': 'string', 'Comment': 'Product name'},
                {'Name': 'category', 'Type': 'string', 'Comment': 'Product category'},
                {'Name': 'quantity', 'Type': 'int', 'Comment': 'Quantity ordered'},
                {'Name': 'price', 'Type': 'decimal(10,2)', 'Comment': 'Unit price'},
                {'Name': 'total_amount', 'Type': 'decimal(10,2)', 'Comment': 'Total order amount'},
                {'Name': 'order_date', 'Type': 'date', 'Comment': 'Order date'},
                {'Name': 'status', 'Type': 'string', 'Comment': 'Order status'}
            ],
            'Location': f's3://{bucket_name}/sample-data/orders/'
        },
        'products': {
            'Description': 'Product catalog',
            'Columns': [
                {'Name': 'product_id', 'Type': 'bigint', 'Comment': 'Unique product identifier'},
                {'Name': 'product_name', 'Type': 'string', 'Comment': 'Product name'},
                {'Name': 'category', 'Type': 'string', 'Comment': 'Product category'},
                {'Name': 'price', 'Type': 'decimal(10,2)', 'Comment': 'Product price'},
                {'Name': 'stock', 'Type': 'int', 'Comment': 'Available stock'},
                {'Name': 'supplier', 'Type': 'string', 'Comment': 'Supplier name'}
            ],
            'Location': f's3://{bucket_name}/sample-data/products/'
        }
    }
    
    for table_name, table_config in tables.items():
        table_input = {
            'Name': table_name,
            'Description': table_config['Description'],
            'StorageDescriptor': {
                'Columns': table_config['Columns'],
                'Location': table_config['Location'],
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                    'Parameters': {
                        'field.delim': ',',
                        'skip.header.line.count': '1'
                    }
                }
            },
            'TableType': 'EXTERNAL_TABLE'
        }
        
        try:
            glue.create_table(
                DatabaseName=database_name,
                TableInput=table_input
            )
            print(f"✓ Created table: {table_name}")
        except glue.exceptions.AlreadyExistsException:
            print(f"✓ Table already exists: {table_name}")
        except Exception as e:
            print(f"✗ Error creating table {table_name}: {str(e)}")


def update_env_file(database_name, bucket_name):
    """Update .env file with the new configuration."""
    env_path = '.env'
    
    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update values
    updated_lines = []
    for line in lines:
        if line.startswith('GLUE_DATABASE='):
            updated_lines.append(f'GLUE_DATABASE={database_name}\n')
        elif line.startswith('ATHENA_OUTPUT_LOCATION='):
            updated_lines.append(f'ATHENA_OUTPUT_LOCATION=s3://{bucket_name}/athena-results/\n')
        else:
            updated_lines.append(line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✓ Updated .env file with database and bucket information")


def main():
    print("\n" + "="*70)
    print("Setting up Complete Glue Catalog Environment for Text-to-SQL Agent")
    print("="*70 + "\n")
    
    try:
        # Step 1: Get or create S3 bucket
        print("Step 1: Setting up S3 bucket...")
        bucket_name = get_or_create_s3_bucket()
        print()
        
        # Step 2: Upload sample data
        print("Step 2: Uploading sample data to S3...")
        upload_sample_data_to_s3(bucket_name)
        print()
        
        # Step 3: Create Glue database
        print("Step 3: Creating Glue database...")
        database_name = create_glue_database()
        print()
        
        # Step 4: Create Glue tables
        print("Step 4: Creating Glue tables...")
        create_glue_tables(database_name, bucket_name)
        print()
        
        # Step 5: Update .env file
        print("Step 5: Updating .env file...")
        update_env_file(database_name, bucket_name)
        print()
        
        # Summary
        print("="*70)
        print("✅ Setup Complete!")
        print("="*70)
        print(f"\nGlue Database: {database_name}")
        print(f"S3 Bucket: {bucket_name}")
        print(f"\nTables created:")
        print("  - customers (10 records)")
        print("  - orders (15 records)")
        print("  - products (15 records)")
        print(f"\nSample queries you can try:")
        print('  - "Show me all customers from Texas"')
        print('  - "What are the top 5 products by price?"')
        print('  - "Count total orders by status"')
        print('  - "List all orders with total amount over $500"')
        print('  - "Show me customers who ordered Electronics"')
        print(f"\nNext steps:")
        print("  1. Run: .\\run.bat test_setup.py")
        print("  2. Run: .\\run.bat example.py")
        print()
        
    except Exception as e:
        print(f"\n✗ Setup failed: {str(e)}")
        print("\nMake sure you have:")
        print("  - AWS credentials configured")
        print("  - Proper IAM permissions for S3, Glue, and Athena")
        raise


if __name__ == "__main__":
    main()
