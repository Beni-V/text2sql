import os
from openai import OpenAI
from dotenv import load_dotenv
from db_service import get_detailed_schema_information
import json

try:
    load_dotenv()
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
except KeyError as e:
    raise RuntimeError(
        f"Missing environment variable: {e}\n"
        "Please create a .env file with all required credentials.\n"
        "See .env.example for reference."
    )


# Retrieve detailed schema information
schema_info = get_detailed_schema_information()

# Convert schema to JSON string for the prompt
schema_json = json.dumps(schema_info, indent=2)

PROMPT_TEMPLATE = """
You are an expert SQL assistant.
Given a natural language question, generate a SQL query using
The db is a Microsoft SQL Server
The query must be a raw query without any prefixes or suffixes

Database schema (JSON format):
{schema_json}
END OF DATABASE SCHEMA

Question: "{question}"
"""


def generate_sql_query(question: str) -> str:
    prompt = PROMPT_TEMPLATE.format(schema_json=schema_json, question=question)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a SQL expert that generates perfect SQL queries",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content
