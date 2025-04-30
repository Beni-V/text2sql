import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from db_service import get_detailed_schema_information

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Retrieve detailed schema information
schema_info = get_detailed_schema_information()
schema_json = json.dumps(schema_info, indent=2)

PROMPT_TEMPLATE = """
You are an expert SQL assistant for Microsoft SQL Server.
Given a natural language question, generate an accurate SQL query.

Database schema (JSON format):
{schema_json}

Rules:
1. Return ONLY the raw SQL query
2. Don't include any explanations or markdown formatting
3. Use proper JOINs and WHERE clauses as needed
4. Include all relevant columns

Question: "{question}"

SQL:
"""

def generate_sql_query(question: str) -> str:
    """Generate SQL query from natural language question"""
    prompt = PROMPT_TEMPLATE.format(
        schema_json=schema_json,
        question=question
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a SQL expert"},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    
    # Clean up the response to get just the SQL
    sql = response.choices[0].message.content
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql
