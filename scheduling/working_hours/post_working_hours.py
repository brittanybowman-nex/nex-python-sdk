# https://docs.nexhealth.com/reference/postworkinghours

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
location_id = os.getenv("LOCATIONID")
provider_id = os.getenv("PROVIDERID")
operatory_id = os.getenv("OPERATORYID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

if provider_id is None:
    raise ValueError("PROVIDERID is missing from .env")

if operatory_id is None:
    raise ValueError("OPERATORYID is missing from .env")

location_id = int(location_id)
provider_id = int(provider_id)
operatory_id = int(operatory_id)

url = "https://nexhealth.info/working_hours"

params = {
    "subdomain": subdomain,
    "location_id": location_id
}

payload = {
    "working_hour": {
        "active": True,
        "provider_id": provider_id,
        "operatory_id": operatory_id,
        "begin_time": "09:00",
        "end_time": "17:00",
        "days": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday"
        ]
    }
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