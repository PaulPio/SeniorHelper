# tools.py
# This file contains the individual "tools" that our AI agent can use.
# Each function is a self-contained capability, like sending a text or fetching data.

import os
import requests
from twilio.rest import Client
from datetime import datetime

# --- Tool 1: Get Today's Reminders ---
def get_reminders():
    """
    Retrieves a list of pre-defined medication and appointment reminders for the current day.
    This function simulates fetching a daily schedule for the user.
    """
    # For a hackathon, hard-coding is faster and more reliable than a real database.
    # We can use the current date to make it feel dynamic.
    today_str = datetime.now().strftime("%A, %B %d")
    
    reminders = (
        f"Here is the schedule for today, {today_str}:\n"
        "1. At 9:00 AM: Take the morning blood pressure pill.\n"
        "2. At 2:00 PM: Doctor's appointment with Dr. Smith.\n"
        "3. At 8:00 PM: Take the evening cholesterol pill."
    )
    print("[Tool Called: get_reminders]") # For debugging in the backend console
    return reminders

# --- Tool 2: Get Current Weather ---
def get_weather(city: str):
    """
    Fetches the current weather for a specified city using the OpenWeatherMap API.

    Args:
        city (str): The city and country code, e.g., "Miami,US".
    """
    # Get the API key securely from the .env file
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: Weather API key is not configured."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial"  # Use Fahrenheit for temperature
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        data = response.json()
        
        temp = round(data['main']['temp'])
        description = data['weather'][0]['description']
        
        print(f"[Tool Called: get_weather for {city}]") # For debugging
        return f"The weather in {city} is currently {temp}°F and {description}."
    except requests.exceptions.RequestException as e:
        print(f"Error calling weather API: {e}")
        return "Sorry, I was unable to fetch the weather information at this time."
    except KeyError:
        return f"Sorry, I couldn't find weather data for {city}. Please check the city name."


# --- Tool 3: Send an Emergency Alert SMS ---
def send_emergency_alert(reason: str):
    """
    Sends an SMS message to a pre-defined emergency contact using Twilio.

    Args:
        reason (str): A brief message explaining the reason for the alert, provided by the user or agent.
    """
    # Get Twilio credentials securely from the .env file
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    emergency_contact = os.getenv("EMERGENCY_CONTACT_NUMBER")

    if not all([account_sid, auth_token, twilio_phone, emergency_contact]):
        return "Error: Twilio credentials are not fully configured."

    try:
        client = Client(account_sid, auth_token)
        
        message_body = (
            "AUTOMATED ALERT from the AI Smart Companion:\n"
            f"An emergency alert was triggered for the following reason: '{reason}'.\n"
            "Please check on your loved one immediately."
        )
        
        message = client.messages.create(
            to=emergency_contact,
            from_=twilio_phone,
            body=message_body
        )
        
        print(f"[Tool Called: send_emergency_alert. SID: {message.sid}]") # For debugging
        return "An emergency alert has been successfully sent to the primary contact."
    except Exception as e:
        print(f"Error sending SMS via Twilio: {e}")
        return "Sorry, I encountered an error and could not send the emergency alert."


"""
    How to use this file :

1.  **Save this code** as `tools.py` in your project folder.
2.  **Create the `.env` file** in the same folder and fill in all the required API keys and phone numbers.
3.  **Test each function individually.** Create a temporary `test_tools.py` file to call each function and make sure it works before integrating it with the main agent logic. For example:

    ```python
    # test_tools.py (temporary file)
    from dotenv import load_dotenv
    from tools import get_weather, send_emergency_alert

    load_dotenv()
    print(get_weather("Miami,US"))
    print(send_emergency_alert("This is a test from the hackathon setup."))
    
"""