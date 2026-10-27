# https://docs.nexhealth.com/reference/patchwebhookendpointsid

# ---------------------------------------------------------
# PLAIN TEXT
#
# PATCH https://nexhealth.info/webhook_endpoints/{id}
#
# ---------------------------------------------------------
# WITH
#
# Path Params:
#   id = NexHealth Webhook Endpoint ID
#
# Query Params:
#   None
#
# Body Params:
#   target_url = URL NexHealth will POST webhook events to
#                Optional
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
# PATCH https://nexhealth.info/webhook_endpoints/123456
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
webhook_endpoint_id = os.getenv("WEBHOOKENDPOINTID")
target_url = os.getenv("WEBHOOKURL")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if webhook_endpoint_id is None:
    raise ValueError("WEBHOOKENDPOINTID is missing from .env")

if target_url is None:
    raise ValueError("WEBHOOKURL is missing from .env")

webhook_endpoint_id = int(webhook_endpoint_id)

url = f"https://nexhealth.info/webhook_endpoints/{webhook_endpoint_id}"

params: dict[str, str | int | bool] = {
}

payload = {
    "target_url": target_url,
    "active": True # or False
    # target_url": target_url
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.patch(
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

# Comments: Because this is a PATCH, you only need to send the field or fields you actually want to change. 
# The response includes the endpoint ID, target URL, secret key, active state, and timestamps.