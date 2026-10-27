# https://docs.nexhealth.com/reference/postpayments

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
payment_type_id = os.getenv("PAYMENTTYPEID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

if patient_id is None:
    raise ValueError("PATIENTID is missing from .env")

if payment_type_id is None:
    raise ValueError("PAYMENTTYPEID is missing from .env")

location_id = int(location_id)
patient_id = int(patient_id)
payment_type_id = int(payment_type_id)

url = "https://nexhealth.info/payments"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain,
    "location_id": location_id
}

payload = {
    "payment": {
        "patient_id": patient_id,
        "amount": -125.00,
        "currency": "USD",
        "payment_type_id": payment_type_id,
        "transaction_id": "API:123456",
        "paid_at": "2026-10-06T15:00:00+00:00",
        "notes": "Payment created via NexHealth API"
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

if response.content:
    try:
        console.print_json(data=response.json())
    except ValueError:
        console.print(response.text, style="yellow")
else:
    console.print(
        "Payment accepted for processing.",
        style="bold green"
    )