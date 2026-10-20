# ---------------------------------------------------------
# PLAIN TEXT
#
# DELETE https://nexhealth.info/webhook_endpoints/{id}/webhook_subscriptions/{subscription_id}
#
# ---------------------------------------------------------
# WITH
#
# Path Params:
#   id = NexHealth Webhook Endpoint ID
#
#   subscription_id = NexHealth Webhook Subscription ID
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
# DELETE https://nexhealth.info/webhook_endpoints/123456/webhook_subscriptions/789012
#
# Successful Response:
#   204 No Content
#
# IMPORTANT:
#   This permanently deletes the webhook subscription.
#   Webhook deliveries for that subscription stop immediately.
# ---------------------------------------------------------


import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
webhook_endpoint_id = os.getenv("WEBHOOKENDPOINTID")
webhook_subscription_id = os.getenv("WEBHOOKSUBSCRIPTIONID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if webhook_endpoint_id is None:
    raise ValueError("WEBHOOKENDPOINTID is missing from .env")

if webhook_subscription_id is None:
    raise ValueError("WEBHOOKSUBSCRIPTIONID is missing from .env")

webhook_endpoint_id = int(webhook_endpoint_id)
webhook_subscription_id = int(webhook_subscription_id)

url = (
    f"https://nexhealth.info/webhook_endpoints/"
    f"{webhook_endpoint_id}/webhook_subscriptions/"
    f"{webhook_subscription_id}"
)

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
        "Webhook subscription deleted successfully.",
        style="bold green"
    )
else:
    try:
        console.print_json(data=response.json())
    except ValueError:
        console.print(response.text, style="yellow")

# Comments: Possible documented responses are 204, 400, 401, 403, 404, and 500