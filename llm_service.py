import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key="okMyFriend")

PROMPT_TEMPLATE = """
You are an expert SQL assistant.
Given a natural language question, generate a SQL query using the AdventureWorks2022 database.

Question: "{question}"

SQL:
"""

def generate_sql_query(question: str) -> str:
    prompt = PROMPT_TEMPLATE.format(question=question)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    sql_query = response.choices[0].message.content
    return sql_query.strip()