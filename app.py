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

# Import the tools defined in tools.py
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
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    system_instruction=SYSTEM_PROMPT,
    tools=[
        tools.get_reminders,
        tools.get_weather,
        tools.send_emergency_alert
    ]
)

# Start a chat session
chat_session = model.start_chat()

# --- API ENDPOINT ---

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles chat requests from the frontend.
    Receives a user's message, sends it to the Gemini agent,
    and returns the agent's response.
    """
    try:
        # Get the user's message from the request body
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        print(f"Received message: {user_message}") # For backend debugging

        # Send the message to the Gemini model
        response = chat_session.send_message(user_message)
        
        # --- AGENT'S REASONING LOOP ---
        # Check if the model decided to use a tool
        if response.function_calls:
            # The model wants to use a tool. We now execute it.
            function_call = response.function_calls[0]
            tool_name = function_call.name
            tool_args = function_call.args
            
            print(f"Agent wants to call tool: {tool_name} with args: {tool_args}") # Debugging

            # Find the actual Python function to call from our tools.py
            tool_function = getattr(tools, tool_name)
            
            # Call the function with the arguments provided by the model
            tool_output = tool_function(**tool_args)

            # Send the tool's output back to the model so it can formulate a final response
            final_response = chat_session.send_message(
                genai.Part(function_response=genai.FunctionResponse(
                    name=tool_name,
                    response={"output": tool_output}
                ))
            )
            # The final response is the text part of the model's new message
            agent_response_text = final_response.text
        else:
            # The model responded with text directly, no tool was needed.
            agent_response_text = response.text

        print(f"Sending response: {agent_response_text}") # Debugging
        return jsonify({"response": agent_response_text})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Run the Flask app. `debug=True` allows for auto-reloading when you save changes.
    # The host '0.0.0.0' makes it accessible on your local network.
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
### **How to Use This File:**

1.  **Save this code** as `app.py` in the same folder as your `tools.py` and `.env` files.
2.  **Make sure your virtual environment is active.**
3.  **Run the server** from your terminal by typing:
    ```bash
    flask run
    ```
    or
    ```bash
    python app.py
    
"""