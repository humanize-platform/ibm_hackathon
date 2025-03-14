import json
import sqlite3
from typing import Dict, List, Any, Union

class JSONtoSQLite:
    def __init__(self, db_path: str):
        """Initialize the database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def load_json(self, json_path: str) -> Dict[str, Any]:
        """Load JSON data from a file."""
        with open(json_path, "r") as f:
            return json.load(f)

    def _infer_schema(self, data: Union[Dict, List]) -> Dict[str, List[tuple]]:
        """
        Infer database schema from JSON data.
        Returns a dictionary mapping table names to lists of column definitions.
        """
        schema = {}

        if isinstance(data, dict):
            table_name = "main_data"
            columns = [(key, self._get_sqlite_type(value)) for key, value in data.items()]
            schema[table_name] = columns

        elif isinstance(data, list) and data:
            table_name = "items"
            first_item = data[0]
            if isinstance(first_item, dict):
                columns = [("id", "INTEGER PRIMARY KEY")]
                columns.extend([(key, self._get_sqlite_type(value)) for key, value in first_item.items()])
                schema[table_name] = columns

        return schema

    def _get_sqlite_type(self, value: Any) -> str:
        """Determine SQLite data type based on Python data type."""
        if isinstance(value, (int, float)):
            return "REAL"
        elif isinstance(value, bool):
            return "INTEGER"
        elif isinstance(value, str):
            return "TEXT"
        elif isinstance(value, (dict, list)):
            return "TEXT"
        else:
            return "TEXT"

    def create_tables(self, schema: Dict[str, List[tuple]]):
        """Create tables based on the schema."""
        for table_name, columns in schema.items():
            column_defs = [f'"{col_name}" {col_type}' for col_name, col_type in columns]
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
            self.cursor.execute(create_stmt)
        self.conn.commit()

    def insert_data(self, data: Union[Dict, List], schema: Dict[str, List[tuple]]):
        """Insert all fields from JSON data into the database."""
        if isinstance(data, dict):
            table_name = "main_data"
            columns = [col[0] for col in schema[table_name]]
            placeholders = ", ".join(["?"] * len(columns))
            values = [json.dumps(data[col]) if isinstance(data[col], (dict, list)) else data[col] for col in columns]
            insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            self.cursor.execute(insert_stmt, values)

        elif isinstance(data, list) and data:
            table_name = "items"
            columns = [col[0] for col in schema[table_name] if col[0] != "id"]
            placeholders = ", ".join(["?"] * len(columns))
            for item in data:
                values = [json.dumps(item[col]) if isinstance(item[col], (dict, list)) else item[col] for col in columns]
                insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                self.cursor.execute(insert_stmt, values)
        
        self.conn.commit()

    def load_json_to_sqlite(self, json_path: str) -> Dict[str, List[tuple]]:
        """
        Load JSON data into SQLite database.
        Returns the schema used for the database.
        """
        data = self.load_json(json_path)
        schema = self._infer_schema(data)
        self.create_tables(schema)
        self.insert_data(data, schema)
        return schema

# Example usage
if __name__ == "__main__":
    json_file_path = "cloudant_query.json"
    db_path = "cloudant_query.db"

    loader = JSONtoSQLite(db_path)
    schema = loader.load_json_to_sqlite(json_file_path)

    print(f"Data loaded into SQLite database: {db_path}")
    print(f"Generated schema: {schema}")

    loader.close()