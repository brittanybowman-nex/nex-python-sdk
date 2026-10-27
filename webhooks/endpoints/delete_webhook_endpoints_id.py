# https://docs.nexhealth.com/reference/deletewebhookendpointsid

# ---------------------------------------------------------
# PLAIN TEXT
#
# DELETE https://nexhealth.info/webhook_endpoints/{id}
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
# Body:
#   None
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# DELETE https://nexhealth.info/webhook_endpoints/123456
#
# This endpoint permanently deletes a webhook endpoint belonging to the authenticated API user 
# Successful Response:
#   204 No Content
# ---------------------------------------------------------


import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
webhook_endpoint_id = os.getenv("WEBHOOKENDPOINTID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if webhook_endpoint_id is None:
    raise ValueError("WEBHOOKENDPOINTID is missing from .env")

webhook_endpoint_id = int(webhook_endpoint_id)

url = f"https://nexhealth.info/webhook_endpoints/{webhook_endpoint_id}"

params: dict[str, str | int | bool] = {
}

headers = {
    "accept": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.delete(
    url,
    headers=headers,
    params=params
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

if response.status_code == 204:
    console.print(
        "Webhook endpoint deleted successfully.",
        style="bold green"
    )
else:
    try:
        console.print_json(data=response.json())
    except ValueError:
        console.print(response.text, style="yellow")

# Comments: The important difference on this one is that success returns no body, 
# so we explicitly check for 204 instead of trying to parse JSON. NexHealth also 
# documents 401, 404, and 500 as possible error responses.