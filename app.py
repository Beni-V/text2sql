from flask import Flask, request, jsonify
from llm_service import generate_sql_query
from db_service import execute_sql

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    sql_query = generate_sql_query(question)

    # Optional: if you want to show the SQL only without executing
    if data.get("only_sql"):
        return jsonify({"sql_query": sql_query})

    # Execute the query on the database
    try:
        results = execute_sql(sql_query)
        return jsonify({
            "sql_query": sql_query,
            "results": results
        })
    except Exception as e:
        return jsonify({
            "sql_query": sql_query,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
