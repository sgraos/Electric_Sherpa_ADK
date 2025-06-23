import os
import time
import asyncio
import streamlit as st
import warnings
import nest_asyncio

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part

from manual_RAG import get_manual_answer
from maps_agent import get_charging_stations, get_Hyundai_service_stations, get_Kia_service_stations

nest_asyncio.apply()
load_dotenv()

# --- ENV VARIABLES ---
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GOOGLE_CLOUD_LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
GOOGLE_GENAI_USE_VERTEXAI = os.environ["GOOGLE_GENAI_USE_VERTEXAI"]
PROJECT_ID = GOOGLE_CLOUD_PROJECT
AGENT_MODEL = "gemini-2.0-flash"

# --- STREAMLIT CONFIG ---
st.set_page_config(page_title="EV driver support app", layout="wide")
st.title("EV driver support app agent")
st.subheader("Supports Hyundai & Kia electric models")
st.write("(Please wait for response if you see the 'running' status')")

# --- CONSTANTS ---
APP_NAME = "EV_manual_support_app"
USER_ID = "EV_user"
INITIAL_STATE = {"EV_model": "Hyundai_Ioniq5"}

warnings.filterwarnings("ignore")

# --- CACHE AGENT + RUNNER SETUP ---
@st.cache_resource
def get_runner_and_service():
    agent = create_manual_agent_team()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    return runner, session_service

# --- CREATE AGENT TEAM ---
@st.cache_resource
def create_manual_agent_team():
    charger_agent = Agent(
        name="charger_agent",
        model=AGENT_MODEL,
        description="Find nearby EV charging stations",
        instruction="Ask user for their address. Pass to tool.",
        tools=[get_charging_stations],
    )
    hyundai_agent = Agent(
        name="Hyundai_service_agent",
        model=AGENT_MODEL,
        description="Find nearby Hyundai EV service centers",
        instruction="Ask user for their address. Pass to tool.",
        tools=[get_Hyundai_service_stations],
    )
    kia_agent = Agent(
        name="Kia_service_agent",
        model=AGENT_MODEL,
        description="Find nearby Kia EV service centers",
        instruction="Ask user for their address. Pass to tool.",
        tools=[get_Kia_service_stations],
    )
    return Agent(
        name="manual_agent_team",
        model=AGENT_MODEL,
        description="Main EV assistant agent",
        instruction=(
            "Handle all EV support. Route to tools or sub-agents based on user intent. "
            "Ask user for car model or address where needed."
        ),
        tools=[get_manual_answer],
        sub_agents=[charger_agent, hyundai_agent, kia_agent],
    )

# --- ASYNC INIT HANDLER ---
async def initialize_adk_async():
    runner, session_service = get_runner_and_service()

    if "ev_adk_session_id" not in st.session_state:
        session_id = f"ev_session_{int(time.time())}_{os.urandom(3).hex()}"
        st.session_state["ev_adk_session_id"] = session_id

        await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
            state=INITIAL_STATE
        )
    else:
        session_id = st.session_state["ev_adk_session_id"]
        if not session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id):
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id,
                state=INITIAL_STATE
            )

    return runner, st.session_state["ev_adk_session_id"]

# --- ASYNC RESPONSE HANDLER ---
async def handle_agent_query(runner, session_id, user_input):
    content = Content(role="user", parts=[Part(text=user_input)])
    final_response = "[No response]"
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = "".join(part.text or "" for part in event.content.parts)
                elif event.error_message:
                    final_response = f"Agent Error: {event.error_message}"
                elif event.actions and event.actions.escalate:
                    final_response = f"Escalated: {event.error_message or 'No reason'}"
                break
    except Exception as e:
        final_response = f"Error on handle_agent_query: {e}"
    return final_response

# --- MAIN LOGIC ---
async def main():
    runner, session_id = await initialize_adk_async()

    # st.write("🆔 Current Session Info:")
    # st.code(f"Session ID: {session_id}", language="python")
    # st.write("🔧 Agent Runner Info:")
    # st.write(f"Runner ID: {id(runner)}")
    # st.write(f"Number of tools: {len(runner.agent.tools) if runner.agent.tools else 0}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Handle user input
    if query := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("Getting response..."):
            response = await handle_agent_query(runner, session_id, query)
            st.session_state.messages.append({"role": "Electric Sherpa", "content": response})
            with st.chat_message("Electric Sherpa"):
                st.markdown(response)

# --- RUN ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise e