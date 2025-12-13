#!/usr/bin/env python3
"""
Test Athena connection and database setup.
"""

from src.database import AthenaManager
from src.schema import SchemaManager

def test_athena_connection():
    """Test if Athena connection is working."""
    
    print("🧪 Testing Athena Connection")
    print("=" * 40)
    
    try:
        # Test Athena Manager
        athena = AthenaManager()
        print(f"✅ Athena Manager initialized")
        print(f"   Database: {athena.database}")
        print(f"   Output Location: {athena.output_location}")
        print(f"   Workgroup: {athena.workgroup}")
        
        # Test getting tables
        print(f"\n📋 Testing table listing...")
        tables = athena.get_tables()
        print(f"✅ Found {len(tables)} tables: {tables}")
        
        # Test schema for each table
        for table in tables:
            print(f"\n📊 Schema for {table}:")
            try:
                schema = athena.get_table_schema(table)
                print(f"   Columns: {len(schema['columns'])}")
                for col in schema['columns'][:3]:  # Show first 3 columns
                    print(f"     - {col['name']} ({col['type']})")
            except Exception as e:
                print(f"   ❌ Error getting schema: {e}")
        
        # Test a simple query
        print(f"\n🔍 Testing simple query...")
        test_query = f"SELECT COUNT(*) as row_count FROM {athena.database}.{tables[0]}" if tables else "SELECT 1"
        
        try:
            results = athena.execute_query(test_query)
            print(f"✅ Query executed successfully")
            print(f"   Results: {results}")
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
        
        # Test the specific query
        if 'customers' in tables:
            print(f"\n🔍 Testing Eve Davis query...")
            eve_query = f"SELECT c.email FROM {athena.database}.customers c WHERE c.name = 'Eve Davis'"
            try:
                results = athena.execute_query(eve_query)
                print(f"✅ Eve Davis query executed")
                print(f"   Results: {results}")
            except Exception as e:
                print(f"❌ Eve Davis query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Athena connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_manager():
    """Test Schema Manager."""
    
    print(f"\n📋 Testing Schema Manager")
    print("-" * 30)
    
    try:
        schema_manager = SchemaManager()
        
        # Get schema context
        context = schema_manager.get_schema_context(include_sample_data=True)
        print(f"✅ Schema context generated")
        print(f"   Length: {len(context)} characters")
        print(f"   Preview: {context[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema Manager failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Athena Connection Test")
    print("=" * 50)
    
    athena_ok = test_athena_connection()
    schema_ok = test_schema_manager()
    
    print(f"\n📊 Test Results:")
    print(f"   Athena Connection: {'✅ PASS' if athena_ok else '❌ FAIL'}")
    print(f"   Schema Manager: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    
    if athena_ok and schema_ok:
        print(f"\n🎉 All tests passed! Your Athena setup is working.")
    else:
        print(f"\n⚠️  Some tests failed. Check the configuration above.")