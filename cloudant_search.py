import os
import json
import requests
from cloudant.client import Cloudant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IBM Cloudant Credentials (Now loaded from .env for security)
CLOUDANT_APIKEY = os.getenv("CLOUDANT_APIKEY")
CLOUDANT_URL = os.getenv("CLOUDANT_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")


# Function to Authenticate and Get IAM Token
def get_iam_token():
    IAM_URL = "https://iam.cloud.ibm.com/identity/token"
    auth_response = requests.post(
        IAM_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": CLOUDANT_APIKEY,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    auth_response.raise_for_status()  # Raise error if authentication fails
    return auth_response.json()["access_token"]


# Function to Query Cloudant
def search_cloudant(selector):
    """Query IBM Cloudant using a given selector and return results."""

    print("Trying to search cloudant based on the query below...")
    print(selector)

    # Get IAM Token
    iam_token = get_iam_token()

    # Connect to Cloudant
    client = Cloudant.iam(None, api_key=CLOUDANT_APIKEY, url=CLOUDANT_URL, connect=True)
    db = client[DATABASE_NAME]

    selected_fields = ["timestamp", "flow_rate", "pulses", "location"]

    # Perform Query
    query_result = db.get_query_result(selector, fields=selected_fields)

    # Close Connection
    client.disconnect()

    return list(query_result)  # Convert cursor to list


# Example Usage (Only runs if executed directly)
if __name__ == "__main__":
    sample_query = {"timestamp": {"$gt": "2025-03-10"}}
    results = search_cloudant(sample_query)
    print(json.dumps(results, indent=2))  # Pretty-print results

    # from cloudant_search import query_cloudant
    # query = {"flow_rate": {"$gt": 10}}  # Get records where flow_rate > 10
    # results = query_cloudant(query, limit=5)
    # print(results)  # Print the retrieved data
