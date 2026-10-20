# https://docs.nexhealth.com/reference/patchwebhookendpointsidwebhooksubscriptionssubscriptionid
#
# ---------------------------------------------------------
# PLAIN TEXT
#
# PATCH https://nexhealth.info/webhook_endpoints/{id}/webhook_subscriptions/{subscription_id}
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
#   subdomain = NexHealth institution subdomain
#               Required
#
#   IMPORTANT:
#   subdomain is required even when the subscription itself
#   is not scoped to an institution, such as Onboarding.
#
# Body Params:
#   active = Pause or resume webhook deliveries
#            true  = active
#            false = paused
#            Optional
#
#   new_endpoint_id = Move this subscription to another
#                     webhook endpoint owned by the same
#                     API user
#                     Optional
#
#   IMPORTANT:
#   If new_endpoint_id is used successfully, future requests
#   for this subscription must use the NEW webhook endpoint
#   ID in the URL path.
#
# Headers:
#   accept = application/json
#   content-type = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# PATCH https://nexhealth.info/webhook_endpoints/123456/webhook_subscriptions/789012
#       ?subdomain=nexhealthsmiles
#
# Body:
# {
#     "active": false
# }
#
# Successful Response:
#   200 OK
# ---------------------------------------------------------


import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
webhook_endpoint_id = os.getenv("WEBHOOKENDPOINTID")
webhook_subscription_id = os.getenv("WEBHOOKSUBSCRIPTIONID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

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
    "subdomain": subdomain
}

payload = {
    "active": False,
     # "new_endpoint_id": 654321
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

# Comments: If new_endpoint_id belongs to another one of your webhook endpoints, 
# NexHealth moves the subscription there; after that, you must use the new endpoint 
# ID in the URL for future GET/PATCH/DELETE calls on that subscription. 
# If the endpoint ID is not yours, NexHealth returns 404.