
import json
import os
import sys
import threading
import time
import unittest

import requests
import uvicorn

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        # Start the server in a background thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(2)  # Give the server time to start

    def run_server(self):
        uvicorn.run(app, host="127.0.0.1", port=8000)

    def tearDown(self):
        # Clean up the database file after tests
        if os.path.exists("dataset.db"):
            os.remove("dataset.db")

    def test_full_workflow(self):
        # 1. Create a schema
        schema_data = {
            "name": "Test-Schema",
            "input_schema": {"type": "object", "properties": {"data": {"type": "string"}}},
            "output_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
        }
        response = requests.post("http://127.0.0.1:8000/schemas/", json=schema_data)
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["name"], "Test-Schema")
        self.assertIn("id", schema)
        schema_id = schema["id"]

        # 2. Create a dataset item
        item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input"},
            "output_data": {"result": "test_output"},
        }
        response = requests.post("http://127.0.0.1:8000/items/", json=item_data)
        self.assertEqual(response.status_code, 200)
        item = response.json()
        self.assertEqual(item["schema_id"], schema_id)
        self.assertIn("id", item)
        item_id = item["id"]

        # 3. Read the schema
        response = requests.get(f"http://127.0.0.1:8000/schemas/{schema_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test-Schema")

        # 4. Read the item
        response = requests.get(f"http://127.0.0.1:8000/items/{item_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["input_data"]["data"], "test_input")

        # 5. Update the schema
        updated_schema_data = {
            "name": "Test-Schema-Updated",
            "input_schema": {"type": "object", "properties": {"data": {"type": "string"}}},
            "output_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
        }
        response = requests.put(
            f"http://127.0.0.1:8000/schemas/{schema_id}", json=updated_schema_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test-Schema-Updated")

        # 6. Update the item
        updated_item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input_updated"},
            "output_data": {"result": "test_output_updated"},
        }
        response = requests.put(
            f"http://127.0.0.1:8000/items/{item_id}", json=updated_item_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["input_data"]["data"], "test_input_updated")

        # 7. Delete the item
        response = requests.delete(f"http://127.0.0.1:8000/items/{item_id}")
        self.assertEqual(response.status_code, 200)

        # 8. Delete the schema
        response = requests.delete(f"http://127.0.0.1:8000/schemas/{schema_id}")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
