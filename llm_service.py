import os
from openai import OpenAI
from dotenv import load_dotenv

try:
    load_dotenv()  # Loads from .env in same directory
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
except KeyError as e:
    raise RuntimeError(
        f"Missing environment variable: {e}\n"
        "Please create a .env file with all required credentials.\n"
        "See .env.example for reference."
    )


PROMPT_TEMPLATE = """
You are an expert SQL assistant.
Given a natural language question, generate a SQL query using the AdventureWorks2022 database.
The db is a Microsoft SQL Server
the query must be a raw query without any prefixes or suffixes

Question: "{question}"

SQL:
"""


def generate_sql_query(question: str) -> str:
    prompt = PROMPT_TEMPLATE.format(question=question)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a SQL expert that generates perfect SQL queries",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()
