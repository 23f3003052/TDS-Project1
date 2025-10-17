import requests
import json

# Your local API endpoint
url = "https://tds-project1-mq1b.onrender.com"

# Test request
payload = {
    "email": "[email protected]",
    "secret": "your-secret-here",
    "task": "test-app-001",
    "round": 1,
    "nonce": "test-nonce-123",
    "brief": "Create a simple page that displays 'Hello World' in an h1 tag",
    "checks": [
        "Page displays Hello World",
        "Uses h1 tag"
    ],
    "evaluation_url": "https://httpbin.org/post",
    "attachments": []
}

# Send request
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")