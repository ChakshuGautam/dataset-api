# Dataset API Documentation

This document provides instructions on how to use the Dataset API to manage schemas and dataset items.

## Prerequisites

Make sure the server is running:

```bash
cd /Users/__chaks__/learn/gemini-cli/dataset-api
uvicorn main:app --reload
```

## 1. Create a Dataset Schema

First, you need to define the structure of your dataset by creating a schema. The schema specifies the format for both the input and output data using JSON Schema.

Here is an example `curl` command to create a new schema for a simple question-answering dataset.

```bash
curl -X POST "http://127.0.0.1:8000/schemas/" \
-H "Content-Type: application/json" \
-d '{
  "name": "QA-Schema",
  "input_schema": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "The question to be answered."
      }
    },
    "required": ["question"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "answer": {
        "type": "string",
        "description": "The answer to the question."
      }
    },
    "required": ["answer"]
  }
}'
```

**Expected Response:**

The API will return the created schema object, including its new `id`.

```json
{
  "name": "QA-Schema",
  "input_schema": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "The question to be answered."
      }
    },
    "required": ["question"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "answer": {
        "type": "string",
        "description": "The answer to the question."
      }
    },
    "required": ["answer"]
  }
},
  "id": 1
}
```

## 2. Add a Dataset Item

Once you have a schema, you can add dataset items that conform to it. Use the `id` of the schema you created in the previous step (`"schema_id": 1`).

Here is an example `curl` command to add a new question-answer pair.

```bash
curl -X POST "http://127.0.0.1:8000/items/" \
-H "Content-Type: application/json" \
-d '{
  "schema_id": 1,
  "input_data": {
    "question": "What is the capital of France?"
  },
  "output_data": {
    "answer": "Paris"
  }
}'
```

**Expected Response:**

The API will return the created dataset item, including its new `id`.

```json
{
  "schema_id": 1,
  "input_data": {
    "question": "What is the capital of France?"
  },
  "output_data": {
    "answer": "Paris"
  },
  "id": 1
}
```
