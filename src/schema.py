from typing import Dict, List
from .database import AthenaManager


class SchemaManager:
    """Manages AWS Glue Catalog schema information for the AI agent."""
    
    def __init__(self):
        self.athena_manager = AthenaManager()
    
    def get_schema_context(self, include_sample_data: bool = False) -> str:
        """
        Generate a formatted schema context from Glue Catalog for the AI model.
        
        Args:
            include_sample_data: Whether to include sample data from tables
            
        Returns:
            Formatted string containing database schema information
        """
        try:
            tables = self.athena_manager.get_tables()
            schema_parts = []
            
            schema_parts.append(f"Database: {self.athena_manager.database}")
            schema_parts.append(f"Total Tables: {len(tables)}\n")
            
            for table in tables:
                table_schema = self.athena_manager.get_table_schema(table)
                schema_parts.append(self._format_table_schema(table_schema))
                
                if include_sample_data:
                    sample_data = self._get_sample_data(table)
                    if sample_data:
                        schema_parts.append(f"Sample Data (first 3 rows):\n{sample_data}")
            
            return "\n\n".join(schema_parts)
        
        except Exception as e:
            raise Exception(f"Failed to get schema context: {str(e)}")
    
    def _format_table_schema(self, schema: Dict) -> str:
        """Format table schema from Glue Catalog for AI consumption."""
        lines = [f"Table: {schema['table_name']}"]
        lines.append(f"Location: {schema['location']}")
        lines.append("Columns:")
        
        for column in schema['columns']:
            partition_marker = " (PARTITION KEY)" if column.get('partition') else ""
            comment = f" -- {column['comment']}" if column.get('comment') else ""
            lines.append(f"  - {column['name']} ({column['type']}){partition_marker}{comment}")
        
        return "\n".join(lines)
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> str:
        """Get sample data from a table."""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = self.athena_manager.execute_query(query)
            
            if not results:
                return "No data available"
            
            # Format as simple text representation
            lines = []
            for i, row in enumerate(results, 1):
                lines.append(f"  Row {i}: {row}")
            
            return "\n".join(lines)
        except Exception:
            return "Sample data unavailable"
    
    def get_table_info(self, table_name: str) -> Dict:
        """Get detailed information about a specific table."""
        return self.athena_manager.get_table_schema(table_name)
    
    def list_tables(self) -> List[str]:
        """Get list of all tables in the Glue database."""
        return self.athena_manager.get_tables()
