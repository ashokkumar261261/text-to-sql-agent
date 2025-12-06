# Enhanced Features Guide

Your Text-to-SQL agent now includes powerful new features!

## 🎯 New Features

### 1. Query Validation ✅

Automatically validates SQL queries before execution to prevent:
- Dangerous operations (DROP, DELETE, UPDATE, etc.)
- SQL injection attempts
- Syntax errors
- Unbalanced parentheses

**Usage:**
```python
from src.agent import TextToSQLAgent

agent = TextToSQLAgent()
result = agent.query("Show me all customers", validate=True)

if result['validation']['is_valid']:
    print("✓ Query is safe to execute")
else:
    print(f"✗ Validation failed: {result['validation']['error']}")
```

**Features:**
- Blocks dangerous SQL operations
- Detects SQL injection patterns
- Provides warnings for potential issues
- Analyzes query complexity
- Suggests improvements (e.g., adding LIMIT)

### 2. Result Caching ⚡

Caches query results to avoid redundant Athena executions:
- In-memory cache for fast access
- Disk cache for persistence
- Configurable TTL (default: 1 hour)
- Automatic cache invalidation

**Usage:**
```python
agent = TextToSQLAgent(enable_cache=True)

# First execution - hits Athena
result1 = agent.query("Count all orders", execute=True, use_cache=True)

# Second execution - uses cache (much faster!)
result2 = agent.query("Count all orders", execute=True, use_cache=True)

print(f"Cached: {result2['cached']}")  # True

# Get cache statistics
stats = agent.get_cache_stats()
print(f"Cache hits: {stats['total_hits']}")

# Clear cache
agent.clear_cache()
```

**Benefits:**
- Faster response times
- Reduced Athena costs
- Better user experience
- Automatic cleanup of expired entries

### 3. Query Explanations 💡

Generates human-readable explanations of SQL queries:
- Explains what the query does
- Describes how it answers the question
- Uses simple, non-technical language

**Usage:**
```python
result = agent.query(
    "Show me top 5 products by price",
    explain=True
)

print(result['explanation'])
# Output: "This query retrieves the 5 most expensive products from the 
# products table by sorting them in descending order by price..."
```

**Use Cases:**
- Learning SQL
- Debugging queries
- Documenting queries
- Explaining to non-technical users

### 4. Conversation History 💬

Maintains context across multiple queries:
- Remembers previous queries
- Handles follow-up questions
- Detects context references
- Persists conversations to disk

**Usage:**
```python
# Create a session
agent = TextToSQLAgent(session_id="user_123")

# First query
agent.query("Show me all Electronics products")

# Follow-up query (uses context)
agent.query("What about Furniture?")  # Understands "products" context

# Another follow-up
agent.query("Show me the most expensive one")  # Knows which table

# Get conversation summary
summary = agent.get_conversation_summary()
print(f"Queries executed: {summary['queries_executed']}")

# Clear conversation
agent.clear_conversation()
```

**Features:**
- Automatic follow-up detection
- Context-aware query enhancement
- Session persistence
- Conversation summaries
- Multi-user support

### 5. Web UI 🌐

Beautiful Streamlit-based web interface:
- Interactive query input
- Real-time SQL generation
- Result visualization
- Query history
- Session management

**Launch:**
```powershell
# Install web dependencies
.\run.bat -m pip install -r requirements.txt

# Start web UI
.\run.bat -m streamlit run web_ui.py
```

**Features:**
- 📝 Live SQL generation
- ✅ Query validation display
- 💡 Query explanations
- 📊 Data visualization (charts)
- 📥 CSV export
- 📜 Query history
- ⚙️ Configurable options
- 💡 Example queries
- ⚡ Cache indicators

## 📚 Complete Examples

### Example 1: Basic Query with All Features

```python
from src.agent import TextToSQLAgent

agent = TextToSQLAgent()

result = agent.query(
    natural_language_query="Show me all customers from California",
    execute=True,           # Execute on Athena
    explain=True,           # Generate explanation
    validate=True,          # Validate before execution
    use_cache=True          # Use cache if available
)

# Check validation
if result['validation']['is_valid']:
    print(f"✓ Query validated")
    print(f"SQL: {result['sql_query']}")
    print(f"Explanation: {result['explanation']}")
    print(f"Results: {result['row_count']} rows")
    print(f"Cached: {result['cached']}")
else:
    print(f"✗ Validation failed: {result['validation']['error']}")
```

### Example 2: Conversation Flow

```python
agent = TextToSQLAgent(session_id="demo")

# Initial query
r1 = agent.query("Show me all orders from January 2024")
print(f"SQL: {r1['sql_query']}")

# Follow-up (understands context)
r2 = agent.query("What about February?")
print(f"SQL: {r2['sql_query']}")

# Another follow-up
r3 = agent.query("Show me the total amount")
print(f"SQL: {r3['sql_query']}")

# View conversation
summary = agent.get_conversation_summary()
print(f"Total queries: {summary['queries_executed']}")
```

