"""
Query validation module to ensure safe SQL execution
"""

import re
from typing import Dict, List, Tuple


class QueryValidator:
    """Validates SQL queries before execution."""
    
    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 
        'INSERT', 'UPDATE', 'GRANT', 'REVOKE', 'EXEC',
        'EXECUTE', 'CALL', 'MERGE'
    ]
    
    # Allowed SQL keywords for read-only queries
    ALLOWED_KEYWORDS = [
        'SELECT', 'WITH', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT',
        'INNER', 'OUTER', 'ON', 'GROUP', 'BY', 'HAVING', 'ORDER',
        'LIMIT', 'OFFSET', 'AS', 'DISTINCT', 'UNION', 'INTERSECT',
        'EXCEPT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'CAST',
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'AND', 'OR', 'NOT',
        'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL'
    ]
    
    def __init__(self, max_query_length: int = 5000):
        self.max_query_length = max_query_length
    
    def validate(self, sql_query: str) -> Tuple[bool, str, List[str]]:
        """
        Validate a SQL query for safety and correctness.
        
        Args:
            sql_query: The SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message, warnings)
        """
        warnings = []
        
        # Check if query is empty
        if not sql_query or not sql_query.strip():
            return False, "Query is empty", []
        
        # Check query length
        if len(sql_query) > self.max_query_length:
            return False, f"Query exceeds maximum length of {self.max_query_length} characters", []
        
        # Normalize query for checking
        normalized_query = sql_query.upper().strip()
        
        # Check for dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, normalized_query):
                return False, f"Dangerous operation detected: {keyword}. Only SELECT queries are allowed.", []
        
        # Check if query starts with SELECT or WITH (for CTEs)
        if not (normalized_query.startswith('SELECT') or normalized_query.startswith('WITH')):
            return False, "Query must start with SELECT or WITH (for Common Table Expressions)", []
        
        # Check for balanced parentheses
        if sql_query.count('(') != sql_query.count(')'):
            return False, "Unbalanced parentheses in query", []
        
        # Check for SQL injection patterns
        injection_patterns = [
            r';\s*DROP',
            r';\s*DELETE',
            r'--\s*$',  # SQL comments at end
            r'/\*.*\*/',  # Block comments
            r'UNION\s+ALL\s+SELECT.*FROM\s+information_schema',
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, normalized_query, re.IGNORECASE):
                warnings.append(f"Potential SQL injection pattern detected: {pattern}")
        
        # Check for missing LIMIT clause (warning only)
        if 'LIMIT' not in normalized_query and 'TOP' not in normalized_query:
            warnings.append("Query does not have a LIMIT clause. Consider adding one to prevent large result sets.")
        
        # Check for SELECT * (warning only)
        if re.search(r'SELECT\s+\*', normalized_query):
            warnings.append("Using SELECT * may return unnecessary columns. Consider specifying columns explicitly.")
        
        # All checks passed
        return True, "", warnings
    
    def suggest_limit(self, sql_query: str, default_limit: int = 1000) -> str:
        """
        Add a LIMIT clause to a query if it doesn't have one.
        
        Args:
            sql_query: The SQL query
            default_limit: Default limit to add
            
        Returns:
            Query with LIMIT clause
        """
        normalized = sql_query.upper().strip()
        
        if 'LIMIT' in normalized or 'TOP' in normalized:
            return sql_query
        
        # Add LIMIT at the end
        return f"{sql_query.rstrip(';')} LIMIT {default_limit}"
    
    def sanitize_query(self, sql_query: str) -> str:
        """
        Sanitize a SQL query by removing comments and extra whitespace.
        
        Args:
            sql_query: The SQL query to sanitize
            
        Returns:
            Sanitized query
        """
        # Remove SQL comments
        query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        return query.strip()
    
    def get_query_info(self, sql_query: str) -> Dict:
        """
        Extract information about the query.
        
        Args:
            sql_query: The SQL query
            
        Returns:
            Dictionary with query information
        """
        normalized = sql_query.upper()
        
        # Extract table names (simple pattern)
        tables = re.findall(r'FROM\s+(\w+)', normalized)
        tables.extend(re.findall(r'JOIN\s+(\w+)', normalized))
        
        # Check for aggregations
        has_aggregation = any(func in normalized for func in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX'])
        
        # Check for joins
        has_joins = 'JOIN' in normalized
        
        # Check for subqueries
        has_subquery = normalized.count('SELECT') > 1
        
        # Check for GROUP BY
        has_groupby = 'GROUP BY' in normalized
        
        return {
            'tables': list(set(tables)),
            'has_aggregation': has_aggregation,
            'has_joins': has_joins,
            'has_subquery': has_subquery,
            'has_groupby': has_groupby,
            'estimated_complexity': self._estimate_complexity(sql_query)
        }
    
    def _estimate_complexity(self, sql_query: str) -> str:
        """Estimate query complexity."""
        normalized = sql_query.upper()
        
        complexity_score = 0
        
        if 'JOIN' in normalized:
            complexity_score += normalized.count('JOIN') * 2
        if normalized.count('SELECT') > 1:
            complexity_score += 3
        if 'GROUP BY' in normalized:
            complexity_score += 2
        if any(func in normalized for func in ['COUNT', 'SUM', 'AVG']):
            complexity_score += 1
        
        if complexity_score == 0:
            return 'Simple'
        elif complexity_score <= 3:
            return 'Moderate'
        elif complexity_score <= 6:
            return 'Complex'
        else:
            return 'Very Complex'
