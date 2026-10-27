import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()
# This endpoint only works for Dentrix, Eaglesoft, and Open Dental


api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
insurance_plan_id = os.getenv("INSURANCEPLANID")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if insurance_plan_id is None:
    raise ValueError("INSURANCEPLANID is missing from .env")

insurance_plan_id = int(insurance_plan_id)

url = f"https://nexhealth.info/insurance_plans/{insurance_plan_id}"

params = {
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