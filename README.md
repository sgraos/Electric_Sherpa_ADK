# Electric_Sherpa_ADK
Electric Sherpa EV user support application built on Google ADK

## How to Use

1. Create and start a virtual environment using:
_python -m venv .venv_
_source .venv/bin/activate_
2. Clone this repository into your local directory
3. Create an environment file with the following variables:
  a.  GOOGLE_GENAI_USE_VERTEXAI=1 (0 for Gemini Developer API)
  b.  GOOGLE_API_KEY=<your Gemini API Key>
  c.  GOOGLE_CLOUD_PROJECT=<your cloud project ID>
  d.  GOOGLE_CLOUD_LOCATION=use-central1
  e.  CORPORA_NAME=<your RAG corpus name with the embeddings for the manual>
  f.  GMAPS_API_KEY=<your Google Maps API key>
4. Install all the python libraries using the following command:
  _pip install -r requirements.txt_
