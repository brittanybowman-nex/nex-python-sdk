# ---------------------------------------------------------
# PLAIN TEXT
#
# GET https://nexhealth.info/sync_status
#
# ---------------------------------------------------------
# WITH
#
# Optional Query Params:
#   subdomain = NexHealth institution subdomain
#   read_status = Filter by read status
#                 Allowed: green, red
#   write_status = Filter by write status
#                  Allowed: green, red
#   location_ids[] = Return sync status for specified
#                    NexHealth Location IDs
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# GET https://nexhealth.info/sync_status
#     ?subdomain=nexhealthsmiles
#     &location_ids[]=357525
# ---------------------------------------------------------


import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
location_id = os.getenv("LOCATIONID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

url = "https://nexhealth.info/sync_status"

# Useful bit from the current docs: read_status_at is the last time NexHealth read from the EHR, 
# while write_status_at is the last write-service check-in. By default, read goes red after 150 
# minutes and write after 25 minutes, though those thresholds can be customized per sync.

params: dict[str, str | int | bool] = {
    "read_status": "red",
    "write_status": "green"
}

if subdomain is not None:
    params["subdomain"] = subdomain

if location_id is not None:
    params["location_ids[]"] = int(location_id)

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