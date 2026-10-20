# https://docs.nexhealth.com/reference/patchpatientsidalertsalertid

# PATCH /patients/{id}/alerts/{alert_id}
# A successful update returns 200. Once disabled, you can’t PATCH it back to active with disabled: false

# - id → required patient ID path param
# - alert_id → required alert ID path param
# - subdomain → required query param
# - patient_alert → required JSON body
# - setting "disabled": true disables the alert
# - re-enabling a disabled alert is not supported and returns 400

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
patient_id = os.getenv("PATIENTID")
alert_id = os.getenv("ALERTID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if patient_id is None:
    raise ValueError("PATIENTID is missing from .env")

if alert_id is None:
    raise ValueError("ALERTID is missing from .env")

patient_id = int(patient_id)
alert_id = int(alert_id)

url = f"https://nexhealth.info/patients/{patient_id}/alerts/{alert_id}"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

payload = {
    "patient_alert": {
        "disabled": False
    }
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