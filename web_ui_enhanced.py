#!/usr/bin/env python3
"""
Enhanced Streamlit Web UI for Text-to-SQL Agent with Knowledge Base integration.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Import our enhanced agent
try:
    from src.enhanced_agent import EnhancedTextToSQLAgent
    from src.knowledge_base import KnowledgeBaseManager
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

load_dotenv()

# Configure Streamlit to hide deploy button
import streamlit as st
import os
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's deploy button and other UI elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
.stDeployButton {display:none !important;}
.stActionButton {display:none !important;}
button[kind="header"] {display:none !important;}
[data-testid="stToolbar"] {display:none !important;}
[data-testid="stDecoration"] {display:none !important;}
[data-testid="stStatusWidget"] {display:none !important;}
.stApp > header {display:none !important;}
.stApp > .main .block-container {padding-top: 1rem !important;}
footer {visibility: hidden !important;}
#stDecoration {display:none !important;}
/* Hide any button with "Deploy" text */
button:has-text("Deploy") {display:none !important;}
/* Hide toolbar area */
.stToolbar {display:none !important;}
/* Hide header buttons */
.stApp header button {display:none !important;}
/* Hide file change notifications */
[data-testid="stNotificationContentInfo"] {display:none !important;}
[data-testid="stNotificationContentWarning"] {display:none !important;}
.stAlert {display:none !important;}
.element-container:has([data-testid="stNotificationContentInfo"]) {display:none !important;}
/* Hide "File change detected" and similar messages */
div[data-testid="stMarkdownContainer"]:has-text("File change") {display:none !important;}
div[data-testid="stMarkdownContainer"]:has-text("Source file changed") {display:none !important;}
div[data-testid="stMarkdownContainer"]:has-text("Rerunning") {display:none !important;}
/* Hide development notifications */
.stNotification {display:none !important;}
[class*="notification"] {display:none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'selected_suggestion' not in st.session_state:
        st.session_state.selected_suggestion = None
    if 'query_text' not in st.session_state:
        st.session_state.query_text = ""
    if 'switch_to_query_tab' not in st.session_state:
        st.session_state.switch_to_query_tab = False


def render_login():
    """Render the login interface with username and password."""
    st.markdown('<div class="main-header">🔐 Login Required</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    🚀 **Secure Access:** Enter your username and password to access the Text-to-SQL Agent.
    Your session is secure and credentials are not saved permanently.
    """)
    
    # Define valid users (in production, this should be in a secure database)
    valid_users = {
        "admin": "admin123",
        "user1": "password123",
        "demo": "demo123",
        "analyst": "analyst123"
    }
    
    with st.form("login_form"):
        st.subheader("🔑 Enter Your Credentials")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            username = st.text_input(
                "Username",
                help="Enter your username"
            )
        
        with col2:
            password = st.text_input(
                "Password",
                type="password",
                help="Enter your password"
            )
        
        submitted = st.form_submit_button("🚀 Login", type="primary")
        
        if submitted:
            if username and password:
                # Check credentials
                if username in valid_users and valid_users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"✅ Welcome {username}! Initializing agent...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")
            else:
                st.error("❌ Please enter both username and password")
    



def initialize_agent():
    """Initialize the enhanced agent for authenticated users."""
    if st.session_state.agent is None and st.session_state.authenticated:
        try:
            with st.spinner("Initializing Enhanced Text-to-SQL Agent..."):
                st.session_state.agent = EnhancedTextToSQLAgent(
                    session_id=f"web_session_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    enable_cache=True,
                    enable_knowledge_base=True
                )
            st.success("✅ Agent initialized successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {str(e)}")
            st.error("Please check your configuration and try again.")
            # Reset authentication on failure
            if st.button("🔄 Try Again"):
                st.session_state.authenticated = False
                st.session_state.agent = None
                st.rerun()
            return False
    return st.session_state.authenticated


