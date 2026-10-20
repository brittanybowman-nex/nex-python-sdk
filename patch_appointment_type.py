import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
location_id = os.getenv("LOCATIONID")
appointment_type_id = os.getenv("APPOINTMENTTYPEID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

if appointment_type_id is None:
    raise ValueError("APPOINTMENTTYPEID is missing from .env")

location_id = int(location_id)
appointment_type_id = int(appointment_type_id)

url = f"https://nexhealth.info/appointment_types/{appointment_type_id}"

params = {
    "subdomain": subdomain
}

payload = {
    "appointment_type": {
        "name": "Updated Appointment Type Name",
        "minutes": 60,
        "bookable_online": False,
        "emr_appt_descriptor_ids": []
    },
    "location_id": location_id
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