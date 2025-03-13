from cloudant_search import search_cloudant
from langchain_ibm import ChatWatsonx, WatsonxLLM
from langchain.prompts import ChatPromptTemplate
import os
import io
from dotenv import load_dotenv
import uuid
from PIL import Image

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

granite_model = WatsonxLLM(
    model_id="ibm/granite-8b-code-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=os.getenv("WATSONX_PROJECTKEY"),
    params={
        "decoding_method": "sample",
        "max_new_tokens": 200,
        "min_new_tokens": 10,
        "temperature": 0.3,
        "top_k": 40,
        "top_p": 0.9,
    },
)


# Tool to search data from IBM Cloudant DB against the query
def searchWaterData(query: str):
    """You will retrieve data from IBM Cloudant database against user's query on
    his water utilization and leakage analysis.
    You will receive JSON formatted data.

    Args:
        query (str): User query
    """
    pass #TODO


# Tool to detect water leakage in user's system
def detectLeakage():
    """You will detect if there is any leakage in user's water system.
    You will fetch data for last 24hrs and if there is continuous flow detected you will mark that as leakage.
    If leakage is detected, return from when the leakage started.
    Otherwise, return 'NO LEAKAGE'.
    """
    pass


# Tool to calculate total water consumption in user's system
def getTotalConsumption(query: str):
    """You will retrieve water data based on user query. You will sum up the pulse count and return that.
    Args:
        query (str): _description_
    """
    pass


# Tool to notify user through WhatsApp
def notifyUser(notification_message: str):
    """You will send notification on water consumption and leakage to user's whatsapp number.
    You will get the notification message from agent and will send that to WhatsApp.

    Args:
        notification_message (str): Notification message that needs to be sent through WhatsApp.
    """
    sendWhatsAppMessage(notification_message)


# Tool to crawl few websites and fetch generic weter related questions
def referWaterGuidlines(query: str):
    """You will retrieve generic weter related questions which user asks for.
    These questions are NOT related to user's personal consumptions,
    rather on generic guidelines and vision from United Nations and World Health Org.
    If you dont know the answer just say that. Dont try to generate arbitrarily."""
    return getDataFromChroma(query)


# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_WaterGuidelineRetriever = create_handoff_tool(
    agent_name="WaterGuidelineRetriever",
    description="Transfer user to the WaterGuidelineRetriever assistant that can search for water docs over web.",
)

# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_WaterUsageRetriever = create_handoff_tool(
    agent_name="WaterUsageRetriever",
    description="Transfer user to the WaterUsageRetriever assistant that can search for database for invidual water consumption data.",
)

search_water_usage_agent = create_react_agent(
    model,
    [
        searchWaterData,
        detectLeakage,
        getTotalConsumption,
        notifyUser,
        transfer_to_WaterGuidelineRetriever,
    ],
    prompt=system_prompt.prompt_search_water_usage,
    name="WaterUsageRetriever",
)

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
