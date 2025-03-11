import json
from swarm_agents import getDBQueryString  # Make sure swarm_agents.py is in the same directory or in PYTHONPATH


def test_getDBQueryString():
    user_query = "Find all users  who consumed more than 1000 liters of water"
    
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
    except json.JSONDecodeError as e:
        print("\n❌ Invalid JSON returned.")
        print("Error:", str(e))


if __name__ == "__main__":
    test_getDBQueryString()