### Example 3: Validation and Safety

```python
agent = TextToSQLAgent()

# Try a dangerous query
result = agent.query("Delete all customers", validate=True)

if not result['validation']['is_valid']:
    print(f"✓ Blocked dangerous query!")
    print(f"Reason: {result['validation']['error']}")

# Safe query with warnings
result = agent.query("SELECT * FROM customers", validate=True)

if result['validation']['warnings']:
    print("Warnings:")
    for warning in result['validation']['warnings']:
        print(f"  - {warning}")
```

### Example 4: Performance with Caching

```python
import time

agent = TextToSQLAgent(enable_cache=True)

query = "Count all orders by status"

# First execution
start = time.time()
result1 = agent.query(query, execute=True)
time1 = time.time() - start
print(f"First execution: {time1:.2f}s")

# Second execution (cached)
start = time.time()
result2 = agent.query(query, execute=True)
time2 = time.time() - start
print(f"Second execution: {time2:.2f}s (cached)")
print(f"Speedup: {time1/time2:.1f}x faster!")
```

## 🚀 Quick Start

1. **Install dependencies:**
```powershell
.\run.bat -m pip install -r requirements.txt
```

2. **Run enhanced examples:**
```powershell
.\run.bat example_enhanced.py
```

3. **Launch web UI:**
```powershell
.\run.bat -m streamlit run web_ui.py
```

## 📁 New Files and Folders

- `.cache/` - Query result cache
- `.history/` - Conversation history
- `src/query_validator.py` - Query validation logic
- `src/query_cache.py` - Caching implementation
- `src/conversation.py` - Conversation management
- `web_ui.py` - Streamlit web interface
- `example_enhanced.py` - Enhanced examples

## ⚙️ Configuration

### Cache Settings

```python
from src.query_cache import QueryCache

# Custom cache with 2-hour TTL
cache = QueryCache(cache_dir='.cache', ttl_seconds=7200)

# Get cache stats
stats = cache.get_stats()

# Clear expired entries
cache.cleanup_expired()
```

### Validator Settings

```python
from src.query_validator import QueryValidator

# Custom validator with 10KB max query size
validator = QueryValidator(max_query_length=10000)

# Validate query
is_valid, error, warnings = validator.validate(sql_query)

# Get query info
info = validator.get_query_info(sql_query)
```

### Conversation Settings

```python
from src.conversation import ConversationHistory

# Custom history location
conversation = ConversationHistory(
    session_id="user_123",
    history_dir='.my_history'
)

# List all sessions
sessions = ConversationHistory.list_sessions()
```

## 🎨 Web UI Features

### Main Interface
- **Query Input:** Large text area for natural language questions
- **Options Panel:** Toggle execution, explanation, caching, validation
- **Results Display:** Formatted SQL, validation, explanation, data table
- **Visualizations:** Auto-generated charts for numeric data

### Sidebar
- **Session Info:** Query count, cache hits, message count
- **Actions:** Clear conversation, clear cache, new session
- **Example Queries:** One-click example questions
- **Settings:** Configure query options

### Data Visualization
- Bar charts
- Line charts
- Scatter plots
- Pie charts
- CSV export

## 💡 Tips and Best Practices

1. **Use Validation:** Always validate queries before execution
2. **Enable Caching:** Significantly improves performance
3. **Request Explanations:** Great for learning and debugging
4. **Maintain Sessions:** Better context for follow-up questions
5. **Monitor Cache:** Check cache stats to optimize TTL
6. **Review Warnings:** Pay attention to validation warnings
7. **Use Web UI:** Best experience for interactive exploration

## 🐛 Troubleshooting

### Cache not working
- Check `.cache/` folder exists
- Verify disk space available
- Check cache TTL settings

### Conversation context lost
- Ensure session_id is consistent
- Check `.history/` folder exists
- Verify file permissions

### Validation too strict
- Review validation rules in `query_validator.py`
- Adjust `DANGEROUS_KEYWORDS` list if needed
- Use `validate=False` for trusted queries

### Web UI not starting
- Install streamlit: `pip install streamlit`
- Check port 8501 is available
- Run: `streamlit run web_ui.py --server.port 8502`

## 📊 Performance Metrics

With these enhancements:
- **Query validation:** < 1ms overhead
- **Cache hits:** 10-100x faster than Athena
- **Explanations:** +2-3s per query
- **Conversation context:** < 10ms overhead

## 🔒 Security Features

- SQL injection detection
- Dangerous operation blocking
- Query sanitization
- Read-only enforcement
- Input validation
- Safe defaults

## 🎯 Next Steps

1. Explore the web UI
2. Try conversation flows
3. Monitor cache performance
4. Review validation logs
5. Customize for your use case
6. Deploy to production

Enjoy your enhanced Text-to-SQL agent! 🚀
