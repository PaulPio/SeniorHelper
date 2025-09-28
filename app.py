# app.py
# This is the backend server for our AI Smart Companion.
# It uses Flask to create a simple API that our frontend website can talk to.
# The core logic involves receiving a message, passing it to the Gemini agent,
# and handling the agent's decision to use tools.

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import the tools we defined in tools.py
import tools

# --- INITIALIZATION ---

# Load environment variables from .env file
load_dotenv()

# Configure the Flask web server
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow our frontend to make requests
CORS(app)

# Configure the Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=gemini_api_key)

# --- AGENT CONFIGURATION ---

# Define the system prompt for the agent's persona and instructions
SYSTEM_PROMPT = """
You are a friendly and helpful AI assistant designed for senior citizens.
Your name is 'Alex'.
Your primary role is to help the user with their daily schedule, provide weather information, and send alerts in an emergency.
You are conversational, patient, and use clear, simple language.
Do not make up information. If you don't know an answer, say so.
When using the 'send_emergency_alert' tool, confirm with the user before sending if the request is ambiguous. If the user's message is clearly an emergency (e.g., "I've fallen"), use the tool immediately.
"""

# Initialize the Gemini model with the system prompt and declare the available tools
# By enabling function calling, the model can decide which tool to use.
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT,
    tools=[
        tools.get_reminders,
        tools.get_weather,
        tools.send_emergency_alert
    ]
)

# Start a chat session with automatic function calling enabled.
# This simplifies our code by letting the library handle the tool execution loop.
chat_session = model.start_chat(enable_automatic_function_calling=True)

# --- API ENDPOINT ---

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles chat requests from the frontend.
    With automatic function calling enabled, this function is now much simpler.
    """
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        print(f"Received message: {user_message}")

        # Send the message to the model. The library will now automatically:
        # 1. Detect if the model wants to call a function.
        # 2. Execute that function from our 'tools' list.
        # 3. Send the function's result back to the model.
        # 4. Get the final, natural-language response.
        response = chat_session.send_message(user_message)
        
        # The final, user-facing text is directly available in the .text attribute.
        agent_response_text = response.text

        print(f"Sending response: {agent_response_text}")
        return jsonify({"response": agent_response_text})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

