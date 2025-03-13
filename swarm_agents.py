from cloudant_search import search_cloudant
from langchain_ibm import ChatWatsonx, WatsonxLLM
from langchain.prompts import ChatPromptTemplate
import os
import io
from dotenv import load_dotenv
import uuid
from PIL import Image

from read_cloudant import query_water_data
from read_vector import getDataFromChroma
import system_prompt
from utility import sendWhatsAppMessage

load_dotenv()

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

watsonx_api_key = os.getenv("WATSONX_APIKEY")
os.environ["WATSONX_APIKEY"] = watsonx_api_key

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "IBM-HACKATHON-HUMANIZE"

parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

model = ChatWatsonx(
    model_id="mistralai/mistral-large",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=os.getenv("WATSONX_PROJECTKEY"),
    params=parameters,
)


# Tool to search data from IBM Cloudant DB against the query
def searchWaterData(query: str):
    """You will retrieve and analyse user's water consumption data based on user's query."""
    return query_water_data(query)


# Tool to crawl few websites and fetch generic weter related questions
def referWaterGuidlines(query: str):
    """You will retrieve generic weter related questions which user asks for.
    You will call RAG with the user's query to retrieve information."""
    return getDataFromChroma(query)


# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_WaterGuidelineRetriever = create_handoff_tool(
    agent_name="WaterGuidelineRetriever",
    description="Transfer user to the Water_Guideline_Retriever assistant that can search for water docs.",
)

# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_WaterUsageRetriever = create_handoff_tool(
    agent_name="WaterUsageRetriever",
    description="Transfer user to the Water_Usage_Retriever assistant that can search for user's water consumption data.",
)

# React agent (Reason + Act) for Water usage record search
search_water_usage_agent = create_react_agent(
    model,
    [
        searchWaterData,
        transfer_to_WaterGuidelineRetriever,
    ],
    prompt=system_prompt.prompt_search_water_usage,
    name="WaterUsageRetriever",
)

# React agent (Reason + Act) for Water Guideline documents search
search_water_guideline_agent = create_react_agent(
    model,
    [referWaterGuidlines, transfer_to_WaterUsageRetriever],
    prompt=system_prompt.prompt_search_water_guideline,
    name="WaterGuidelineRetriever",
)

checkpointer = InMemorySaver()

workflow = create_swarm(
    [search_water_usage_agent, search_water_guideline_agent],
    default_active_agent="WaterUsageRetriever",
)

app = workflow.compile(checkpointer=checkpointer)


# Dynamically generate a thread_id for each user session
def get_config():
    thread_id = str(uuid.uuid4())
    return {"configurable": {"thread_id": thread_id}}


# Example of invoking the app with a dynamic thread ID
config = get_config()

# Generate workflow diagram
# image_bytes = app.get_graph().draw_mermaid_png()
# image = Image.open(io.BytesIO(image_bytes))
# image.save("water_agents.png")
