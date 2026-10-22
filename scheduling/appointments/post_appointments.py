# https://docs.nexhealth.com/reference/postappointments

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
location_id = os.getenv("LOCATIONID")
patient_id = os.getenv("PATIENTID")
provider_id = os.getenv("PROVIDERID")
appointment_type_id = os.getenv("APPOINTMENTTYPEID")
operatory_id = os.getenv("OPERATORYID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

if patient_id is None:
    raise ValueError("PATIENTID is missing from .env")

if provider_id is None:
    raise ValueError("PROVIDERID is missing from .env")

if operatory_id is None:
    raise ValueError("OPERATORYID is missing from .env")

if appointment_type_id is None:
    raise ValueError("APPOINTMENTTYPEID is missing from .env")

location_id = int(location_id)
patient_id = int(patient_id)
provider_id = int(provider_id)
appointment_type_id = int(appointment_type_id)
operatory_id = int(operatory_id)

url = "https://nexhealth.info/appointments"

params = {
    "subdomain": subdomain,
    "location_id": location_id,
    "notify_patient": False
}

payload = {
    "appt": {
        "patient_id": patient_id,
        "provider_id": provider_id,
        "start_time": "2026-11-05T16:00:00-07:00",
        "end_time": "2026-11-05T17:00:00-07:00",
        "appointment_type_id": appointment_type_id,
        "operatory_id": operatory_id,
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