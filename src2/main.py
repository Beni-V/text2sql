from flask import Flask, request, jsonify

from src2.infrastructure.config import EnvConfig
from src2.presentation.ui import UI
from src2.services.llm_text_to_sql_service import LLMTextToSQLService


def run_streamlit_app():
    """Run the Streamlit UI application."""
    # Create and render UI
    ui = UI()
    ui.render()


def create_flask_app():
    """Create a Flask application for API access."""
    app = Flask(__name__)

    # Create service
    text_to_sql_service = LLMTextToSQLService()

    @app.route("/ask", methods=["POST"])
    def ask():
        data = request.json
        question = data.get("question")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        try:
            sql = text_to_sql_service.generate_sql(question)

            if data.get("execute", False):
                result = text_to_sql_service.database_facade.execute_query(sql)
                return jsonify({"question": question, "sql": sql, "result": result})
            else:
                return jsonify({"question": question, "sql": sql})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
