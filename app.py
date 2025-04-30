import streamlit as st
from llm_service import generate_sql_query
from db_service import get_detailed_schema_information, execute_sql
import pandas as pd

# Configure page
st.set_page_config(
    page_title="SQL Query Generator",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .sql-box {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.title("🔍 SQL Query Generator")

# Sidebar with schema
with st.sidebar:
    st.header("Database Schema")
    if st.button("Refresh Schema"):
        st.cache_data.clear()
    schema_info = get_detailed_schema_information()
    st.json(schema_info, expanded=False)

# Main content
question = st.text_input(
    "Enter your question:",
    placeholder="e.g. Show me all employees in the Sales department"
)

if st.button("Generate and Execute SQL"):
    if question:
        with st.spinner("Processing..."):
            try:
                # Generate SQL
                sql_query = generate_sql_query(question)
                st.success("Generated SQL Query")
                st.code(sql_query, language="sql")
                
                # Execute SQL
                try:
                    results = execute_sql(sql_query)
                    st.success("Query Results")
                    
                    if isinstance(results, list) and len(results) > 0:
                        df = pd.DataFrame(results)
                        st.dataframe(df)
                    else:
                        st.info("Query executed successfully but returned no results")
                except Exception as e:
                    st.error(f"Execution error: {str(e)}")
            except Exception as e:
                st.error(f"Generation error: {str(e)}")
    else:
        st.warning("Please enter a question first")