def render_sidebar():
    """Render the sidebar with configuration and status."""
    st.sidebar.title("🔧 Configuration")
    
    # Agent status
    if st.session_state.agent:
        st.sidebar.success("🤖 Agent: Ready")
        
        # Knowledge base status
        kb_status = st.session_state.agent.get_knowledge_base_status()
        if kb_status['enabled']:
            st.sidebar.success("📚 Knowledge Base: Connected")
        else:
            st.sidebar.warning("📚 Knowledge Base: Not configured")
            st.sidebar.caption("Set BEDROCK_KNOWLEDGE_BASE_ID in .env")
        
        # Cache status
        cache_stats = st.session_state.agent.get_cache_stats()
        if cache_stats.get('enabled'):
            hit_rate = cache_stats.get('hit_rate', 0) * 100
            st.sidebar.info(f"⚡ Cache Hit Rate: {hit_rate:.1f}%")
    else:
        st.sidebar.error("🤖 Agent: Not initialized")
    
    # Query options
    st.sidebar.subheader("Query Options")
    
    execute_query = st.sidebar.checkbox("Execute Query", value=True, 
                                       help="Execute the generated SQL on Athena")
    
    use_knowledge_base = st.sidebar.checkbox("Use Knowledge Base", value=True,
                                           help="Enhance queries with business context")
    
    explain_query = st.sidebar.checkbox("Explain Query", value=True,
                                       help="Generate AI explanation of the SQL")
    
    include_sample_data = st.sidebar.checkbox("Include Sample Data", value=True,
                                            help="Include sample data in schema context")
    
    # Advanced options
    with st.sidebar.expander("Advanced Options"):
        use_cache = st.checkbox("Use Cache", value=True)
        validate_query = st.checkbox("Validate Query", value=True)
    
    return {
        'execute_query': execute_query,
        'use_knowledge_base': use_knowledge_base,
        'explain_query': explain_query,
        'include_sample_data': include_sample_data,
        'use_cache': use_cache,
        'validate_query': validate_query
    }


def render_query_suggestions():
    """Render intelligent query suggestions."""
    if not st.session_state.agent:
        return
    
    st.subheader("💡 Intelligent Query Suggestions")
    
    try:
        suggestions = st.session_state.agent.get_query_suggestions()
        
        if suggestions:
            cols = st.columns(min(len(suggestions), 3))
            for i, suggestion in enumerate(suggestions[:6]):
                col_idx = i % 3
                with cols[col_idx]:
                    if st.button(f"📝 {suggestion[:50]}...", key=f"suggestion_{i}"):
                        st.session_state.query_text = suggestion
                        st.session_state.switch_to_query_tab = True
                        st.success(f"✅ Selected: {suggestion[:60]}...")
                        st.info("💡 Switch to the 'Query' tab to process this question!")
        else:
            st.info("No suggestions available. Try asking a question first!")
            
    except Exception as e:
        st.error(f"Error getting suggestions: {str(e)}")


def render_query_interface(options):
    """Render the main query interface."""
    st.subheader("🔍 Ask Your Question")
    
    # Show notification if user came from suggestions
    if st.session_state.switch_to_query_tab:
        st.success("✅ Query loaded from suggestions! You can now process it.")
        st.session_state.switch_to_query_tab = False
    
    # Query input - use session state to maintain value
    query_input = st.text_area(
        "Enter your question in natural language:",
        value=st.session_state.query_text,
        height=100,
        placeholder="e.g., Show me all customers from Texas who ordered Electronics",
        key="query_input"
    )
    
    # Update session state when user types
    if query_input != st.session_state.query_text:
        st.session_state.query_text = query_input
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        process_query = st.button("🚀 Process Query", type="primary")
    
    with col2:
        if st.button("🔄 Clear History"):
            st.session_state.query_history = []
            st.session_state.query_text = ""  # Also clear the query text
            st.rerun()
    
    with col3:
        if st.button("📊 Analyze Intent"):
            if query_input and st.session_state.agent:
                analyze_query_intent(query_input)
    
    return query_input, process_query


