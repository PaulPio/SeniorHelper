# app.py
# This is the backend server for our AI Smart Companion.
# It uses Flask to create a simple API that the frontend website can talk to.
# The core logic involves receiving a message, passing it to the Gemini agent,
# and handling the agent's decision to use tools.

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import the tools we defined in tools.py. This makes our functions available to this script.
import tools

# --- INITIALIZATION ---

# load_dotenv() reads the .env file in the same directory and loads the key-value pairs
# into the environment, so os.getenv() can access them.
load_dotenv()

# Create an instance of the Flask class. This is the foundation of our web application.
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS). This is a security feature that browsers enforce.
# By enabling it, we are telling the browser it's okay for our Netlify frontend to make requests to our Render backend.
CORS(app)

# Securely retrieve the Gemini API key from the environment variables.
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    # If the key is not found, raise an error to stop the application from running without it.
    raise ValueError("GEMINI_API_KEY not found in .env file.")
# Configure the google-generativeai library with our API key.
genai.configure(api_key=gemini_api_key)

# --- AGENT CONFIGURATION ---

# The system prompt is a set of high-level instructions that guides the AI's persona and behavior.
# It tells the model how to act, what its name is, and the rules it should follow.
SYSTEM_PROMPT = """
You are a friendly and helpful AI assistant designed for senior citizens.
Your name is 'Alex'.
Your primary role is to help the user with their daily schedule, provide weather information, and send alerts in an emergency.
You are conversational, patient, and use clear, simple language.
Do not make up information. If you don't know an answer, say so.
When using the 'send_emergency_alert' tool, confirm with the user before sending if the request is ambiguous. If the user's message is clearly an emergency (e.g., "I've fallen"), use the tool immediately.
"""

# Initialize the Gemini model. We specify the model name, provide its system instructions,
# and most importantly, we declare the list of Python functions from tools.py that it's allowed to use.
# The model will read the docstrings of these functions to understand what they do.
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',
    system_instruction=SYSTEM_PROMPT,
    tools=[ #Functions created for the chatbot to use
        tools.get_reminders,
        tools.get_weather,
        tools.send_emergency_alert
    ]
)

# Start a chat session with the model. This allows the model to remember the context of the conversation.
chat_session = model.start_chat()

# --- API ENDPOINT ---

# @app.route defines a URL endpoint. Our frontend will send requests to 'http://your-backend-url.com/api/chat'.
# methods=['POST'] specifies that this endpoint only accepts POST requests, which is standard for sending data.
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles chat requests from the frontend.
    Receives a user's message, sends it to the Gemini agent,
    and returns the agent's response.
    """
    # A try-except block is used for error handling. If anything goes wrong inside the 'try'
    # block, the code in the 'except' block will run, preventing the server from crashing.
    try:
        # request.get_json() parses the incoming request body from the frontend as JSON.
        data = request.get_json()
        # We extract the user's message from the JSON object.
        user_message = data.get("message")

        # Basic validation to ensure a message was actually sent.
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        print(f"Received message: {user_message}") # For backend debugging in the Render logs.

        # This is the first call to the Gemini model, sending the user's message.
        response = chat_session.send_message(user_message)
        
        # --- AGENT'S REASONING LOOP ---
        # After the first call, we check if the model's response includes a request to use a tool.
        if response.function_calls:
            # The model has decided to use a tool. We now need to execute it.
            function_call = response.function_calls[0]
            tool_name = function_call.name
            tool_args = function_call.args
            
            print(f"Agent wants to call tool: {tool_name} with args: {tool_args}") # Debugging

            # getattr() is a powerful Python function that gets a function from a module by its string name.
            # E.g., if tool_name is "get_weather", this becomes tools.get_weather
            tool_function = getattr(tools, tool_name)
            
            # The **tool_args syntax unpacks the arguments the model provided into the function call.
            # E.g., tool_function(city="Miami,US")
            tool_output = tool_function(**tool_args)

            # This is the second call to the model. We send the output from our tool back to the agent.
            # This allows the agent to take the raw tool output (e.g., weather data)
            # and formulate a natural, human-readable response.
            final_response = chat_session.send_message(
                genai.Part(function_response=genai.FunctionResponse(
                    name=tool_name,
                    response={"output": tool_output}
                ))
            )
            # The agent's final, user-facing message is in the .text attribute of this second response.
            agent_response_text = final_response.text
        else:
            # If the model didn't need to use a tool, its response is simply in the .text attribute.
            # This happens for general conversation (e.g., user says "hello").
            agent_response_text = response.text

        print(f"Sending response: {agent_response_text}") # Debugging
        # We send the final text response back to the frontend in a JSON object.
        return jsonify({"response": agent_response_text})

    except Exception as e:
        print(f"An error occurred: {e}")
        # If any error occurred, we send a generic error message back to the frontend.
        return jsonify({"error": "An internal error occurred."}), 500

# --- MAIN EXECUTION ---
# This standard Python construct ensures that the Flask development server runs only
# when the script is executed directly (not when imported as a module).
if __name__ == '__main__':
    # app.run() starts the web server.
    # `debug=True` enables auto-reloading when you save the file, which is great for development.
    # `host='0.0.0.0'` makes the server accessible from other devices on your local network.
    app.run(host='0.0.0.0', port=5000, debug=True)

