import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import warnings
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

from manual_RAG import get_manual_answer
from maps_agent import get_charging_stations, get_Hyundai_service_stations, get_Kia_service_stations

import nest_asyncio
nest_asyncio.apply()
warnings.filterwarnings("ignore")

# --- Step 1: Import API keys from .env file ---

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GOOGLE_CLOUD_LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
GOOGLE_GENAI_USE_VERTEXAI=os.environ["GOOGLE_GENAI_USE_VERTEXAI"]
PROJECT_ID = GOOGLE_CLOUD_PROJECT

# --- Step 2: Define Model Used ---
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

# --- Step 4: Define agents ---

def create_charger_agent():
    try:
        charger_agent = Agent(
            name="charger_agent",
            model=AGENT_MODEL,
            description="Retrieves a list of the nearest charging points to the user. Each element in the list is a dictionary containing the address, coordinates (in latitude and longitude) and name of the location",
            instruction="You are the EV charger listing agent. Request the user's address. Pass this address to the function as the argument",
            tools=[get_charging_stations],
        )
        return charger_agent
    except Exception as e:
        print("Fatal error creating charger agent. Please check API keys and refresh.")

def create_Hyundai_service_agent():
    try:
        Hyundai_service_agent = Agent(
            name="Hyundai_service_agent",
            model=AGENT_MODEL,
            description="Retrieves a list of the nearest Hyundai service stations to the user. Each element in the list is a dictionary containing the address, coordinates (in latitude and longitude) and name of the location",
            instruction="You are the Hyundai service station listing agent. Request the user's address. Pass this address to the function as the argument",
            tools=[get_Hyundai_service_stations],
        )
        return Hyundai_service_agent
    except Exception as e:
        print("Fatal error creating Hyundai service agent. Please check API keys and refresh.")

def create_Kia_service_agent():
    try:
        Kia_service_agent = Agent(
            name="Kia_service_agent",
            model=AGENT_MODEL,
            description="Retrieves a list of the nearest Kia service stations to the user. Each element in the list is a dictionary containing the address, coordinates (in latitude and longitude) and name of the location",
            instruction="You are the Kia service station listing agent. Request the user's address. Pass this address to the function as the argument",
            tools=[get_Kia_service_stations],
        )
        return Kia_service_agent
    except Exception as e:
        print("Fatal error creating Hyundai service agent. Please check API keys and refresh.")

def create_manual_agent_team(_charger_agent, _Hyundai_service_agent, _Kia_service_agent):
    if not _charger_agent or not _Hyundai_service_agent or not _Kia_service_agent:
        print("Cannot create main agent. One or more agents missing. Please check API keys and refresh")
    try:
        manual_agent_team = Agent(
            name="manual_agent_team",
            model=AGENT_MODEL,
            description="Main contributor agent: handles the manual lookup and delegates charging point and Kia and Hyundai service station lookups.",
            instruction=(
                "If the user has any questions about their electric vehicle, prompt the user to provide their car make and model (for example, 'Kia EV6'). Provide the make and model and the user prompt as inputs to 'manual_agent' tool."
                "If the user wants to find the nearest charging stations, prompt the user to provide their address. Provide this address as an argument to the 'charger_agent' tool. The chargers returned are listed in order of proximity. Parse through the output and provide a neat response to the user."
                "If the user wants to find the nearest Hyundai service stations, prompt the user to provide their address. Provide this address as an argument to the 'Hyundai_service_agent' tool. The locations returned are listed in order of proximity. Parse through the output and provide a neat response to the user."
                "If the user wants to find the nearest Kia service stations, prompt the user to provide their address. Provide this address as an argument to the 'Kia_service_agent' tool. The locations returned are listed in order of proximity. Parse through the output and provide a neat response to the user."
                "Otherwise, say you can't help with that."
            ),
            tools=[get_manual_answer],
            sub_agents=[_charger_agent, _Hyundai_service_agent, _Kia_service_agent],
        )
        return manual_agent_team
    except Exception as e:
        print("Cannot create main agent. One or more agents missing. Please check API keys and refresh")

charger_agent = create_charger_agent()
Kia_service_agent = create_Kia_service_agent()
Hyundai_service_agent = create_Hyundai_service_agent()
manual_agent_team = create_manual_agent_team(charger_agent, Hyundai_service_agent, Kia_service_agent)

# --- Step 5: Run Execution Loop ---
async def run():
    user_id = "EV_user"
    session_id = "session_001"
    app_name = "EV_manual_support_app"
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    runner = Runner(agent=manual_agent_team, app_name=app_name, session_service=session_service)

    print("How can I help you with your EV today? (Enter 'exit' or 'quit' to quit)")
    while True:
        query = input("User: ")
        if(query.lower() in ("exit", "quit")):
            break
        content = Content(role="user", parts=[Part(text=query)])
        response_text = ""

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.content and event.content.parts:
                response_text += "".join(part.text or "" for part in event.content.parts)
        print("Electric_Sherpa:", response_text)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"❌ Error: {e}")
