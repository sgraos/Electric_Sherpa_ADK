import os
from google import genai
from google.cloud import aiplatform
import vertexai
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GOOGLE_CLOUD_LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
PROJECT_ID = GOOGLE_CLOUD_PROJECT
CORPORA_NAME = os.environ["CORPORA_NAME"]

vertexai.init(project=PROJECT_ID, location=GOOGLE_CLOUD_LOCATION)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=GOOGLE_CLOUD_LOCATION)

from vertexai.preview import rag

manual_corpus = rag.get_corpus(name=CORPORA_NAME)

rag_retrieval_tool = Tool(
    retrieval=Retrieval(
        vertex_rag_store=VertexRagStore(
            rag_corpora=[manual_corpus.name],
            similarity_top_k=10,
            vector_distance_threshold=0.5,
        )
    )
)

def get_manual_answer(car_model: str, prompt: str) -> str:
    '''
    It accepts a description of the problem as a prompt (for example "my car battery is not charging") and retrieves answers from electric vehicle manual.
    Vehicles supported are Hyundai Kona Electric, Hyundai Ionic, Hyundai Ioniq 5, 
    Hyundai Ioniq6, Kia Niro Electric, Kia EV6
    '''
    prompt = f"My car is a {car_model}." + prompt
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=prompt,
        config=GenerateContentConfig(tools=[rag_retrieval_tool]),
    )
    return response.text

