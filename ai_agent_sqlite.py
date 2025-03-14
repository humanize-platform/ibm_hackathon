import sqlite3
import json
from typing import Dict, List, Any, Optional
import os
import re
from langchain_ibm import WatsonxLLM


class SQLiteDataAgent:
    def __init__(self, db_path: str):
        """
        Initialize the AI agent for SQLite data extraction.

        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Initialize Watsonx LLM client
        self.llm = WatsonxLLM(
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

        # Analyze database schema for context
        self.schema = self._analyze_schema()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def _analyze_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Analyze the database schema and return a structured representation.
        """
        schema = {}

        # Get all tables
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()

        for table in tables:
            table_name = table[0]

            # Skip SQLite internal tables
            if table_name.startswith("sqlite_"):
                continue

            # Get columns for each table
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = self.cursor.fetchall()

            # Format column info
            col_info = [
                {
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "pk": bool(col[5]),
                }
                for col in columns
            ]

            # Get a sample of data
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_rows = self.cursor.fetchall()
            sample_data = [dict(row) for row in sample_rows]

            # Store table schema
            schema[table_name] = {"columns": col_info, "sample_data": sample_data}

        return schema

    def _generate_query(self, user_request: str) -> str:
        """
        Use WatsonX to generate an SQL query based on the user's request.
        """
        schema_description = json.dumps(self.schema, indent=2)

        prompt = f"""
        You are an AI assistant that translates natural language queries into SQL queries for a SQLite database.
        
        The database has the following schema:
        {schema_description}
        
        User request: {user_request}
        
        Generate a valid SQLite SQL query to fulfill this request. Return only the SQL query with no additional explanation.
        """

        response = self.llm.invoke(prompt).strip()

        # Extract only the SQL query using regex
        match = re.search(r"SELECT .*", response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(0)
        else:
            raise ValueError("Invalid SQL query generated: " + response)

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute an SQL query and return the results.
        """
        try:
            self.cursor.execute(sql_query)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Error executing SQL query: {e}")

    def extract_data(self, user_request: str) -> Dict[str, Any]:
        """
        Process a natural language request for data extraction.

        Args:
            user_request: Natural language request for data

        Returns:
            Dictionary containing the SQL query, results, and any extra information
        """
        try:
            sql_query = self._generate_query(user_request)
            results = self.execute_query(sql_query)

            insight_prompt = f"""
            You are an AI data analyst. Analyze these query results and extract key insights.
            
            User request: {user_request}
            
            SQL query used: {sql_query}
            
            Query results: {json.dumps(results, indent=2)}
            
            Provide 3-5 insights based on patterns, trends, or outliers found in the data.
            """

            insight_response = self.llm.invoke(insight_prompt)
            insights = insight_response.strip()

            return {
                "user_request": user_request,
                "sql_query": sql_query,
                "results": results,
                "insights": insights,
                "row_count": len(results),
            }
        except Exception as e:
            return {"error": str(e), "user_request": user_request}


def getUsageData(user_request):
    db_path = "cloudant_query.db"
    agent = SQLiteDataAgent(db_path)
    # user_request = "What are the top 5 items in our database?"
    # user_request = "When last time the flow was recorded?"
    result = agent.extract_data(user_request)
    response = json.dumps(result, indent=2)
    agent.close()
    return response
