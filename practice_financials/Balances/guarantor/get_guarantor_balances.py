# https://docs.nexhealth.com/reference/getguarantorbalances

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
location_id = os.getenv("LOCATIONID")
updated_since = os.getenv("UPDATEDSINCE")
# guarantor_id = os.getenv("GUARANTORID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

if updated_since is None:
    raise ValueError("UPDATEDSINCE is missing from .env")

# if guarantor_id is None:
    raise ValueError("GUARANTORID is missing from .env")

location_id = int(location_id)
updated_since = str(updated_since)
# guarantor_id = int(guarantor_id)

url = "https://nexhealth.info/guarantor_balances"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain,
    "location_id": location_id,
    "updated_since": updated_since,
    "per_page": 1000,  
    # "guarantor_id": guarantor_id
}

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