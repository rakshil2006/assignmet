from flask import Flask, request, jsonify
import requests
import json
from argparse import RawTextHelpFormatter
import warnings

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

# Main block to run Flask app
if __name__ == "__main__":
    app.run(debug=True)
