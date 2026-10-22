# ---------------------------------------------------------
# PLAIN TEXT
#
# GET https://nexhealth.info/appointment_types
#
# ---------------------------------------------------------
# WITH
#
# Query Params:
#   subdomain = NexHealth institution subdomain
#               Required
#
#   location_id = NexHealth Location ID
#                 Required when appointment types are
#                 location-specific.
#
#                 Also required when requesting sub-resources
#                 through include[].
#
#   include[] = Optional related resources to include
#
#               Allowed:
#                   descriptors
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# GET https://nexhealth.info/appointment_types
#     ?subdomain=nexhealthsmiles
#     &location_id=123456
#
# Example including appointment descriptors:
# GET https://nexhealth.info/appointment_types
#     ?subdomain=nexhealthsmiles
#     &location_id=123456
#     &include[]=descriptors
#
# Successful Response:
#   200 OK
#
# Possible Responses:
#   200 = Successful
#   400 = Bad Request
#   401 = Unauthorized
#   403 = Forbidden
#   404 = Not Found
#   500 = Internal Server Error
# ---------------------------------------------------------


import requests
import os
from rich.console import Console
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
location_id = os.getenv("LOCATIONID")

if not api_key:
    raise ValueError("APIKEY is missing or empty in .env")

if not subdomain:
    raise ValueError("SUBDOMAIN is missing or empty in .env")

url = "https://nexhealth.info/appointment_types"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

# LOCATIONID is optional unless the institution uses
# location-specific appointment types.
if location_id:
    params["location_id"] = int(location_id)

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