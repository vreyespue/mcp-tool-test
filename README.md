# MCP Time Tool

This project is a simple, self-contained example of an MCP-based "Time Tool" server. It's built with Python and Flask.

The server provides a single endpoint that an AI application can call to get the current date and time.

## Setup

1.  Make sure you have Python 3 and the Google Cloud CLI installed.
2.  Authenticate with Application Default Credentials using Vertex AI:
    ```bash
    gcloud auth application-default login
    gcloud auth application-default set-quota-project YOUR_PROJECT_ID
    gcloud services enable aiplatform.googleapis.com --project YOUR_PROJECT_ID
    ```
3.  Set the project for the client:
    ```bash
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    export GOOGLE_CLOUD_LOCATION=global
    ```
4.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
5.  Install the necessary dependencies from `requirements.txt`:
    ```bash
    python -m pip install -r requirements.txt
    ```

## Usage

1.  **Run the Server:**
    Start the MCP time tool server:
    ```bash
    python3 app.py
    ```
    The server will start and listen on `http://127.0.0.1:5000`.

2.  **Run the Client:**
    In a separate terminal, run the example client to send a request to the server:
    ```bash
    python3 client.py
    ```
    The client will send a request to the server and print the JSON response it receives.