def analyze_query_intent(query):
    """Analyze and display query intent."""
    try:
        intent_analysis = st.session_state.agent.analyze_query_intent(query)
        
        st.subheader("📊 Query Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Intent Type", intent_analysis['intent_type'].title())
        
        with col2:
            st.metric("Complexity", intent_analysis['complexity'].title())
        
        with col3:
            st.metric("Tables Needed", len(intent_analysis['tables_likely_needed']))
        
        if intent_analysis['tables_likely_needed']:
            st.write("**Likely Tables:**", ", ".join(intent_analysis['tables_likely_needed']))
        
        if intent_analysis['recommendations']:
            st.write("**Recommendations:**")
            for rec in intent_analysis['recommendations']:
                st.write(f"• {rec}")
        
        if intent_analysis['business_context']:
            with st.expander("📚 Business Context from Knowledge Base"):
                for context in intent_analysis['business_context']:
                    confidence = int(context['confidence'] * 100)
                    st.write(f"**Confidence: {confidence}%**")
                    st.write(context['content'])
                    st.divider()
        
    except Exception as e:
        st.error(f"Error analyzing query intent: {str(e)}")


def process_query(query, options):
    """Process the natural language query."""
    if not query.strip():
        st.warning("Please enter a query")
        return
    
    if not st.session_state.agent:
        st.error("Agent not initialized")
        return
    
    with st.spinner("Processing your query..."):
        try:
            result = st.session_state.agent.query(
                query,
                execute=options['execute_query'],
                include_sample_data=options['include_sample_data'],
                explain=options['explain_query'],
                use_cache=options['use_cache'],
                validate=options['validate_query'],
                use_knowledge_base=options['use_knowledge_base']
            )
            
            # Store in history
            st.session_state.query_history.append({
                'timestamp': datetime.now(),
                'query': query,
                'result': result
            })
            
            # Store current results
            st.session_state.current_results = result
            
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")


def display_query_results(result):
    """Display the query results."""
    st.subheader("📋 Query Results")
    
    # Check if there's an error first
    if 'error' in result:
        st.error(f"❌ Error: {result['error']}")
        return
    
    # Display SQL query
    if 'sql_query' in result:
        st.write("**Generated SQL:**")
        st.code(result['sql_query'], language='sql')
    else:
        st.error("❌ No SQL query was generated. Check the error messages above.")
    
    # Display validation results
    if 'validation' in result:
        validation = result['validation']
        if validation['is_valid']:
            st.markdown('<div class="success-box">✅ Query validation passed</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">❌ Validation failed: {validation["error"]}</div>', 
                       unsafe_allow_html=True)
        

        
        # Business rule compliance
        if validation.get('business_rule_compliance'):
            compliance = validation['business_rule_compliance']
            if compliance['compliant']:
                st.success("✅ Business rules compliant")
            else:
                st.warning("⚠️ Business rule warnings found")
            
            if compliance['applicable_rules']:
                with st.expander("📋 Applicable Business Rules"):
                    for rule in compliance['applicable_rules']:
                        st.write(f"• {rule}")
    
    # Display knowledge base insights
    if result.get('knowledge_base_insights'):
        insights = result['knowledge_base_insights']
        
        if insights['relevant_context']:
            with st.expander("📚 Knowledge Base Insights"):
                for i, context in enumerate(insights['relevant_context'], 1):
                    confidence = int(context['confidence'] * 100)
                    st.write(f"**Context {i} (Confidence: {confidence}%)**")
                    st.write(context['content'])
                    if i < len(insights['relevant_context']):
                        st.divider()
        
        if insights['similar_queries']:
            with st.expander("🔍 Similar Queries"):
                for query in insights['similar_queries']:
                    st.write(f"• {query}")
    
    # Display explanation
    if 'explanation' in result:
        with st.expander("💭 Query Explanation"):
            st.write(result['explanation'])
    
    # Display execution results
    if result.get('executed') and 'results' in result:
        st.subheader("📊 Execution Results")
        
        if result['results']:
            df = pd.DataFrame(result['results'])
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows Returned", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                cached_status = "Yes" if result.get('cached') else "No"
                st.metric("Cached Result", cached_status)
            
            # Display data
            st.dataframe(df, use_container_width=True)
            
            # Auto-generate visualizations for numeric data
            render_auto_visualizations(df)
            
        else:
            st.info("Query executed successfully but returned no results")
    
    elif result.get('executed'):
        st.info("Query executed successfully")


