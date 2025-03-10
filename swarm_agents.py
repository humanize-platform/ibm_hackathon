from cloudant_search import query_cloudant
from langchain_ibm import ChatWatsonx
import os
import io
from dotenv import load_dotenv
import uuid

import system_prompt
load_dotenv()

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

watsonx_api_key = os.getenv("WATSONX_APIKEY")
os.environ["WATSONX_APIKEY"] = watsonx_api_key

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
    """ You will retrieve data from IBM Cloudant database against user's query on water utilization 
    and leakage analysis. You will receive JSON formatted data. 
    If you dont know the answerm just say that. Dont try to generate arbitrarily."""
    return query_cloudant(query);


# Too to crawl few websites and fetch generic weter related questions
def referWaterGuidlines():
    """ You will crawl few websites and fetch generic weter related questions which user asks for. 
    If you dont know the answerm just say that. Dont try to generate arbitrarily."""
    return "water is purified"


# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_SearchWebAgent = create_handoff_tool(
    agent_name="SearchWebAgent",
    description="Transfer user to the SearchWebAgent assistant that can search for water docs over web.",
)

# Tool to transfer user to the TestScriptAgent from the HowToAgent
transfer_to_SearchDBAgent = create_handoff_tool(
    agent_name="SearchDBAgent",
    description="Transfer user to the SearchDBAgent assistant that can search for database for invidual water consumption data.",
)

search_db_agent = create_react_agent(
    model,
    [searchWaterData, transfer_to_SearchWebAgent],
    prompt=system_prompt.prompt_search_db_agent,
    name="SearchDBAgent",
)

search_web_agent = create_react_agent(
    model,
    [referWaterGuidlines, transfer_to_SearchDBAgent],
    prompt=system_prompt.prompt_search_web_agent,
    name="SearchWebAgent",
)

checkpointer = InMemorySaver()

workflow = create_swarm(
    [search_db_agent, search_web_agent], default_active_agent="SearchDBAgent"
)

app = workflow.compile(checkpointer=checkpointer)

# Dynamically generate a thread_id for each user session
def get_config():
    thread_id = str(uuid.uuid4())
    return {"configurable": {"thread_id": thread_id}}


# Example of invoking the app with a dynamic thread ID
config = get_config()