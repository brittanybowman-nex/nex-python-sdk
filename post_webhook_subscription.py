# https://docs.nexhealth.com/reference/postwebhookendpointsidwebhooksubscriptions
#
# ---------------------------------------------------------
# PLAIN TEXT
#
# POST https://nexhealth.info/webhook_endpoints/{id}/webhook_subscriptions
#
# ---------------------------------------------------------
# WITH
#
# Path Params:
#   id = NexHealth Webhook Endpoint ID
#
# Query Params:
#   subdomain = NexHealth institution subdomain
#
#   IMPORTANT:
#   subdomain MUST be sent as a query parameter.
#   Sending subdomain in the JSON body returns 403.
#
#   subdomain must be omitted for:
#       LocationDataReadiness
#       Onboarding
#
# Body Params:
#   resource_type = Resource to subscribe to
#                   Required
#                   Case-sensitive
#                   Example: Appointment
#
#   event = Webhook event to listen for
#           Required
#           Case-sensitive
#           Example: appointment_updated
#
#   active = Whether the subscription is active
#            Optional boolean
#            Default: true
#
# Headers:
#   accept = application/json
#   content-type = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# POST https://nexhealth.info/webhook_endpoints/123456/webhook_subscriptions
#      ?subdomain=nexhealthsmiles
#
# Body:
# {
#     "resource_type": "Appointment",
#     "event": "appointment_updated",
#     "active": true
# }
#
# Successful Response:
#   201 Created
#
# NOTE:
#   The subscription is pinned to the API version used
#   when the subscription is created.
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
resource_type = os.getenv("WEBHOOKRESOURCETYPE")
webhook_event = os.getenv("WEBHOOKEVENT")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if webhook_endpoint_id is None:
    raise ValueError("WEBHOOKENDPOINTID is missing from .env")

if resource_type is None:
    raise ValueError("WEBHOOKRESOURCETYPE is missing from .env")

if webhook_event is None:
    raise ValueError("WEBHOOKEVENT is missing from .env")

webhook_endpoint_id = int(webhook_endpoint_id)

url = (
    f"https://nexhealth.info/webhook_endpoints/"
    f"{webhook_endpoint_id}/webhook_subscriptions"
)

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

payload = {
    "resource_type": resource_type, # Case Sensitive!
    "event": webhook_event,
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