def render_auto_visualizations(df):
    """Automatically generate visualizations for the data."""
    if df.empty:
        return
    
    # Filter out ID columns that are difficult to understand
    def is_id_column(col_name):
        """Check if a column is likely an ID column."""
        col_lower = col_name.lower()
        id_patterns = ['id', '_id', 'uuid', 'guid', 'key', '_key']
        return any(pattern in col_lower for pattern in id_patterns)
    
    numeric_columns = [col for col in df.select_dtypes(include=['number']).columns.tolist() 
                      if not is_id_column(col)]
    categorical_columns = [col for col in df.select_dtypes(include=['object', 'category']).columns.tolist() 
                          if not is_id_column(col)]
    
    if not numeric_columns:
        return
    
    st.subheader("📈 Auto-Generated Visualizations")
    
    # Simple bar chart for categorical + numeric
    if len(categorical_columns) >= 1 and len(numeric_columns) >= 1:
        cat_col = categorical_columns[0]
        num_col = numeric_columns[0]
        
        if len(df[cat_col].unique()) <= 20:  # Reasonable number of categories
            fig = px.bar(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
            st.plotly_chart(fig, use_container_width=True, key="bar_chart")
    
    # Time series if date column exists
    date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
    if date_columns and numeric_columns:
        date_col = date_columns[0]
        num_col = numeric_columns[0]
        fig = px.line(df, x=date_col, y=num_col, title=f"{num_col} over time")
        st.plotly_chart(fig, use_container_width=True, key="time_series_chart")
    
    # Distribution for numeric columns
    if len(numeric_columns) >= 1:
        num_col = numeric_columns[0]
        fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}")
        st.plotly_chart(fig, use_container_width=True, key="histogram_chart")


def render_query_history():
    """Render query history."""
    if not st.session_state.query_history:
        return
    
    st.subheader("📜 Query History")
    
    for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):  # Last 10 queries
        with st.expander(f"Query {len(st.session_state.query_history) - i}: {entry['query'][:50]}..."):
            st.write(f"**Time:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Query:** {entry['query']}")
            
            # Handle cases where sql_query might not exist
            if 'sql_query' in entry['result'] and entry['result']['sql_query']:
                st.code(entry['result']['sql_query'], language='sql')
            elif 'error' in entry['result']:
                st.error(f"Error: {entry['result']['error']}")
            else:
                st.warning("No SQL query generated")
            
            if entry['result'].get('executed'):
                row_count = entry['result'].get('row_count', 0)
                st.write(f"**Results:** {row_count} rows returned")


def render_knowledge_base_management():
    """Render knowledge base management interface."""
    st.subheader("📚 Knowledge Base Management")
    
    if not st.session_state.agent:
        st.warning("Initialize agent first")
        return
    
    kb_status = st.session_state.agent.get_knowledge_base_status()
    
    if kb_status['enabled']:
        st.success("✅ Knowledge Base is connected and ready")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuration:**")
            st.write(f"• KB ID: {kb_status.get('knowledge_base_id', 'N/A')}")
            st.write(f"• Max Results: {kb_status.get('max_results', 'N/A')}")
            st.write(f"• Confidence Threshold: {kb_status.get('confidence_threshold', 'N/A')}")
        
        with col2:
            st.write("**Test Knowledge Base:**")
            test_query = st.text_input("Test query:", placeholder="business rules for customers")
            if st.button("🔍 Test Query"):
                if test_query:
                    try:
                        kb_results = st.session_state.agent.knowledge_base.query_knowledge_base(test_query)
                        if kb_results:
                            st.write(f"Found {len(kb_results)} results:")
                            for result in kb_results[:3]:
                                confidence = int(result['confidence'] * 100)
                                st.write(f"**Confidence: {confidence}%**")
                                st.write(result['content'][:200] + "...")
                                st.divider()
                        else:
                            st.info("No results found")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    else:
        st.warning("⚠️ Knowledge Base not configured")
        st.write("To set up knowledge base:")
        st.code("""
1. Run: python setup_knowledge_base.py --bucket-name your-kb-bucket
2. Follow the setup instructions
3. Update .env with BEDROCK_KNOWLEDGE_BASE_ID
4. Restart the application
        """)
        
        # Show sample documents
        with st.expander("📄 Sample Knowledge Base Documents"):
            try:
                kb_manager = KnowledgeBaseManager()
                documents = kb_manager.create_sample_knowledge_base_content()
                
                for filename, content in documents.items():
                    st.write(f"**{filename}**")
                    st.text(content[:300] + "...")
                    st.divider()
            except Exception as e:
                st.error(f"Error creating sample documents: {str(e)}")


