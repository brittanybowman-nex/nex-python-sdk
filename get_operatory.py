import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
operatory_id = os.getenv("OPERATORYID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if operatory_id is None:
    raise ValueError("OPERATORYID is missing from .env")

operatory_id = int(operatory_id)

url = f"https://nexhealth.info/operatories/{operatory_id}"

params = {
    "subdomain": subdomain,
    # "include[]": "appointment_types" OR "appt_categories"
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