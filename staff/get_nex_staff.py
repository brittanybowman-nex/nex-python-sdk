# ---------------------------------------------------------
# PLAIN TEXT
#
# GET https://nexhealth.info/nex_staff
#
# ---------------------------------------------------------
# WITH
#
# Query Params:
#   subdomain = NexHealth institution subdomain
#
# Optional Query Params:
#   page = Page number, starting at 1
#   per_page = Number of results per page
#              Default: 5
#              Max: 300
#   inactive = Filter by inactive status
#   location_ids[] = Filter staff by accessible location IDs
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# GET https://nexhealth.info/nex_staff?subdomain=nexhealthsmiles
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

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

url = "https://nexhealth.info/nex_staff"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

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