def render_sample_data():
    """Render sample data and table schemas."""
    st.subheader("📊 Sample Data & Table Schemas")
    
    if not st.session_state.agent:
        st.warning("Initialize agent first")
        return
    
    # Always show example tables for now
    st.info("💡 Showing example database structure. Connect to your database to see actual schema.")
    
    # Always show example tables for demonstration
    st.write("### 🗂️ Available Tables")
    st.success("📋 **Example Database Schema & Sample Data**")
    st.write("Here's what your database structure looks like:")
    
    example_tables = {
                "customers": {
                    "description": "Customer information and details",
                    "columns": [
                        {"name": "customer_id", "type": "INTEGER", "description": "Unique customer identifier"},
                        {"name": "name", "type": "VARCHAR", "description": "Customer full name"},
                        {"name": "email", "type": "VARCHAR", "description": "Customer email address"},
                        {"name": "state", "type": "VARCHAR", "description": "Customer state/region"},
                        {"name": "created_date", "type": "DATE", "description": "Account creation date"}
                    ],
                    "sample_data": [
                        {"customer_id": 1, "name": "John Smith", "email": "john.smith@email.com", "state": "Texas", "created_date": "2024-01-15"},
                        {"customer_id": 2, "name": "Sarah Johnson", "email": "sarah.j@email.com", "state": "California", "created_date": "2024-02-20"},
                        {"customer_id": 3, "name": "Mike Davis", "email": "mike.davis@email.com", "state": "New York", "created_date": "2024-03-10"},
                        {"customer_id": 4, "name": "Lisa Wilson", "email": "lisa.w@email.com", "state": "Florida", "created_date": "2024-01-25"},
                        {"customer_id": 5, "name": "David Brown", "email": "david.brown@email.com", "state": "Texas", "created_date": "2024-02-05"}
                    ]
                },
                "products": {
                    "description": "Product catalog and information",
                    "columns": [
                        {"name": "product_id", "type": "INTEGER", "description": "Unique product identifier"},
                        {"name": "name", "type": "VARCHAR", "description": "Product name"},
                        {"name": "category", "type": "VARCHAR", "description": "Product category"},
                        {"name": "price", "type": "DECIMAL", "description": "Product price"},
                        {"name": "description", "type": "TEXT", "description": "Product description"}
                    ],
                    "sample_data": [
                        {"product_id": 101, "name": "Laptop Pro", "category": "Electronics", "price": 1299.99, "description": "High-performance laptop"},
                        {"product_id": 102, "name": "Wireless Mouse", "category": "Electronics", "price": 29.99, "description": "Ergonomic wireless mouse"},
                        {"product_id": 103, "name": "Office Chair", "category": "Furniture", "price": 249.99, "description": "Comfortable office chair"},
                        {"product_id": 104, "name": "Desk Lamp", "category": "Furniture", "price": 79.99, "description": "LED desk lamp"},
                        {"product_id": 105, "name": "Smartphone", "category": "Electronics", "price": 699.99, "description": "Latest smartphone model"}
                    ]
                },
                "orders": {
                    "description": "Customer orders and transactions",
                    "columns": [
                        {"name": "order_id", "type": "INTEGER", "description": "Unique order identifier"},
                        {"name": "customer_id", "type": "INTEGER", "description": "Customer who placed order"},
                        {"name": "product_id", "type": "INTEGER", "description": "Ordered product"},
                        {"name": "quantity", "type": "INTEGER", "description": "Quantity ordered"},
                        {"name": "order_date", "type": "DATE", "description": "Date order was placed"},
                        {"name": "total_amount", "type": "DECIMAL", "description": "Total order amount"}
                    ],
                    "sample_data": [
                        {"order_id": 1001, "customer_id": 1, "product_id": 101, "quantity": 1, "order_date": "2024-03-15", "total_amount": 1299.99},
                        {"order_id": 1002, "customer_id": 2, "product_id": 102, "quantity": 2, "order_date": "2024-03-16", "total_amount": 59.98},
                        {"order_id": 1003, "customer_id": 3, "product_id": 103, "quantity": 1, "order_date": "2024-03-17", "total_amount": 249.99},
                        {"order_id": 1004, "customer_id": 1, "product_id": 104, "quantity": 1, "order_date": "2024-03-18", "total_amount": 79.99},
                        {"order_id": 1005, "customer_id": 4, "product_id": 105, "quantity": 1, "order_date": "2024-03-19", "total_amount": 699.99}
                    ]
                }
    }
    
    table_tabs = st.tabs([f"📋 {name}" for name in example_tables.keys()])
    
    for i, (table_name, table_info) in enumerate(example_tables.items()):
        with table_tabs[i]:
            st.write(f"**📝 Table: {table_name}**")
            st.write(f"*{table_info['description']}*")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**📋 Schema:**")
                schema_df = pd.DataFrame([
                    {
                        'Column': col['name'],
                        'Type': col['type'],
                        'Description': col['description']
                    }
                    for col in table_info['columns']
                ])
                st.dataframe(schema_df, use_container_width=True)
            
            with col2:
                st.write("**🔍 Sample Data:**")
                if 'sample_data' in table_info:
                    sample_df = pd.DataFrame(table_info['sample_data'])
                    st.dataframe(sample_df, use_container_width=True)
                else:
                    st.info("💡 Connect to your database to see actual sample data")
    
    # Add helpful information (outside the loop)
    st.divider()
    st.write("### 💡 How to Use This Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📝 For Writing Queries:**")
        st.write("• Use table and column names shown above")
        st.write("• Reference the data types for proper filtering")
        st.write("• Check sample data to understand data patterns")
    
    with col2:
        st.write("**🔍 Query Examples:**")
        st.code("""
-- Find customers from Texas
SELECT * FROM customers WHERE state = 'Texas'

-- Top 5 most expensive products
SELECT * FROM products ORDER BY price DESC LIMIT 5

-- Recent orders with customer info
SELECT c.name, o.order_date, o.total_amount 
FROM customers c 
JOIN orders o ON c.customer_id = o.customer_id 
WHERE o.order_date >= '2024-01-01'
        """, language='sql')


