import os
import sys
from app import create_app
from app.database import db
from app.assistant.llm_engine import llm_engine

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Trigger asynchronous background model loading before starting server
    # use_reloader=False prevents duplicate model loading across reloader child processes
    print("[DisasterAI] Initiating LLM background loading at startup...")
    llm_engine.load_model_background()

    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() in ("true", "1", "yes")
    print(f"Starting Disaster AI Backend on http://localhost:{port} (debug={debug_mode}, use_reloader=False)")
    app.run(host="0.0.0.0", port=port, debug=debug_mode, use_reloader=False)
