from flask import Flask, request, jsonify
from main import ask_assistant, run_chat
import uuid
import sys

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.json
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    reply = ask_assistant(session_id, user_message)
    return jsonify({"reply": reply, "session_id": session_id})

if __name__ == "__main__":
    
        app.run(debug=True, port=5000)