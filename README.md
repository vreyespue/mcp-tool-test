# MCP Time Tool

This project is a simple, self-contained example of an MCP-based "Time Tool" server. It's built with Python and Flask.

The server provides a single endpoint that an AI application can call to get the current date and time.

## Setup

1.  Make sure you have Python 3 installed.
2.  Install the necessary dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
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
