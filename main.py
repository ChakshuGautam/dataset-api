
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

# Database setup
DATABASE_URL = "dataset.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dataset_schemas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        input_schema TEXT NOT NULL,
        output_schema TEXT NOT NULL
    );
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dataset_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schema_id INTEGER NOT NULL,
        input_data TEXT NOT NULL,
        output_data TEXT NOT NULL,
        FOREIGN KEY (schema_id) REFERENCES dataset_schemas (id)
    );
    """)
    conn.commit()
    conn.close()

create_tables()

app = FastAPI()

# Pydantic models
class DatasetSchemaCreate(BaseModel):
    name: str
    input_schema: dict
    output_schema: dict

class DatasetSchema(DatasetSchemaCreate):
    id: int

class DatasetItemCreate(BaseModel):
    schema_id: int
    input_data: dict
    output_data: dict

class DatasetItem(DatasetItemCreate):
    id: int

# --- Dataset Schema CRUD ---

@app.post("/schemas/", response_model=DatasetSchema)
def create_schema(schema: DatasetSchemaCreate):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO dataset_schemas (name, input_schema, output_schema) VALUES (?, ?, ?)",
            (schema.name, json.dumps(schema.input_schema), json.dumps(schema.output_schema)),
        )
        conn.commit()
        return {**schema.model_dump(), "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Schema name already exists")
    finally:
        conn.close()

@app.get("/schemas/{schema_id}", response_model=DatasetSchema)
def read_schema(schema_id: int):
    conn = get_db_connection()
    schema = conn.execute("SELECT * FROM dataset_schemas WHERE id = ?", (schema_id,)).fetchone()
    conn.close()
    if schema is None:
        raise HTTPException(status_code=404, detail="Schema not found")
    return {
        "id": schema["id"],
        "name": schema["name"],
        "input_schema": json.loads(schema["input_schema"]),
        "output_schema": json.loads(schema["output_schema"]),
    }

@app.put("/schemas/{schema_id}", response_model=DatasetSchema)
def update_schema(schema_id: int, schema: DatasetSchemaCreate):
    conn = get_db_connection()
    conn.execute(
        "UPDATE dataset_schemas SET name = ?, input_schema = ?, output_schema = ? WHERE id = ?",
        (schema.name, json.dumps(schema.input_schema), json.dumps(schema.output_schema), schema_id),
    )
    conn.commit()
    conn.close()
    return {**schema.model_dump(), "id": schema_id}

@app.delete("/schemas/{schema_id}")
def delete_schema(schema_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM dataset_schemas WHERE id = ?", (schema_id,))
    conn.commit()
    conn.close()
    return {"message": "Schema deleted successfully"}

# --- Dataset Item CRUD ---

@app.post("/items/", response_model=DatasetItem)
def create_item(item: DatasetItemCreate):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO dataset_items (schema_id, input_data, output_data) VALUES (?, ?, ?)",
        (item.schema_id, json.dumps(item.input_data), json.dumps(item.output_data)),
    )
    conn.commit()
    return {**item.model_dump(), "id": cursor.lastrowid}

@app.get("/items/{item_id}", response_model=DatasetItem)
def read_item(item_id: int):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM dataset_items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "id": item["id"],
        "schema_id": item["schema_id"],
        "input_data": json.loads(item["input_data"]),
        "output_data": json.loads(item["output_data"]),
    }

@app.put("/items/{item_id}", response_model=DatasetItem)
def update_item(item_id: int, item: DatasetItemCreate):
    conn = get_db_connection()
    conn.execute(
        "UPDATE dataset_items SET schema_id = ?, input_data = ?, output_data = ? WHERE id = ?",
        (item.schema_id, json.dumps(item.input_data), json.dumps(item.output_data), item_id),
    )
    conn.commit()
    conn.close()
    return {**item.model_dump(), "id": item_id}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM dataset_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted successfully"}

