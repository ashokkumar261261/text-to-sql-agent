import os
import boto3
import time
from typing import List, Dict, Any
from pyathena import connect
from pyathena.pandas.cursor import PandasCursor
from dotenv import load_dotenv

load_dotenv()


class AthenaManager:
    """Manages AWS Athena connections and query execution for S3 data lake."""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.database = os.getenv('GLUE_DATABASE')
        self.output_location = os.getenv('ATHENA_OUTPUT_LOCATION')
        self.workgroup = os.getenv('ATHENA_WORKGROUP', 'primary')
        
        if not self.database:
            raise ValueError("GLUE_DATABASE environment variable is required")
        if not self.output_location:
            raise ValueError("ATHENA_OUTPUT_LOCATION environment variable is required")
        
        self.athena_client = boto3.client('athena', region_name=self.region)
        self.glue_client = boto3.client('glue', region_name=self.region)
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query using Athena and return results.
        
        Args:
            sql_query: The SQL query to execute
            
        Returns:
            List of dictionaries representing query results
        """
        cursor = connect(
            s3_staging_dir=self.output_location,
            region_name=self.region,
            work_group=self.workgroup,
            cursor_class=PandasCursor
        ).cursor()
        
        # Execute query and fetch results as DataFrame
        df = cursor.execute(sql_query).as_pandas()
        
        # Convert DataFrame to list of dictionaries
        return df.to_dict('records')
    
    def execute_query_async(self, sql_query: str) -> str:
        """
        Execute a SQL query asynchronously and return the query execution ID.
        
        Args:
            sql_query: The SQL query to execute
            
        Returns:
            Query execution ID
        """
        response = self.athena_client.start_query_execution(
            QueryString=sql_query,
            QueryExecutionContext={'Database': self.database},
            ResultConfiguration={'OutputLocation': self.output_location},
            WorkGroup=self.workgroup
        )
        
        return response['QueryExecutionId']
    
    def get_query_results(self, query_execution_id: str, wait: bool = True) -> List[Dict[str, Any]]:
        """
        Get results from an async query execution.
        
        Args:
            query_execution_id: The query execution ID
            wait: Whether to wait for query completion
            
        Returns:
            List of dictionaries representing query results
        """
        if wait:
            self._wait_for_query_completion(query_execution_id)
        
        results = []
        paginator = self.athena_client.get_paginator('get_query_results')
        
        for page in paginator.paginate(QueryExecutionId=query_execution_id):
            rows = page['ResultSet']['Rows']
            
            if not results:
                # First row contains column names
                columns = [col['VarCharValue'] for col in rows[0]['Data']]
                rows = rows[1:]
            
            for row in rows:
                values = [col.get('VarCharValue', '') for col in row['Data']]
                results.append(dict(zip(columns, values)))
        
        return results
    
    def _wait_for_query_completion(self, query_execution_id: str, max_wait: int = 60):
        """Wait for query to complete."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = self.athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                if status == 'FAILED':
                    reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                    raise Exception(f"Query failed: {reason}")
                elif status == 'CANCELLED':
                    raise Exception("Query was cancelled")
                return
            
            time.sleep(1)
        
        raise TimeoutError(f"Query did not complete within {max_wait} seconds")
    
    def get_tables(self) -> List[str]:
        """Get list of all tables from Glue Catalog."""
        try:
            tables = []
            paginator = self.glue_client.get_paginator('get_tables')
            
            for page in paginator.paginate(DatabaseName=self.database):
                for table in page['TableList']:
                    tables.append(table['Name'])
            
            return tables
        except Exception as e:
            raise Exception(f"Failed to get tables from Glue Catalog: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table from Glue Catalog."""
        try:
            response = self.glue_client.get_table(
                DatabaseName=self.database,
                Name=table_name
            )
            
            table = response['Table']
            columns = []
            
            # Get regular columns
            for col in table['StorageDescriptor']['Columns']:
                columns.append({
                    'name': col['Name'],
                    'type': col['Type'],
                    'comment': col.get('Comment', '')
                })
            
            # Get partition columns if any
            partition_keys = table.get('PartitionKeys', [])
            for col in partition_keys:
                columns.append({
                    'name': col['Name'],
                    'type': col['Type'],
                    'comment': col.get('Comment', ''),
                    'partition': True
                })
            
            return {
                'table_name': table_name,
                'columns': columns,
                'location': table['StorageDescriptor'].get('Location', ''),
                'input_format': table['StorageDescriptor'].get('InputFormat', ''),
                'output_format': table['StorageDescriptor'].get('OutputFormat', '')
            }
        except Exception as e:
            raise Exception(f"Failed to get table schema from Glue Catalog: {str(e)}")
