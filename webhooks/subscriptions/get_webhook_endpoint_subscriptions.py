# ---------------------------------------------------------
# PLAIN TEXT
#
# GET https://nexhealth.info/webhook_endpoints/{id}/webhook_subscriptions
#
# ---------------------------------------------------------
# WITH
#
# Path Params:
#   id = NexHealth Webhook Endpoint ID
#
# Optional Query Params:
#   subdomain = Scope subscriptions to a specific institution
#
#   resource_type = Filter by subscribed resource type
#                   Example: Appointment
#
#   event = Filter by webhook event name
#           Example: appointment_updated
#
# IMPORTANT:
#   If subdomain is provided:
#       Results are scoped to that institution and exclude
#       subscriptions without an institution.
#
#   If subdomain is omitted:
#       NexHealth returns every subscription associated with
#       the webhook endpoint, including institutionless
#       subscriptions such as Onboarding.
#
#   Results are NOT paginated.
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# GET https://nexhealth.info/webhook_endpoints/123456/webhook_subscriptions
#     ?subdomain=nexhealthsmiles
#
# Filtered Example:
# GET https://nexhealth.info/webhook_endpoints/123456/webhook_subscriptions
#     ?subdomain=nexhealthsmiles
#     &resource_type=Appointment
#     &event=appointment_updated
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
webhook_endpoint_id = os.getenv("WEBHOOKENDPOINTID")
subdomain = os.getenv("SUBDOMAIN")
resource_type = os.getenv("WEBHOOKRESOURCETYPE")
webhook_event = os.getenv("WEBHOOKEVENT")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if webhook_endpoint_id is None:
    raise ValueError("WEBHOOKENDPOINTID is missing from .env")

webhook_endpoint_id = int(webhook_endpoint_id)

url = (
    f"https://nexhealth.info/webhook_endpoints/"
    f"{webhook_endpoint_id}/webhook_subscriptions"
)

params: dict[str, str | int | bool] = {
}

if subdomain is not None:
    params["subdomain"] = subdomain

if resource_type is not None:
    params["resource_type"] = resource_type

if webhook_event is not None:
    params["event"] = webhook_event

headers = {
    "accept": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.get(
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

try:
    console.print_json(data=response.json())
except ValueError:
    console.print(response.text, style="yellow")