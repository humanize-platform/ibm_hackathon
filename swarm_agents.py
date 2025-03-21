from langchain_ibm import ChatWatsonx
import os
import io
from dotenv import load_dotenv
import uuid
from PIL import Image

from read_vector import getGuidelineData

# from read_vector_cloudant import getUsageData
from ai_agent_sqlite import getUsageData
import system_prompt
from utility import sendWhatsAppMessage, getQualityData
from langchain_core.tools import tool

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
    "max_new_tokens": 500,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

model = ChatWatsonx(
    model_id="ibm/granite-3-8b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=os.getenv("WATSONX_PROJECTKEY"),
    params=parameters,
)


# Tool to analyse PH and TDS values from the water data
@tool
def analysePH(query: str):
    """You will analyse user's water PH and TDS count and will explain in simple terms.
    You will also provide the user with the information on how to maintain the PH and TDS count in water.
    Provide low cost remedies to improve the PH and TDS count in water."""
    return getQualityData(query)


# Tool to search data from IBM Cloudant DB against the query
@tool
def searchWaterData(query: str):
    """You will retrieve and analyse user's water consumption data based on user's query."""
    return getUsageData(query)


# Tool to crawl few websites and fetch generic weter related questions
@tool
def referWaterGuidlines(query: str):
    """You will retrieve generic weter related questions which user asks for.
    You will call RAG with the user's query to retrieve information."""
    return getGuidelineData(query)


# Tool to notify user or community on some message around SDG 6 water usage
@tool
def notifyCommunity(query: str):
    """You will receive a message that to be broadcasted over WhatsApp.
    You will receive the message that to be broadcasted.
    Send the message over WhatsApp/
    """
    return sendWhatsAppMessage(query)


# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_WaterGuidelineRetriever = create_handoff_tool(
    agent_name="WaterGuidelineRetriever",
    description="Transfer user to the WaterGuidelineRetriever assistant that can search for water guideline docs.",
)

# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_WaterUsageRetriever = create_handoff_tool(
    agent_name="WaterUsageRetriever",
    description="Transfer user to the WaterUsageRetriever assistant that can search for user's water consumption records.",
)

# React agent (Reason + Act) for Water usage record search
search_water_usage_agent = create_react_agent(
    model,
    [
        searchWaterData,
        notifyCommunity,
        analysePH,
        transfer_to_WaterGuidelineRetriever,
    ],
    prompt=system_prompt.prompt_search_water_usage,
    name="WaterUsageRetriever",
)

# React agent (Reason + Act) for Water Guideline documents search
search_water_guideline_agent = create_react_agent(
    model,
    [referWaterGuidlines, notifyCommunity, analysePH, transfer_to_WaterUsageRetriever],
    prompt=system_prompt.prompt_search_water_guideline,
    name="WaterGuidelineRetriever",
)

checkpointer = InMemorySaver()

workflow = create_swarm(
    [search_water_usage_agent, search_water_guideline_agent],
    default_active_agent="WaterUsageRetriever",
)

app = workflow.compile(checkpointer=checkpointer)


def invoke_with_language(input_data, config=None):
    language = input_data.get("language", "English")
    messages = input_data.get("messages", [])

    # Add language instruction to the first message
    if messages and len(messages) > 0:
        first_message = messages[0]
        language_instruction = f"Please respond in {language}. "
        first_message["content"] = language_instruction + first_message["content"]

    return app.invoke({"messages": messages}, config=config)


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
