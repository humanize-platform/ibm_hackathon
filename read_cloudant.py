import json
import datetime
from langchain_ibm import WatsonxLLM
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

watsonx_api_key = os.getenv("WATSONX_APIKEY")
os.environ["WATSONX_APIKEY"] = watsonx_api_key

llm = WatsonxLLM(
    model_id="ibm/granite-20b-code-instruct",
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

# Load JSON Data
with open("cloudant_query.json", "r") as file:
    cloudant_data = json.load(file)


def generate_json_query(user_query):
    """Uses LLM to generate a JSON filter from user input."""

    prompt_template = ChatPromptTemplate.from_template(
        """
    Convert the following user request into a JSON filter to search the dataset.

    User Request: "{user_query}"

    The JSON filter should match the structure of the dataset:
    {{
        "timestamp": "YYYY-MM-DD HH:MM:SS",
        "flow_rate": FLOAT,
        "pulses": INT
    }}

    Example:
    - User asks: "Show me all readings where flow rate was above 1 L/min today"
    - JSON Filter:
    {{
        "flow_rate": {{ "$gt": 1 }},
        "timestamp": {{ "$gte": "2025-03-10 00:00:00" }}
    }}

    Generate only the JSON query without any explanation or additional text. Only valida json formatted response.
    """
    )

    formatted_prompt = prompt_template.format(user_query=user_query)
    query = llm(formatted_prompt).strip()
    print("query", query)
    return json.loads(query)


def filter_json_data(query):
    """Filters JSON data based on the generated query."""
    filtered_results = []

    for record in cloudant_data:
        match = True
        for key, condition in query.items():
            if key in record:
                value = record[key]

                if isinstance(condition, dict):
                    for op, threshold in condition.items():
                        if op == "$gt" and not (value > threshold):
                            match = False
                        elif op == "$gte" and not (value >= threshold):
                            match = False
                        elif op == "$lt" and not (value < threshold):
                            match = False
                        elif op == "$lte" and not (value <= threshold):
                            match = False
                elif record[key] != condition:
                    match = False

        if match:
            filtered_results.append(record)

    return filtered_results


def summarize_results(results):
    """Uses LLM to generate a natural language summary of the query results."""
    if not results:
        return "No matching records found."

    summary_prompt = ChatPromptTemplate.from_template(
        """
    Given the following JSON sensor data:

    {data}

    Summarize the key trends and insights in plain language.
    """
    )

    response = llm(summary_prompt.format(data=json.dumps(results, indent=2)))
    return response.strip()


def query_water_data(user_query):
    """Processes user query, retrieves data from JSON, and summarizes response."""

    json_query = generate_json_query(user_query)  # Step 1: Convert to JSON filter
    print("json_query", json_query)
    filtered_data = filter_json_data(json_query)  # Step 2: Query local JSON
    print("filtered_data", filtered_data)
    summary = summarize_results(filtered_data)  # Step 3: Summarize output

    return summary


# Example Usage
# user_query = "Show me readings where pulses were greater than 5 in the last hour."
# response = query_json(user_query)
# print(response)
