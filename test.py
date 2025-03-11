import json
from swarm_agents import getDBQueryString  # Make sure swarm_agents.py is in the same directory or in PYTHONPATH

from cloudant_search import query_cloudant


def test_getDBQueryString():
    user_query = "Find all users  whoes flowrate is less then 5 ltr"
    
    print("🔍 Sending user query to getDBQueryString...")
    mango_query_str = getDBQueryString(user_query)

    print("\n=== 🧠 Generated Mongo Query ===")
    print(mango_query_str)

    print("\n=== 🧪 Testing JSON validity ===")
    print(mango_query_str)
    print("🔍 Checking if the JSON is valid...")

    try:
        mango_query = json.loads(mango_query_str)
        print("\n✅ JSON is valid. You can now send it to query_cloudant().", mango_query)

        print("\n🔍 Querying Cloudant with the generated query...")
        results = query_cloudant(mango_query)
        print("\n=== 📦 Cloudant Query Results ===")
        print(json.dumps(results, indent=2))  # Pretty-print results

    except json.JSONDecodeError as e:
        print("\n❌ Invalid JSON returned.")
        print("Error:", str(e))


if __name__ == "__main__":
    test_getDBQueryString()
