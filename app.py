import json
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)

# This is a mock tool definition that the server knows about.
# In a real MCP system, this might be more dynamic.
TOOL_DEF = {
    "tool_name": "get_current_time",
    "description": "Gets the current UTC date and time.",
    "parameters": [],
}


@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """
    This endpoint simulates a generic MCP server.
    It expects a request asking to use a specific tool.
    """
    request_data = request.get_json()

    if not request_data or "tool_name" not in request_data:
        return jsonify({"error": "Invalid MCP request, 'tool_name' is required."}), 400

    tool_name = request_data.get("tool_name")

    # Check if the requested tool is our time tool
    if tool_name == TOOL_DEF["tool_name"]:
        # Execute the tool's logic
        current_time_utc = datetime.now(timezone.utc)
        time_str = current_time_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

        # Format the response according to a simplified MCP-like structure
        response_data = {
            "tool_name": tool_name,
            "status": "success",
            "result": {"time": time_str},
        }
        return jsonify(response_data)
    else:
        # If the tool is not found, return an error
        return jsonify(
            {
                "tool_name": tool_name,
                "status": "error",
                "error_message": f"Tool '{tool_name}' not found.",
            }
        ), 404


@app.route("/", methods=["GET"])
def index():
    """
    A simple index route to show that the server is running
    and list available tools.
    """
    return f"""
    <h1>MCP Time Tool Server</h1>
    <p>This server is running. It exposes a /mcp endpoint for tool calls.</p>
    <h2>Available Tools:</h2>
    <pre>{json.dumps(TOOL_DEF, indent=2)}</pre>
    """


if __name__ == "__main__":
    # Run the Flask app
    # Use port 5003 to avoid potential conflicts with other common dev ports.
    app.run(host="0.0.0.0", port=5003, debug=True)
