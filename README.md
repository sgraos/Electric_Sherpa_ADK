# Electric_Sherpa_ADK
Electric Sherpa EV user support application built on Google ADK

## Introduction
This is the Electric Sherpa EV user support application build using Google Agent Development Kit.
It has the following features:
1. It allows the user to ask questions of their EV manual (EV models currently supported: Hyundai Ioniq, Hyundai Ioniq5, Hyundai Ioniq6, Kia Niro, Kia EV6)
2. It provides a list of nearest charging stations based on the user's address
3. It provides a list of nearest Kia and Hyundai service stations

## How to Install

1. Create and start a virtual environment using:
_python -m venv .venv_
_source .venv/bin/activate_
2. Clone this repository into your local directory
3. Create an environment file with the following variables:

  a.  GOOGLE_GENAI_USE_VERTEXAI=1 (0 for Gemini Developer API)

  b.  GOOGLE_API_KEY=<your Gemini API Key>

  c.  GOOGLE_CLOUD_PROJECT=<your cloud project ID>

  d.  GOOGLE_CLOUD_LOCATION=use-central1

  e.  GMAPS_API_KEY=<your Google Maps API key>

4. Install all the python libraries using the following command:
  _pip install -r requirements.txt_

## How to Use

There are 3 options for using:
1. **Using Streamlit GUI**: In terminal run
    _streamlit run agent_team_v6.py_
2. **Using Terminal Interface**: In terminal run
    _python agent_team_terminal.py_
3. **Live Link:**
    https://ev-driver-support-app-251571508738.us-central1.run.app
   
