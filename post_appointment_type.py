# https://docs.nexhealth.com/reference/postappointmenttypes

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

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

location_id = int(location_id)

url = "https://nexhealth.info/appointment_types"

params = {
    "subdomain": subdomain
}

payload = {
    "appointment_type": {
        "name": "EMR Descriptor Regular Appointment",
        "minutes": 60,
        "parent_type": "Location",
        "parent_id": location_id,
        "bookable_online": True,
        "emr_appt_descriptor_ids": [14344343]
    },
    "location_id": location_id
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
    console.print(f"Status Code: {response.status_code}", style="bold green")
else:
    console.print(f"Status Code: {response.status_code}", style="bold red")

console.print(f"Request URL: {response.url}", style="bold magenta")

try:
    console.print_json(data=response.json())
except ValueError:
    console.print(response.text, style="yellow")