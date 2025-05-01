import json


class SQLGenerationPrompt:
    DEFAULT_TEMPLATE = """
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

    def __init__(self, template: str = None):
        self._template = template or self.DEFAULT_TEMPLATE

    def format(self, **kwargs) -> str:
        # Schema can be a dict that needs JSON conversion
        if "schema_json" in kwargs and not isinstance(kwargs["schema_json"], str):
            kwargs["schema_json"] = json.dumps(kwargs["schema_json"], indent=2)

        return self._template.format(**kwargs)

    def get_raw_template(self) -> str:
        return self._template
