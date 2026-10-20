# https://docs.nexhealth.com/reference/getpaymenttypesid

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
payment_type_id = os.getenv("PAYMENTTYPEID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if payment_type_id is None:
    raise ValueError("PAYMENTTYPEID is missing from .env")

payment_type_id = int(payment_type_id)

url = f"https://nexhealth.info/payment_types/{payment_type_id}"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
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