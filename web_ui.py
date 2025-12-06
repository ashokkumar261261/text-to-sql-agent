#!/usr/bin/env python3
"""
Streamlit Web UI for Text-to-SQL Agent
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.agent import TextToSQLAgent
from src.conversation import ConversationHistory
import json

# Page configuration
st.set_page_config(
    page_title="Text-to-SQL Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .sql-code {
        background-color: #282c34;
        color: #abb2bf;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def initialize_agent():
    """Initialize the Text-to-SQL agent."""
    if st.session_state.agent is None:
        with st.spinner("Initializing agent..."):
            st.session_state.agent = TextToSQLAgent(
                session_id=st.session_state.session_id,
                enable_cache=True
            )
            st.session_state.session_id = st.session_state.agent.conversation.session_id

def display_query_result(result):
    """Display query results in a formatted way."""
    
    # Display SQL Query
    st.subheader("📝 Generated SQL")
    st.code(result.get('sql_query', ''), language='sql')
    
    # Display Validation
    if 'validation' in result:
        validation = result['validation']
        if validation['is_valid']:
            st.success("✅ Query validation passed")
        else:
            st.error(f"❌ Validation failed: {validation['error']}")
            return
        
        if validation.get('warnings'):
            with st.expander("⚠️ Warnings"):
                for warning in validation['warnings']:
                    st.warning(warning)
    
    # Display Query Info
    if 'query_info' in result:
        info = result['query_info']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tables", len(info.get('tables', [])))
        with col2:
            st.metric("Complexity", info.get('estimated_complexity', 'Unknown'))
        with col3:
            st.metric("Has Joins", "Yes" if info.get('has_joins') else "No")
        with col4:
            st.metric("Has Aggregation", "Yes" if info.get('has_aggregation') else "No")
    
    # Display Explanation
    if 'explanation' in result:
        with st.expander("💡 Query Explanation", expanded=True):
            st.info(result['explanation'])
    
    # Display Results
    if result.get('executed'):
        st.subheader("📊 Query Results")
        
        if result.get('cached'):
            st.info("⚡ Results loaded from cache")
        
        if 'results' in result and result['results']:
            df = pd.DataFrame(result['results'])
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows Returned", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            
            # Display data table
            st.dataframe(df, use_container_width=True)
            
            # Offer to visualize if numeric columns exist
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) > 0:
                with st.expander("📈 Visualize Data"):
                    viz_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Pie"])
                    
                    if viz_type == "Bar" and len(df.columns) >= 2:
                        x_col = st.selectbox("X-axis", df.columns)
                        y_col = st.selectbox("Y-axis", numeric_cols)
                        fig = px.bar(df, x=x_col, y=y_col)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Line" and len(numeric_cols) >= 1:
                        y_col = st.selectbox("Y-axis", numeric_cols)
                        fig = px.line(df, y=y_col)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Scatter" and len(numeric_cols) >= 2:
                        x_col = st.selectbox("X-axis", numeric_cols)
                        y_col = st.selectbox("Y-axis", numeric_cols)
                        fig = px.scatter(df, x=x_col, y=y_col)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Pie" and len(df.columns) >= 2:
                        names_col = st.selectbox("Labels", df.columns)
                        values_col = st.selectbox("Values", numeric_cols)
                        fig = px.pie(df, names=names_col, values=values_col)
                        st.plotly_chart(fig, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
        else:
            st.info("No results returned")
    
    # Display Error
    if 'error' in result:
        st.error(f"❌ Error: {result['error']}")

def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">🔍 Text-to-SQL Agent</div>', unsafe_allow_html=True)
    st.markdown("Convert natural language questions into SQL queries and execute them on your data lake")
    
    # Initialize agent
    initialize_agent()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Query Options
        st.subheader("Query Options")
        execute_query = st.checkbox("Execute Query", value=False, 
                                   help="Execute the generated SQL on Athena")
        explain_query = st.checkbox("Explain Query", value=True,
                                   help="Generate explanation of the SQL query")
        use_cache = st.checkbox("Use Cache", value=True,
                               help="Use cached results if available")
        validate_query = st.checkbox("Validate Query", value=True,
                                    help="Validate query before execution")
        
        st.divider()
        
        # Session Info
        st.subheader("📊 Session Info")
        if st.session_state.agent:
            summary = st.session_state.agent.get_conversation_summary()
            st.metric("Queries", summary['queries_executed'])
            st.metric("Messages", summary['message_count'])
            
            if st.session_state.agent.cache:
                cache_stats = st.session_state.agent.get_cache_stats()
                st.metric("Cache Hits", cache_stats.get('total_hits', 0))
        
        st.divider()
        
        # Actions
        st.subheader("🔧 Actions")
        if st.button("🗑️ Clear Conversation"):
            st.session_state.agent.clear_conversation()
            st.session_state.query_history = []
            st.success("Conversation cleared!")
            st.rerun()
        
        if st.button("🧹 Clear Cache"):
            st.session_state.agent.clear_cache()
            st.success("Cache cleared!")
        
        if st.button("🔄 New Session"):
            st.session_state.agent = None
            st.session_state.session_id = None
            st.session_state.query_history = []
            st.rerun()
        
        st.divider()
        
        # Example Queries
        st.subheader("💡 Example Queries")
        examples = [
            "Show me all customers from Texas",
            "What are the top 5 products by price?",
            "Count total orders by status",
            "List orders over $500",
            "Show customers who ordered Electronics",
            "Calculate total revenue by category"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.example_query = example
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Query input
        query_input = st.text_area(
            "Enter your question:",
            value=st.session_state.get('example_query', ''),
            height=100,
            placeholder="e.g., Show me all customers from California who made purchases over $1000"
        )
        
        # Clear example query after use
        if 'example_query' in st.session_state:
            del st.session_state.example_query
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        submit_button = st.button("💡 Get Insights", type="primary", use_container_width=True)
    
    # Process query
    if submit_button and query_input:
        with st.spinner("Generating SQL query..."):
            result = st.session_state.agent.query(
                natural_language_query=query_input,
                execute=execute_query,
                explain=explain_query,
                use_cache=use_cache,
                validate=validate_query
            )
            
            # Add to history
            st.session_state.query_history.append({
                'query': query_input,
                'result': result
            })
            
            # Display result
            display_query_result(result)
    
    # Query History
    if st.session_state.query_history:
        st.divider()
        st.subheader("📜 Query History")
        
        for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"Query {len(st.session_state.query_history) - idx}: {item['query'][:50]}..."):
                st.write(f"**Question:** {item['query']}")
                st.code(item['result'].get('sql_query', ''), language='sql')
                if item['result'].get('executed'):
                    st.write(f"**Rows:** {item['result'].get('row_count', 0)}")
                    if item['result'].get('cached'):
                        st.info("⚡ Cached result")

if __name__ == "__main__":
    main()
