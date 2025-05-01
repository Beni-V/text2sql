from src.main import run_streamlit_app, create_flask_app
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Check if UI is enabled
    enable_ui = os.getenv("ENABLE_UI", "true").lower() == "true"

    if enable_ui:
        # Run Streamlit app
        run_streamlit_app()
    else:
        # Run Flask app
        app = create_flask_app()
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
