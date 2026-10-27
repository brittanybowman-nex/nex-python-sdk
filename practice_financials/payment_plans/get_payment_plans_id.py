# https://docs.nexhealth.com/reference/getpaymentplansid

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
payment_plan_id = os.getenv("PAYMENTPLANID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if payment_plan_id is None:
    raise ValueError("PAYMENTPLANID is missing from .env")

payment_plan_id = int(payment_plan_id)

url = f"https://nexhealth.info/payment_plans/{payment_plan_id}"

params: dict[str, str | int | bool] = {
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