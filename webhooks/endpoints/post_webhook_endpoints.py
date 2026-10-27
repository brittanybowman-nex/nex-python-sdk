# https://docs.nexhealth.com/reference/postwebhookendpoints

# ---------------------------------------------------------
# PLAIN TEXT
#
# POST https://nexhealth.info/webhook_endpoints
#
# ---------------------------------------------------------
# WITH
#
# Query Params:
#   None
#
# Body Params:
#   target_url = URL NexHealth will POST webhook events to
#                Required
#                Must use HTTPS in production
#
#   active = Whether the webhook endpoint is active
#            Optional boolean
#
# Headers:
#   accept = application/json
#   content-type = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# POST https://nexhealth.info/webhook_endpoints
#
# Body:
# {
#     "target_url": "https://yourapp.com/nexhealth/webhooks",
#     "active": true
# }
# ---------------------------------------------------------


import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
target_url = os.getenv("WEBHOOKURL")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if target_url is None:
    raise ValueError("WEBHOOKURL is missing from .env")

url = "https://nexhealth.info/webhook_endpoints"

params: dict[str, str | int | bool] = {
}

payload = {
    "target_url": target_url,
    "active": True
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.post(
    url,
    headers=headers,
    params=params,
    json=payload
)

if response.ok:
    console.print(
        f"Status Code: {response.status_code}",
        style="bold green"
    )
else:
    console.print(
        f"Status Code: {response.status_code}",
        style="bold red"
    )

console.print(
    f"Request URL: {response.url}",
    style="bold cyan"
)

try:
    console.print_json(data=response.json())
except ValueError:
    console.print(response.text, style="yellow")

# Comments: For local development, you'd typically need something that gives your computer a publicly reachable HTTPS URL, because NexHealth has to be able to send an inbound POST to it. In production, NexHealth explicitly requires target_url to use HTTPS. NexHealth Synchronizer 
# The response to this call is important because you'll use the newly created webhook endpoint's ID when you create subscriptions for events like appointment_updated or appointment_insertion.