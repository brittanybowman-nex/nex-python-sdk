import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
location_id = os.getenv("LOCATIONID")
descriptor_type = os.getenv("DESCRIPTORTYPE")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

location_id = int(location_id)

url = f"https://nexhealth.info/locations/{location_id}/appointment_descriptors"

params = {
}

if descriptor_type is not None:
    params["descriptor_type"] = descriptor_type

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