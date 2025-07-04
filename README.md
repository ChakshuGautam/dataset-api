# Dataset API

This project provides a simple FastAPI-based API for managing datasets. A dataset consists of a schema and items that conform to that schema.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

To run the API server, use the following command:

```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the end-to-end tests, first install the testing requirements:

```bash
pip install pytest requests
```

Then, run the tests using `pytest`:

```bash
pytest
```

## API Documentation

For detailed API documentation, including `curl` examples for creating schemas and dataset items, please see the [docs.md](docs.md) file.

## CI/CD

A GitHub Actions workflow is configured to run the tests automatically on every push and pull request to the `main` branch. See `.github/workflows/test.yml` for details.