def render_query_interface(options):
    """Render the main query interface."""
    st.subheader("🔍 Ask Your Question")
    
    # Show notification if user came from suggestions
    if st.session_state.switch_to_query_tab:
        st.success("✅ Query loaded from suggestions! You can now process it.")
        st.session_state.switch_to_query_tab = False
    
    # Query input - use session state to maintain value
    query_input = st.text_area(
        "Enter your question in natural language:",
        value=st.session_state.query_text,
        height=100,
        placeholder="e.g., Show me all customers from Texas who ordered Electronics",
        key="query_input_area"
    )
    
    # Update session state when user types
    if query_input != st.session_state.query_text:
        st.session_state.query_text = query_input
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Use a unique key and check for both button click and query content
        process_query = st.button("🚀 Process Query", type="primary", key="process_btn")
    
    with col2:
        if st.button("🔄 Clear History", key="clear_btn"):
            st.session_state.query_history = []
            st.session_state.query_text = ""  # Also clear the query text
            st.rerun()
    
    with col3:
        if st.button("📊 Analyze Intent", key="analyze_btn"):
            if query_input and st.session_state.agent:
                analyze_query_intent(query_input)
    
    return query_input, process_query


def process_query(query, options):
    """Process the natural language query."""
    if not query.strip():
        st.warning("Please enter a query")
        return
    
    if not st.session_state.agent:
        st.error("Agent not initialized")
        return
    
    with st.spinner("Processing your query..."):
        try:
            result = st.session_state.agent.query(
                query,
                execute=options['execute_query'],
                include_sample_data=options['include_sample_data'],
                explain=options['explain_query'],
                use_cache=options['use_cache'],
                validate=options['validate_query'],
                use_knowledge_base=options['use_knowledge_base']
            )
            
            # Store in history
            st.session_state.query_history.append({
                'timestamp': datetime.now(),
                'query': query,
                'result': result
            })
            
            # Store current results
            st.session_state.current_results = result
            
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")


