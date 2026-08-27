import json
import os

import requests
from google import genai
from google.genai import types

# The URL of the running MCP server
SERVER_URL = "http://127.0.0.1:5003/mcp"
GEMINI_FLASH_MODEL = "gemini-3.7-flash"

# Configure Gemini through Vertex AI using Application Default Credentials (ADC).
google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
if not google_cloud_project:
    print("ERROR: GOOGLE_CLOUD_PROJECT environment variable not set.")
    print("Set it to the Google Cloud project that has Vertex AI enabled.")
    exit(1)
client = genai.Client(
    vertexai=True,
    project=google_cloud_project,
    location=google_cloud_location,
)

# Define the tool for Gemini to understand
# This mirrors the 'get_current_time' functionality we expect from our MCP server
time_tool_spec = types.FunctionDeclaration(
    name="get_current_time",
    description="Gets the current UTC date and time.",
    parameters=types.Schema(type=types.Type.OBJECT, properties={}, required=[]),
)
tool_config = types.GenerateContentConfig(
    tools=[types.Tool(functionDeclarations=[time_tool_spec])],
    automaticFunctionCalling=types.AutomaticFunctionCallingConfig(disable=True),
)


def call_mcp_tool(tool_name, parameters):
    """
    Calls the specified MCP tool with the given parameters.
    """
    print(f"\n--- MCP TOOL CALL ---")
    print(f"INFO: Application is calling the '{tool_name}' tool via MCP.")

    mcp_request = {"tool_name": tool_name, "parameters": parameters}

    try:
        response = requests.post(SERVER_URL, json=mcp_request)
        response.raise_for_status()
        mcp_response = response.json()
        print(
            f"INFO: Received response from MCP tool:\n{json.dumps(mcp_response, indent=2)}"
        )
        return mcp_response
    except requests.exceptions.RequestException as e:
        print(f"ERROR: An error occurred while calling the MCP tool: {e}")
        return {"status": "error", "error_message": str(e)}


def call_gemini_llm(user_prompt, tool_response=None):
    """
    Interacts with the Gemini Flash model.
    Handles both initial intent detection and final response generation.
    """
    print(f"\n--- GEMINI LLM INTERACTION ---")
    chat_history = []
    # The chat history is crucial for Gemini to understand context and previous tool outputs.
    # For a simple single-turn interaction, we can re-initialize or manage it.
    # For this example, we'll create a new chat for each interaction for simplicity.

    if tool_response:
        # If we have a tool response, add the original user prompt and the tool response
        # to the history so the model can generate the final answer.
        chat_history.append(
            types.Content(role="user", parts=[types.Part(text=user_prompt)])
        )
        chat_history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_response["tool_name"],
                            response=tool_response["result"],
                        )
                    )
                ],
            )
        )
        print("INFO: Sending tool response back to Gemini for final answer.")
    else:
        # Initial prompt to detect intent
        chat_history.append(
            types.Content(role="user", parts=[types.Part(text=user_prompt)])
        )
        print(f"INFO: Sending user prompt to Gemini: '{user_prompt}'")

    chat = client.chats.create(
        model=GEMINI_FLASH_MODEL,
        config=tool_config,
        history=chat_history,
    )  # We will manually handle tool calls
    response = chat.send_message(
        user_prompt
        if not tool_response
        else "Generate final answer based on tool output."
    )

    # Process model's response
    # For tool calling, the response will have a function_call part
    # For text generation, the response will have a parts[0].text part

    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.function_call:
                print(f"INFO: Gemini wants to call a tool: {part.function_call.name}")
                return {
                    "tool_call": {
                        "tool_name": part.function_call.name,
                        "parameters": {
                            k: v for k, v in part.function_call.args.items()
                        },
                    }
                }
            elif part.text:
                print(f"INFO: Gemini responded with text.")
                return part.text

    return "Gemini did not provide a clear response (tool call or text)."


def main():
    """
    Runs the full end-to-end workflow using Gemini Flash.
    """
    print("--- START OF WORKFLOW (Gemini Flash) ---")
    print(f"INFO: Using Gemini model: {GEMINI_FLASH_MODEL}")
    user_prompt = "What time is it in UTC?"  # Example user query

    # 1. The application sends the user prompt to Gemini to get an intent
    llm_response = call_gemini_llm(user_prompt)

    # 2. The application checks if Gemini wants to call a tool
    if isinstance(llm_response, dict) and "tool_call" in llm_response:
        tool_call_details = llm_response["tool_call"]
        tool_name = tool_call_details["tool_name"]
        parameters = tool_call_details["parameters"]

        # 3. The application calls the appropriate tool via MCP
        mcp_tool_result = call_mcp_tool(tool_name, parameters)

        # 4. The application sends the tool's result back to Gemini for final processing
        if mcp_tool_result and mcp_tool_result.get("status") == "success":
            final_answer = call_gemini_llm(user_prompt, tool_response=mcp_tool_result)
        else:
            final_answer = "Sorry, I tried to check the time, but the tool failed."
    else:
        # Gemini handled the request directly with text
        final_answer = llm_response

    # 5. The final, user-facing answer is displayed
    print("\n--- FINAL RESPONSE ---")
    print(final_answer)
    print("\n--- END OF WORKFLOW ---")


if __name__ == "__main__":
    main()
