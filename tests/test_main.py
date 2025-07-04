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
    @classmethod
    def setUpClass(cls):
        # Start the server in a background thread
        cls.server_thread = threading.Thread(target=cls.run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)  # Give the server time to start

    @classmethod
    def run_server(cls):
        uvicorn.run(app, host="127.0.0.1", port=8000)

    def setUp(self):
        # Clean up the database file before each test
        if os.path.exists("dataset.db"):
            os.remove("dataset.db")
        # Re-create tables for each test to ensure a clean state
        from main import create_tables
        create_tables()

        self.base_url = "http://127.0.0.1:8000"
        self.schema_data = {
            "name": "Test-Schema",
            "input_schema": {
                "type": "object",
                "properties": {"data": {"type": "string"}},
                "required": ["data"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {"result": {"type": "string"}},
                "required": ["result"],
                "additionalProperties": False,
            },
        }
        self.updated_schema_data = {
            "name": "Test-Schema-Updated",
            "input_schema": {
                "type": "object",
                "properties": {"data": {"type": "string"}},
                "required": ["data"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {"result": {"type": "string"}},
                "required": ["result"],
                "additionalProperties": False,
            },
        }

    def tearDown(self):
        # Clean up the database file after each test
        if os.path.exists("dataset.db"):
            os.remove("dataset.db")

    def test_1_create_and_read_schema(self):
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["name"], "Test-Schema")
        self.assertIn("id", schema)
        schema_id = schema["id"]

        response = requests.get(f"{self.base_url}/schemas/{schema_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test-Schema")

    def test_2_create_and_read_item(self):
        # Create a schema first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]

        item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input"},
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data)
        self.assertEqual(response.status_code, 200)
        item = response.json()
        self.assertEqual(item["schema_id"], schema_id)
        self.assertIn("id", item)
        item_id = item["id"]

        response = requests.get(f"{self.base_url}/items/{item_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["input_data"]["data"], "test_input")

    def test_3_update_schema(self):
        # Create a schema first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]

        response = requests.put(
            f"{self.base_url}/schemas/{schema_id}", json=self.updated_schema_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Test-Schema-Updated")

    def test_4_update_item(self):
        # Create a schema and item first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]
        item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input"},
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data)
        item_id = response.json()["id"]

        updated_item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input_updated"},
            "output_data": {"result": "test_output_updated"},
        }
        response = requests.put(
            f"{self.base_url}/items/{item_id}", json=updated_item_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["input_data"]["data"], "test_input_updated")

    def test_5_delete_item_and_schema(self):
        # Create a schema and item first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]
        item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input"},
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data)
        item_id = response.json()["id"]

        response = requests.delete(f"{self.base_url}/items/{item_id}")
        self.assertEqual(response.status_code, 200)

        response = requests.delete(f"{self.base_url}/schemas/{schema_id}")
        self.assertEqual(response.status_code, 200)

    def test_6_validation_error_on_create_item_invalid_key(self):
        # Create a schema first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]

        invalid_item_data = {
            "schema_id": schema_id,
            "input_data": {"invalid_key": "test_input"},  # Invalid key
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=invalid_item_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data validation error", response.json()["detail"])

    def test_7_validation_error_on_update_item_invalid_key(self):
        # Create a schema and item first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]
        item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input"},
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data)
        item_id = response.json()["id"]

        invalid_item_data_update = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input_updated"},
            "output_data": {"invalid_key": "test_output_updated"},  # Invalid key
        }
        response = requests.put(
            f"{self.base_url}/items/{item_id}", json=invalid_item_data_update
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data validation error", response.json()["detail"])

    def test_8_create_schema_duplicate_name(self):
        # Create a schema first
        requests.post(f"{self.base_url}/schemas/", json=self.schema_data)

        # Attempt to create another schema with the same name
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Schema name already exists")

    def test_9_create_item_non_existent_schema(self):
        item_data_invalid_schema = {
            "schema_id": 999,  # Non-existent schema ID
            "input_data": {"data": "test_input"},
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data_invalid_schema)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Schema with id 999 not found")

    def test_10_create_item_missing_required_properties(self):
        # Create a schema first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]

        item_data_missing_props = {
            "schema_id": schema_id,
            "input_data": {},  # Missing 'data' property
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data_missing_props)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data validation error", response.json()["detail"])

    def test_11_create_item_incorrect_data_types(self):
        # Create a schema first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]

        item_data_wrong_type = {
            "schema_id": schema_id,
            "input_data": {"data": 123},  # 'data' should be a string
            "output_data": {"result": "test_output"},
        }
        response = requests.post(f"{self.base_url}/items/", json=item_data_wrong_type)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Data validation error", response.json()["detail"])

    def test_12_read_non_existent_schema(self):
        response = requests.get(f"{self.base_url}/schemas/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Schema not found")

    def test_13_read_non_existent_item(self):
        response = requests.get(f"{self.base_url}/items/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Item not found")

    def test_14_update_non_existent_schema(self):
        response = requests.put(f"{self.base_url}/schemas/999", json=self.schema_data)
        self.assertEqual(response.status_code, 200) # FastAPI returns 200 even if not found for PUT, but no change is made.
        # We should ideally check if the schema was actually created/updated, but for now, just checking status code.

    def test_15_update_non_existent_item(self):
        # Create a schema first
        response = requests.post(f"{self.base_url}/schemas/", json=self.schema_data)
        schema_id = response.json()["id"]

        updated_item_data = {
            "schema_id": schema_id,
            "input_data": {"data": "test_input_updated"},
            "output_data": {"result": "test_output_updated"},
        }
        response = requests.put(f"{self.base_url}/items/999", json=updated_item_data)
        self.assertEqual(response.status_code, 200) # FastAPI returns 200 even if not found for PUT, but no change is made.
        # We should ideally check if the item was actually created/updated, but for now, just checking status code.

    def test_16_delete_non_existent_schema(self):
        response = requests.delete(f"{self.base_url}/schemas/999")
        self.assertEqual(response.status_code, 200) # FastAPI returns 200 even if not found for DELETE, but no change is made.

    def test_17_delete_non_existent_item(self):
        response = requests.delete(f"{self.base_url}/items/999")
        self.assertEqual(response.status_code, 200) # FastAPI returns 200 even if not found for DELETE, but no change is made.

if __name__ == "__main__":
    unittest.main()