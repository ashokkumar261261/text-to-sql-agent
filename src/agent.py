import boto3
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .database import AthenaManager
from .schema import SchemaManager
from .query_validator import QueryValidator
from .query_cache import QueryCache
from .conversation import ConversationHistory

load_dotenv()


class TextToSQLAgent:
    """Enhanced agent for converting natural language to SQL queries with validation, caching, and conversation history."""
    
    def __init__(self, session_id: str = None, enable_cache: bool = True):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=self.region)
        self.athena_manager = AthenaManager()
        self.schema_manager = SchemaManager()
        
        # New features
        self.validator = QueryValidator()
        self.cache = QueryCache() if enable_cache else None
        self.conversation = ConversationHistory(session_id=session_id)
    
    def query(self, natural_language_query: str, execute: bool = False, 
              include_sample_data: bool = False, explain: bool = False,
              use_cache: bool = True, validate: bool = True) -> Dict[str, Any]:
        """
        Convert natural language to SQL and optionally execute it on Athena.
        
        Args:
            natural_language_query: The user's question in natural language
            execute: Whether to execute the generated SQL query
            include_sample_data: Include sample data in schema context for better SQL generation
            explain: Generate explanation of the SQL query
            use_cache: Use cached results if available
            validate: Validate query before execution
            
        Returns:
            Dictionary containing SQL query, results, validation, and explanation
        """
        try:
            # Add user query to conversation history
            self.conversation.add_message('user', natural_language_query)
            
            # Enhance query with conversation context
            enhanced_query = self.conversation.enhance_query_with_context(natural_language_query)
            
            # Get Glue Catalog schema context
            schema_context = self.schema_manager.get_schema_context(
                include_sample_data=include_sample_data
            )
            
            # Add conversation context to schema
            conv_context = self.conversation.get_context()
            if conv_context:
                schema_context = f"{schema_context}\n\n{conv_context}"
            
            # Generate SQL using Bedrock
            sql_query = self._generate_sql(enhanced_query, schema_context)
            
            result = {
                'natural_language_query': natural_language_query,
                'sql_query': sql_query,
                'executed': execute,
                'database': self.athena_manager.database,
                'cached': False
            }
            
            # Validate query
            if validate:
                is_valid, error_msg, warnings = self.validator.validate(sql_query)
                result['validation'] = {
                    'is_valid': is_valid,
                    'error': error_msg,
                    'warnings': warnings
                }
                result['query_info'] = self.validator.get_query_info(sql_query)
                
                if not is_valid:
                    result['error'] = f"Query validation failed: {error_msg}"
                    self.conversation.add_message('assistant', '', sql_query=sql_query, 
                                                metadata={'validation_failed': True})
                    return result
            
            # Generate explanation if requested
            if explain:
                result['explanation'] = self._explain_query(sql_query, natural_language_query)
            
            # Execute query if requested
            if execute:
                # Check cache first
                if use_cache and self.cache:
                    cached_results = self.cache.get(sql_query, self.athena_manager.database)
                    if cached_results is not None:
                        result['results'] = cached_results
                        result['row_count'] = len(cached_results)
                        result['cached'] = True
                        self.conversation.add_message('assistant', '', sql_query=sql_query,
                                                    results=cached_results, 
                                                    metadata={'cached': True})
                        return result
                
                # Execute query
                query_results = self.athena_manager.execute_query(sql_query)
                result['results'] = query_results
                result['row_count'] = len(query_results)
                
                # Cache results
                if self.cache:
                    self.cache.set(sql_query, query_results, self.athena_manager.database)
                
                # Add to conversation history
                self.conversation.add_message('assistant', '', sql_query=sql_query,
                                            results=query_results)
            else:
                # Just add SQL to history
                self.conversation.add_message('assistant', '', sql_query=sql_query)
            
            return result
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'natural_language_query': natural_language_query
            }
            self.conversation.add_message('assistant', '', metadata={'error': str(e)})
            return error_result
    
    def query_async(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Convert natural language to SQL and execute it asynchronously.
        
        Args:
            natural_language_query: The user's question in natural language
            
        Returns:
            Dictionary containing SQL query and query execution ID
        """
        try:
            schema_context = self.schema_manager.get_schema_context()
            sql_query = self._generate_sql(natural_language_query, schema_context)
            
            # Execute query asynchronously
            query_execution_id = self.athena_manager.execute_query_async(sql_query)
            
            return {
                'natural_language_query': natural_language_query,
                'sql_query': sql_query,
                'query_execution_id': query_execution_id,
                'database': self.athena_manager.database
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'natural_language_query': natural_language_query
            }
    
    def get_query_results(self, query_execution_id: str) -> Dict[str, Any]:
        """
        Get results from an async query execution.
        
        Args:
            query_execution_id: The query execution ID from query_async
            
        Returns:
            Dictionary containing query results
        """
        try:
            results = self.athena_manager.get_query_results(query_execution_id)
            
            return {
                'query_execution_id': query_execution_id,
                'results': results,
                'row_count': len(results)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'query_execution_id': query_execution_id
            }
    
    def _generate_sql(self, query: str, schema_context: str) -> str:
        """Generate SQL query using Amazon Bedrock (supports Claude and Titan)."""
        
        database_name = self.athena_manager.database
        
        prompt = f"""You are an AWS Athena SQL expert. Convert the following natural language query into a valid Athena SQL statement.

Important Athena SQL Guidelines:
- Use Presto/Trino SQL syntax (Athena's query engine)
- ALWAYS use fully qualified table names: {database_name}.table_name
- For date operations, use date_parse() or from_iso8601_timestamp()
- Use CAST() for type conversions
- Partition columns should be used in WHERE clauses when possible for better performance
- String literals use single quotes
- Use appropriate aggregate functions: COUNT, SUM, AVG, MIN, MAX
- For JSON data, use json_extract() or json_extract_scalar()

Database: {database_name}

Glue Catalog Schema:
{schema_context}

Natural Language Query: {query}

IMPORTANT: Use fully qualified table names like {database_name}.customers, {database_name}.orders, etc.

Generate ONLY the SQL query without any explanation. The query should be valid Athena SQL and executable.

SQL Query:"""

        # Check if using Titan or Claude
        if 'titan' in self.model_id.lower():
            # Amazon Titan API format
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 1000,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            })
        else:
            # Claude API format
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1
            })
        
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract SQL based on model type
        if 'titan' in self.model_id.lower():
            sql_query = response_body['results'][0]['outputText'].strip()
        else:
            sql_query = response_body['content'][0]['text'].strip()
        
        # Clean up the SQL query
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        return sql_query

    def _explain_query(self, sql_query: str, natural_language_query: str) -> str:
        """Generate an explanation of the SQL query."""
        
        prompt = f"""Explain the following SQL query in simple terms. Describe what it does and how it answers the user's question.

User's Question: {natural_language_query}

SQL Query:
{sql_query}

Provide a clear, concise explanation that a non-technical person can understand."""

        # Check if using Titan or Claude
        if 'titan' in self.model_id.lower():
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.3
                }
            })
        else:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3
            })
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract explanation based on model type
            if 'titan' in self.model_id.lower():
                explanation = response_body['results'][0]['outputText'].strip()
            else:
                explanation = response_body['content'][0]['text'].strip()
            
            return explanation
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of the current conversation."""
        return self.conversation.get_summary()
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        if self.cache:
            return self.cache.get_stats()
        return {'enabled': False}
    
    def clear_cache(self):
        """Clear query cache."""
        if self.cache:
            self.cache.invalidate()
