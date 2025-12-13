import boto3
import json
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from .agent import TextToSQLAgent
from .knowledge_base import BedrockKnowledgeBase
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class EnhancedTextToSQLAgent(TextToSQLAgent):
    """
    Enhanced Text-to-SQL Agent with Bedrock Knowledge Base integration.
    Provides domain-specific context, business rules, and intelligent query suggestions.
    """
    
    def __init__(self, session_id: str = None, enable_cache: bool = True, enable_knowledge_base: bool = True):
        super().__init__(session_id=session_id, enable_cache=enable_cache)
        
        # Initialize knowledge base if enabled
        self.knowledge_base = None
        if enable_knowledge_base:
            try:
                self.knowledge_base = BedrockKnowledgeBase()
                logger.info("Knowledge base integration enabled")
            except Exception as e:
                logger.warning(f"Knowledge base initialization failed: {str(e)}")
    
    def query(self, natural_language_query: str, execute: bool = False, 
              include_sample_data: bool = False, explain: bool = False,
              use_cache: bool = True, validate: bool = True, 
              use_knowledge_base: bool = True) -> Dict[str, Any]:
        """
        Enhanced query method with knowledge base integration.
        
        Args:
            natural_language_query: The user's question in natural language
            execute: Whether to execute the generated SQL query
            include_sample_data: Include sample data in schema context
            explain: Generate explanation of the SQL query
            use_cache: Use cached results if available
            validate: Validate query before execution
            use_knowledge_base: Use knowledge base for enhanced context
            
        Returns:
            Dictionary containing SQL query, results, validation, explanation, and KB insights
        """
        try:
            # Add user query to conversation history
            self.conversation.add_message('user', natural_language_query)
            
            # Enhance query with conversation context
            enhanced_query = self.conversation.enhance_query_with_context(natural_language_query)
            
            # Get base schema context
            schema_context = self.schema_manager.get_schema_context(
                include_sample_data=include_sample_data
            )
            
            # Enhance with knowledge base if available
            if use_knowledge_base and self.knowledge_base:
                schema_context = self.knowledge_base.get_enhanced_context(
                    enhanced_query, schema_context
                )
            
            # Add conversation context
            conv_context = self.conversation.get_context()
            if conv_context:
                schema_context = f"{schema_context}\n\n{conv_context}"
            
            # Generate SQL using enhanced context
            sql_query = self._generate_sql(enhanced_query, schema_context)
            
            result = {
                'natural_language_query': natural_language_query,
                'sql_query': sql_query,
                'executed': execute,
                'database': self.athena_manager.database,
                'cached': False,
                'knowledge_base_used': use_knowledge_base and self.knowledge_base is not None
            }
            
            # Add knowledge base insights
            if use_knowledge_base and self.knowledge_base:
                kb_insights = self._get_knowledge_base_insights(natural_language_query, sql_query)
                result['knowledge_base_insights'] = kb_insights
            
            # Validate query (including business rules if KB is available)
            if validate:
                validation_result = self._enhanced_validation(sql_query, natural_language_query, use_knowledge_base)
                result['validation'] = validation_result
                result['query_info'] = self.validator.get_query_info(sql_query)
                
                if not validation_result['is_valid']:
                    result['error'] = f"Query validation failed: {validation_result['error']}"
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
            error_message = str(e)
            
            # Provide more helpful error messages
            if "GLUE_DATABASE" in error_message or "database" in error_message.lower():
                error_message = f"Database configuration error: {error_message}. Please check your GLUE_DATABASE and ATHENA_OUTPUT_LOCATION in .env file."
            elif "credentials" in error_message.lower():
                error_message = f"AWS credentials error: {error_message}. Please check your AWS configuration."
            elif "bedrock" in error_message.lower():
                error_message = f"Bedrock error: {error_message}. Please check your Bedrock permissions and model access."
            
            error_result = {
                'error': error_message,
                'natural_language_query': natural_language_query,
                'knowledge_base_used': use_knowledge_base and self.knowledge_base is not None,
                'sql_query': None,  # Add this to prevent KeyError
                'executed': False
            }
            self.conversation.add_message('assistant', '', metadata={'error': str(e)})
            return error_result
    
    def get_query_suggestions(self, partial_query: str = None) -> List[str]:
        """
        Get intelligent query suggestions based on knowledge base and conversation history.
        
        Args:
            partial_query: Optional partial query for context
            
        Returns:
            List of suggested queries
        """
        suggestions = []
        
        # Get suggestions from knowledge base
        if self.knowledge_base:
            if partial_query:
                kb_suggestions = self.knowledge_base.get_query_suggestions(partial_query)
                suggestions.extend(kb_suggestions)
            else:
                # Get general suggestions based on conversation history
                recent_queries = self.conversation.get_recent_queries(limit=3)
                for query in recent_queries:
                    kb_suggestions = self.knowledge_base.get_query_suggestions(query)
                    suggestions.extend(kb_suggestions[:2])  # Limit per query
        
        # Add default suggestions if none from KB
        if not suggestions:
            suggestions = [
                "Show me all customers from Texas",
                "What are the top 5 products by price?",
                "Count total orders by status",
                "List customers who ordered Electronics",
                "Calculate total revenue by category this month"
            ]
        
        return list(set(suggestions))  # Remove duplicates
    
    def analyze_query_intent(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Analyze the intent and complexity of a natural language query.
        
        Args:
            natural_language_query: User's natural language query
            
        Returns:
            Analysis of query intent, complexity, and recommendations
        """
        analysis = {
            'query': natural_language_query,
            'intent_type': 'unknown',
            'complexity': 'low',
            'tables_likely_needed': [],
            'business_context': [],
            'recommendations': []
        }
        
        query_lower = natural_language_query.lower()
        
        # Determine intent type
        if any(word in query_lower for word in ['show', 'list', 'display', 'get']):
            analysis['intent_type'] = 'retrieval'
        elif any(word in query_lower for word in ['count', 'sum', 'total', 'average', 'calculate']):
            analysis['intent_type'] = 'aggregation'
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            analysis['intent_type'] = 'comparison'
        elif any(word in query_lower for word in ['trend', 'over time', 'monthly', 'yearly']):
            analysis['intent_type'] = 'temporal_analysis'
        
        # Determine complexity
        complexity_indicators = ['join', 'group by', 'having', 'subquery', 'multiple tables']
        if any(indicator in query_lower for indicator in complexity_indicators):
            analysis['complexity'] = 'high'
        elif any(word in query_lower for word in ['top', 'best', 'most', 'least']):
            analysis['complexity'] = 'medium'
        
        # Identify likely tables needed
        if 'customer' in query_lower:
            analysis['tables_likely_needed'].append('customers')
        if any(word in query_lower for word in ['order', 'purchase', 'buy']):
            analysis['tables_likely_needed'].append('orders')
        if 'product' in query_lower:
            analysis['tables_likely_needed'].append('products')
        
        # Get business context from knowledge base
        if self.knowledge_base:
            kb_results = self.knowledge_base.query_knowledge_base(natural_language_query)
            for result in kb_results[:3]:
                analysis['business_context'].append({
                    'content': result['content'][:200] + '...',  # Truncate for summary
                    'confidence': result['confidence']
                })
        
        # Generate recommendations
        if analysis['complexity'] == 'high':
            analysis['recommendations'].append("This query may require multiple tables and complex joins")
        if not analysis['tables_likely_needed']:
            analysis['recommendations'].append("Consider specifying which data you're interested in (customers, orders, products)")
        
        return analysis
    
    def _enhanced_validation(self, sql_query: str, natural_language_query: str, use_knowledge_base: bool) -> Dict[str, Any]:
        """
        Enhanced validation including business rules from knowledge base.
        """
        # Start with standard validation
        is_valid, error_msg, warnings = self.validator.validate(sql_query)
        
        validation_result = {
            'is_valid': is_valid,
            'error': error_msg,
            'warnings': warnings,
            'business_rule_compliance': None
        }
        
        # Add business rule validation if knowledge base is available
        if use_knowledge_base and self.knowledge_base and is_valid:
            business_validation = self.knowledge_base.validate_business_rules(
                sql_query, natural_language_query
            )
            validation_result['business_rule_compliance'] = business_validation
            
            # Add business rule warnings to main warnings
            if business_validation['warnings']:
                validation_result['warnings'].extend(business_validation['warnings'])
        
        return validation_result
    
    def _get_knowledge_base_insights(self, natural_language_query: str, sql_query: str) -> Dict[str, Any]:
        """
        Get insights from knowledge base about the query.
        """
        insights = {
            'relevant_context': [],
            'similar_queries': [],
            'business_rules': [],
            'optimization_tips': []
        }
        
        if not self.knowledge_base:
            return insights
        
        # Get relevant context
        kb_results = self.knowledge_base.query_knowledge_base(natural_language_query)
        for result in kb_results[:3]:
            insights['relevant_context'].append({
                'content': result['content'],
                'confidence': result['confidence'],
                'source': result.get('metadata', {})
            })
        
        # Get similar queries
        similar_queries = self.knowledge_base.get_query_suggestions(natural_language_query)
        insights['similar_queries'] = similar_queries[:3]
        
        # Get business rules validation
        business_validation = self.knowledge_base.validate_business_rules(sql_query, natural_language_query)
        insights['business_rules'] = business_validation.get('applicable_rules', [])
        
        return insights
    
    def get_knowledge_base_status(self) -> Dict[str, Any]:
        """
        Get status and configuration of the knowledge base.
        """
        if not self.knowledge_base:
            return {'enabled': False, 'reason': 'Knowledge base not initialized'}
        
        return {
            'enabled': True,
            'knowledge_base_id': self.knowledge_base.knowledge_base_id,
            'model_id': self.knowledge_base.model_id,
            'max_results': self.knowledge_base.max_results,
            'confidence_threshold': self.knowledge_base.confidence_threshold
        }