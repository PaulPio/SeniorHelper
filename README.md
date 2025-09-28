AI Smart Companion for Seniors
A conversational AI agent built during a 2364-hour hackathon to provide senior citizens with a simple way to manage their day and get help in emergencies.

Live Demo
You can interact with our live, deployed application here:

https://seniorhelper.netlify.app/

You can also check a video of the demo in action here:
https://www.youtube.com/watch?v=mBz7OSK-2kA

The Problem Statement
As family members live farther apart and daily life becomes more complex, senior citizens living independently face significant challenges. They often juggle multiple medications and appointments while navigating technology that can be confusing and inaccessible. This can lead to missed medications, social isolation, and critical delays in getting help during an emergency.

Our Solution
The AI Smart Companion is a full-stack web application designed with simplicity and accessibility at its core. It provides a single, friendly interface where users can have a natural conversation with an intelligent agent named Alex.

Key Features:
Conversational Interface: Users can type or speak in plain English to get information.

Daily Reminders: The agent can provide a clear, consolidated list of the day's medication and appointment schedules.

Live Weather Updates: Users can ask for the current weather, helping them plan their day.

One-Command Emergency Alert: If the user expresses distress or asks for help, the agent instantly sends a customizable SMS alert to a pre-defined emergency contact via Twilio.

Architecture
This project was built using a modern, full-stack architecture. The frontend is completely decoupled from the backend, communicating via a REST API.

Frontend: A static, single-page web application built with HTML, Tailwind CSS, and vanilla JavaScript. It is hosted on Netlify for global scalability and continuous deployment.

Backend: A Python Flask server that hosts our intelligent agent. It exposes a single API endpoint to the frontend. It is deployed on Render.

The Agent (Brain): The core logic is powered by Google's Gemini model. It uses an agentic approach with function calling to reason about the user's request and autonomously decide which tool to use.

Key Technologies Used
Backend: Python, Flask, Gunicorn

AI: Google Generative AI (Gemini), Function Calling

Frontend: HTML, Tailwind CSS, JavaScript

APIs & Services: Twilio (for SMS), OpenWeatherMap (for weather)

Deployment: Render (for backend), Netlify (for frontend), GitHub (for version control)

Features we wanted to add but did not have time for it:
    - Tech & Wellness Tips
    - Login Feature
    - Quick-Action Buttons

How to Run This Project Locally
Clone the repository:

git clone git@github.com:PaulPio/SeniorHelper.git

Setup the Backend:

cd [project-folder]
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Create a .env file and add your API keys
flask run
