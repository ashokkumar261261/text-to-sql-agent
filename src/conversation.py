"""
Conversation history management for follow-up questions
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class ConversationHistory:
    """Manages conversation history for context-aware queries."""
    
    def __init__(self, session_id: str = None, history_dir: str = '.history'):
        """
        Initialize conversation history.
        
        Args:
            session_id: Unique session identifier
            history_dir: Directory to store conversation history
        """
        self.session_id = session_id or self._generate_session_id()
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.messages: List[Dict] = []
        self._load_history()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _get_history_file(self) -> Path:
        """Get the history file path for this session."""
        return self.history_dir / f"session_{self.session_id}.json"
    
    def _load_history(self):
        """Load conversation history from disk."""
        history_file = self._get_history_file()
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.messages = data.get('messages', [])
            except Exception:
                self.messages = []
    
    def _save_history(self):
        """Save conversation history to disk."""
        history_file = self._get_history_file()
        try:
            with open(history_file, 'w') as f:
                json.dump({
                    'session_id': self.session_id,
                    'created_at': self.messages[0]['timestamp'] if self.messages else datetime.now().isoformat(),
                    'messages': self.messages
                }, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def add_message(self, role: str, content: str, sql_query: str = None, 
                   results: any = None, metadata: Dict = None):
        """
        Add a message to conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: The message content
            sql_query: Generated SQL query (for assistant messages)
            results: Query results (for assistant messages)
            metadata: Additional metadata
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'sql_query': sql_query,
            'metadata': metadata or {}
        }
        
        # Don't store full results in history (can be large)
        if results is not None:
            message['result_count'] = len(results) if isinstance(results, list) else 1
        
        self.messages.append(message)
        self._save_history()
    
    def get_context(self, max_messages: int = 5) -> str:
        """
        Get recent conversation context for the AI.
        
        Args:
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Formatted context string
        """
        if not self.messages:
            return ""
        
        recent_messages = self.messages[-max_messages:]
        
        context_parts = ["Previous conversation:"]
        for msg in recent_messages:
            if msg['role'] == 'user':
                context_parts.append(f"User asked: {msg['content']}")
            elif msg['role'] == 'assistant' and msg.get('sql_query'):
                context_parts.append(f"Generated SQL: {msg['sql_query']}")
        
        return "\n".join(context_parts)
    
    def get_last_query(self) -> Optional[str]:
        """Get the last SQL query from history."""
        for msg in reversed(self.messages):
            if msg['role'] == 'assistant' and msg.get('sql_query'):
                return msg['sql_query']
        return None
    
    def get_last_tables(self) -> List[str]:
        """Get tables mentioned in recent queries."""
        tables = set()
        for msg in reversed(self.messages[-5:]):
            if msg.get('sql_query'):
                # Simple extraction of table names
                import re
                sql = msg['sql_query'].upper()
                found_tables = re.findall(r'FROM\s+(\w+)', sql)
                found_tables.extend(re.findall(r'JOIN\s+(\w+)', sql))
                tables.update(found_tables)
        return list(tables)
    
    def detect_follow_up(self, query: str) -> bool:
        """
        Detect if a query is a follow-up question.
        
        Args:
            query: The user's query
            
        Returns:
            True if it appears to be a follow-up
        """
        if not self.messages:
            return False
        
        query_lower = query.lower()
        
        # Follow-up indicators
        follow_up_patterns = [
            'also', 'too', 'as well', 'additionally',
            'what about', 'how about', 'and',
            'same', 'those', 'these', 'that', 'this',
            'more', 'other', 'another',
            'show me more', 'tell me more',
            'previous', 'last', 'earlier'
        ]
        
        return any(pattern in query_lower for pattern in follow_up_patterns)
    
    def enhance_query_with_context(self, query: str) -> str:
        """
        Enhance a follow-up query with context from history.
        
        Args:
            query: The user's query
            
        Returns:
            Enhanced query with context
        """
        if not self.detect_follow_up(query):
            return query
        
        last_tables = self.get_last_tables()
        if last_tables:
            context = f"(Context: Previous query used tables: {', '.join(last_tables)})"
            return f"{query} {context}"
        
        return query
    
    def get_summary(self) -> Dict:
        """Get a summary of the conversation."""
        return {
            'session_id': self.session_id,
            'message_count': len(self.messages),
            'queries_executed': sum(1 for m in self.messages if m.get('sql_query')),
            'started_at': self.messages[0]['timestamp'] if self.messages else None,
            'last_activity': self.messages[-1]['timestamp'] if self.messages else None
        }
    
    def get_recent_queries(self, limit: int = 5) -> List[str]:
        """
        Get recent user queries from conversation history.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of recent user queries
        """
        queries = []
        for msg in reversed(self.messages):
            if msg['role'] == 'user' and msg['content']:
                queries.append(msg['content'])
                if len(queries) >= limit:
                    break
        return list(reversed(queries))
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []
        history_file = self._get_history_file()
        if history_file.exists():
            history_file.unlink()
    
    @staticmethod
    def list_sessions(history_dir: str = '.history') -> List[Dict]:
        """List all conversation sessions."""
        history_path = Path(history_dir)
        if not history_path.exists():
            return []
        
        sessions = []
        for file in history_path.glob('session_*.json'):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        'session_id': data.get('session_id'),
                        'created_at': data.get('created_at'),
                        'message_count': len(data.get('messages', []))
                    })
            except Exception:
                pass
        
        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)
