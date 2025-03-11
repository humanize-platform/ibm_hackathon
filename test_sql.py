import json
from swarm_agents import getDBQueryString

from cloudant_search import search_cloudant


def test_getDBQueryString():
    user_query = "Find all users  whoes flowrate is less then 5 ltr"

    print("🔍 Sending user query to getDBQueryString...")
    query_str = getDBQueryString(user_query)

    print("\n=== 🧠 Generated Mongo Query ===")
    print(query_str)

    print("🔍 Checking if the JSON is valid...")

    try:
        json_query = json.loads(query_str)
        print(
            "\n✅ JSON is valid. You can now send it to query_cloudant().", json_query
        )

        print("\n🔍 Querying Cloudant with the generated query...")
        results = search_cloudant(json_query)
        print("\n=== 📦 Cloudant Query Results ===")
        print(json.dumps(results, indent=2))  # Pretty-print results

    except json.JSONDecodeError as e:
        print("\n❌ Invalid JSON returned.")
        print("Error:", str(e))


if __name__ == "__main__":
    test_getDBQueryString()
