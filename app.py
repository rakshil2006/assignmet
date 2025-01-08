from flask import Flask, request, jsonify
import requests
import argparse
import json
from argparse import RawTextHelpFormatter
import warnings

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "f0bccfc9-7daa-4036-9a97-967812bd8582"
FLOW_ID = "0f98cd62-6d8d-4823-b6a9-005bbd2301e1"
APPLICATION_TOKEN = "AstraCS:HtpwdZitcaILjbadGQRBRcGU:93c69278d7f6b287cd840f92763d6bdea147c22acdbd0ee811664c9990760dff"  # Replace with your valid token

# Default tweaks dictionary
TWEAKS = {
    "ChatInput-UooHX": {"input_value": "default query", "sender": "User"},
    "Prompt-zgYSd": {"context": "", "question": ""},
}

# Flask App
app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests by sending data to the LangFlow API.
    """
    data = request.json
    message = data.get('query', '')  # User query
    endpoint = data.get('endpoint', FLOW_ID)  # Use default FLOW_ID if endpoint is not specified
    tweaks = data.get('tweaks', TWEAKS)  # Optional tweaks for flow behavior

    # Prepare the request payload
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": tweaks,
    }
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json",
    }

    # Send the request to LangFlow
    try:
        response = requests.post(
            f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()  # Raise HTTP errors, if any
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error communicating with LangFlow", "details": str(e)}), 500

# CLI Utility
def run_flow(message: str, endpoint: str, tweaks: dict, output_type="chat", input_type="chat") -> dict:
    """
    Run a flow with a given message and optional tweaks.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
        "tweaks": tweaks,
    }
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    """
    CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="""Run a flow with a given message and optional tweaks.
        Run it like: python <script>.py "your message here" --endpoint "<endpoint>" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument("--endpoint", type=str, default=FLOW_ID, help="The endpoint ID or name of the flow")
    parser.add_argument("--tweaks", type=str, help="JSON string for tweaks", default=json.dumps(TWEAKS))

    args = parser.parse_args()
    try:
        tweaks = json.loads(args.tweaks)
    except json.JSONDecodeError:
        raise ValueError("Invalid tweaks JSON string")

    try:
        response = run_flow(args.message, args.endpoint, tweaks)
        print(json.dumps(response, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")

# Main block
if __name__ == "__main__":
    
    main()
    app.run(debug=True)
