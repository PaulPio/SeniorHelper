# tools.py
# This file contains the individual tools that our AI agent can use.
# Each function is a self-contained capability, like sending a text or fetching data.
# The Gemini model will read the docstring of each function to understand its purpose.

# Standard library imports
import os  # Used to access environment variables ( API keys)
from datetime import datetime  # Used to get the current date for dynamic reminders

# Third-party library imports
import requests  # A popular library for making HTTP requests to APIs ( OpenWeatherMap)
from twilio.rest import Client  # The official Twilio library to make sending SMS messages easy

#  Tool 1: Get Today's Reminders 
def get_reminders():
    """
    Retrieves a list of pre-defined medication and appointment reminders for the current day.
    This function simulates fetching a daily schedule for the user.
    The docstring is crucial as it's what the AI model reads to understand what this tool does.
    """
    # For a hackathon, hard-coding the schedule is faster and more reliable than setting up a database.
    # We use the datetime library to get the current date and format it nicely
    # to make the agent's response feel current and personalized.
    today_str = datetime.now().strftime("%A, %B %d")
    
    # We create a multi-line string that formats the schedule clearly for the user.
    reminders = (
        f"Here is the schedule for today, {today_str}:\n"
        "1. At 9:00 AM: Take the morning blood pressure pill.\n"
        "2. At 2:00 PM: Doctor's appointment with Dr. Smith.\n"
        "3. At 8:00 PM: Take the evening cholesterol pill."
    )
    # This print statement is for the backend developer's benefit. It will show up in the Render logs
    # every time this tool is successfully called by the agent, which is great for debugging.
    print("[Tool Called: get_reminders]")
    return reminders

# --- Tool 2: Get Current Weather ---
# The `: str` is a type hint. It tells the model (and other developers) that the 'city' argument must be a string.
def get_weather(city: str):
    """
    Fetches the current weather for a specified city using the OpenWeatherMap API.

    Args:
        city (str): The city and country code, e.g., "Miami,US".
    """
    # Securely retrieve the API key from the .env file. This keeps our secrets out of the code.
    api_key = os.getenv("OPENWEATHER_API_KEY")
    # A validation check to ensure the key was loaded correctly.
    if not api_key:
        return "Error: Weather API key is not configured."

    # The base URL for the OpenWeatherMap API endpoint we want to use.
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    # A dictionary of parameters to send with our request. This includes the city, our API key,
    # and setting the units to imperial (Fahrenheit).
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial"
    }

    # A try-except block for robust error handling. This prevents the entire application from crashing
    # if the API call fails for any reason (e.g., no internet, invalid API key).
    try:
        # The actual API call is made here using the requests library.
        response = requests.get(base_url, params=params)
        # This line will automatically raise an error if the API returns a bad status (like 404 Not Found or 401 Unauthorized).
        response.raise_for_status()
        # We parse the JSON response from the API into a Python dictionary.
        data = response.json()
        
        # We extract the specific pieces of information we need from the complex JSON response.
        temp = round(data['main']['temp'])
        description = data['weather'][0]['description']
        
        print(f"[Tool Called: get_weather for {city}]") # For debugging
        # We return a clean, human-readable string for the agent to use.
        return f"The weather in {city} is currently {temp}°F and {description}."
    except requests.exceptions.RequestException as e:
        # This catches network-related errors (e.g., no internet connection).
        print(f"Error calling weather API: {e}")
        return "Sorry, I was unable to fetch the weather information at this time."
    except KeyError:
        # This catches errors if the API response is missing expected data (e.g., for an invalid city).
        return f"Sorry, I couldn't find weather data for {city}. Please check the city name."


# --- Tool 3: Send an Emergency Alert SMS ---
def send_emergency_alert(reason: str):
    """
    Sends an SMS message to a pre-defined emergency contact using Twilio.

    Args:
        reason (str): A brief message explaining the reason for the alert, provided by the user or agent.
    """
    # Securely retrieve all necessary Twilio credentials from the .env file.
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    emergency_contact = os.getenv("EMERGENCY_CONTACT_NUMBER")

    # A validation check to ensure all four credentials are present before proceeding.
    if not all([account_sid, auth_token, twilio_phone, emergency_contact]):
        return "Error: Twilio credentials are not fully configured."

    try:
        # Initialize the Twilio client with our account credentials.
        client = Client(account_sid, auth_token)
        
        # We construct a clear and informative message body for the SMS.
        message_body = (
            "AUTOMATED ALERT from the AI Smart Companion:\n"
            f"An emergency alert was triggered for the following reason: '{reason}'.\n"
            "Please check on your loved one immediately."
        )
        
        # This is the line that actually sends the SMS.
        message = client.messages.create(
            to=emergency_contact,    # The number we are sending the message to.
            from_=twilio_phone,      # Special Twilio phone number.
            body=message_body
        )
        
        # The 'message.sid' is a unique ID for the sent message, useful for logging and debugging.
        print(f"[Tool Called: send_emergency_alert. SID: {message.sid}]")
        return "An emergency alert has been successfully sent to the primary contact."
    except Exception as e:
        # A general catch-all for any other errors that might occur during the Twilio process.
        print(f"Error sending SMS via Twilio: {e}")
        return "Sorry, I encountered an error and could not send the emergency alert."