def analyze_query_intent(query):
    """Analyze and display query intent."""
    try:
        intent_analysis = st.session_state.agent.analyze_query_intent(query)
        
        st.subheader("📊 Query Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Intent Type", intent_analysis['intent_type'].title())
        
        with col2:
            st.metric("Complexity", intent_analysis['complexity'].title())
        
        with col3:
            st.metric("Tables Needed", len(intent_analysis['tables_likely_needed']))
        
        if intent_analysis['tables_likely_needed']:
            st.write("**Likely Tables:**", ", ".join(intent_analysis['tables_likely_needed']))
        
        if intent_analysis['recommendations']:
            st.write("**Recommendations:**")
            for rec in intent_analysis['recommendations']:
                st.write(f"• {rec}")
        
        if intent_analysis['business_context']:
            with st.expander("📚 Business Context from Knowledge Base"):
                for context in intent_analysis['business_context']:
                    confidence = int(context['confidence'] * 100)
                    st.write(f"**Confidence: {confidence}%**")
                    st.write(context['content'])
                    st.divider()
        
    except Exception as e:
        st.error(f"Error analyzing query intent: {str(e)}")


def display_query_results(result):
    """Display the query results."""
    st.subheader("📋 Query Results")
    
    # Check if there's an error first
    if 'error' in result:
        st.error(f"❌ Error: {result['error']}")
        return
    
    # Display SQL query
    if 'sql_query' in result:
        st.write("**Generated SQL:**")
        st.code(result['sql_query'], language='sql')
    else:
        st.error("❌ No SQL query was generated. Check the error messages above.")
    
    # Display validation results
    if 'validation' in result:
        validation = result['validation']
        if validation['is_valid']:
            st.markdown('<div class="success-box">✅ Query validation passed</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">❌ Validation failed: {validation["error"]}</div>', 
                       unsafe_allow_html=True)
        
        # Business rule compliance
        if validation.get('business_rule_compliance'):
            compliance = validation['business_rule_compliance']
            if compliance['compliant']:
                st.success("✅ Business rules compliant")
            else:
                st.warning("⚠️ Business rule warnings found")
            
            if compliance['applicable_rules']:
                with st.expander("📋 Applicable Business Rules"):
                    for rule in compliance['applicable_rules']:
                        st.write(f"• {rule}")
    
    # Display knowledge base insights
    if result.get('knowledge_base_insights'):
        insights = result['knowledge_base_insights']
        
        if insights['relevant_context']:
            with st.expander("📚 Knowledge Base Insights"):
                for i, context in enumerate(insights['relevant_context'], 1):
                    confidence = int(context['confidence'] * 100)
                    st.write(f"**Context {i} (Confidence: {confidence}%)**")
                    st.write(context['content'])
                    if i < len(insights['relevant_context']):
                        st.divider()
        
        if insights['similar_queries']:
            with st.expander("🔍 Similar Queries"):
                for query in insights['similar_queries']:
                    st.write(f"• {query}")
    
    # Display explanation
    if 'explanation' in result:
        with st.expander("💭 Query Explanation"):
            st.write(result['explanation'])
    
    # Display execution results
    if result.get('executed') and 'results' in result:
        st.subheader("📊 Execution Results")
        
        if result['results']:
            df = pd.DataFrame(result['results'])
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows Returned", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                cached_status = "Yes" if result.get('cached') else "No"
                st.metric("Cached Result", cached_status)
            
            # Display data
            st.dataframe(df, use_container_width=True)
            
            # Auto-generate visualizations for numeric data
            render_auto_visualizations(df)
            
        else:
            st.info("Query executed successfully but returned no results")
    
    elif result.get('executed'):
        st.info("Query executed successfully")


