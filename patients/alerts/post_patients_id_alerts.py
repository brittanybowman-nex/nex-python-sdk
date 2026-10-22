# https://docs.nexhealth.com/reference/postpatientsidalerts

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
patient_id = os.getenv("PATIENTID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if patient_id is None:
    raise ValueError("PATIENTID is missing from .env")

patient_id = int(patient_id)

url = f"https://nexhealth.info/patients/{patient_id}/alerts"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

payload = {
    "patient_alert": {
        "note": "Patient alert created via NexHealth API"
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