def render_auto_visualizations(df):
    """Automatically generate visualizations for the data."""
    if df.empty:
        return
    
    # Filter out ID columns that are difficult to understand
    def is_id_column(col_name):
        """Check if a column is likely an ID column."""
        col_lower = col_name.lower()
        id_patterns = ['id', '_id', 'uuid', 'guid', 'key', '_key']
        return any(pattern in col_lower for pattern in id_patterns)
    
    numeric_columns = [col for col in df.select_dtypes(include=['number']).columns.tolist() 
                      if not is_id_column(col)]
    categorical_columns = [col for col in df.select_dtypes(include=['object', 'category']).columns.tolist() 
                          if not is_id_column(col)]
    
    if not numeric_columns:
        return
    
    st.subheader("📈 Auto-Generated Visualizations")
    
    # Simple bar chart for categorical + numeric
    if len(categorical_columns) >= 1 and len(numeric_columns) >= 1:
        cat_col = categorical_columns[0]
        num_col = numeric_columns[0]
        
        if len(df[cat_col].unique()) <= 20:  # Reasonable number of categories
            fig = px.bar(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
            st.plotly_chart(fig, use_container_width=True, key="bar_chart")
    
    # Time series if date column exists
    date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
    if date_columns and numeric_columns:
        date_col = date_columns[0]
        num_col = numeric_columns[0]
        fig = px.line(df, x=date_col, y=num_col, title=f"{num_col} over time")
        st.plotly_chart(fig, use_container_width=True, key="time_series_chart")
    
    # Distribution for numeric columns
    if len(numeric_columns) >= 1:
        num_col = numeric_columns[0]
        fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}")
        st.plotly_chart(fig, use_container_width=True, key="histogram_chart")


def render_query_history():
    """Render query history."""
    if not st.session_state.query_history:
        return
    
    st.subheader("📜 Query History")
    
    for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):  # Last 10 queries
        with st.expander(f"Query {len(st.session_state.query_history) - i}: {entry['query'][:50]}..."):
            st.write(f"**Time:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Query:** {entry['query']}")
            
            # Handle cases where sql_query might not exist
            if 'sql_query' in entry['result'] and entry['result']['sql_query']:
                st.code(entry['result']['sql_query'], language='sql')
            elif 'error' in entry['result']:
                st.error(f"Error: {entry['result']['error']}")
            else:
                st.warning("No SQL query generated")
            
            if entry['result'].get('executed'):
                row_count = entry['result'].get('row_count', 0)
                st.write(f"**Results:** {row_count} rows returned")


def main():
    """Main application function."""
    initialize_session_state()
    
    # Check authentication first
    if not st.session_state.authenticated:
        render_login()
        return
    
    # Add logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", help="Clear session and logout"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Show current user
        if st.session_state.username:
            st.caption(f"👤 Logged in as: {st.session_state.username}")
    
    # Header
    st.markdown('<div class="main-header">🤖 Text-to-SQL Agent</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    🚀 **Powered by Knowledge Base:** Get intelligent SQL generation with business context, 
    query suggestions, and domain-specific insights powered by Amazon Bedrock Knowledge Base.
    """)
    
    # Initialize agent
    if not initialize_agent():
        st.stop()
    
    # Sidebar
    options = render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query", "💡 Suggestions", "📜 History", "📊 Sample Data"])
    
    with tab1:
        query_input, process_query_btn = render_query_interface(options)
        
        if process_query_btn and query_input:
            process_query(query_input, options)
        
        # Display current results if any
        if st.session_state.current_results:
            st.divider()
            display_query_results(st.session_state.current_results)
    
    with tab2:
        render_query_suggestions()
    
    with tab3:
        render_query_history()
    
    with tab4:
        render_sample_data()


if __name__ == "__main__":
    main()