# https://docs.nexhealth.com/reference/getinstitutions - PROBABLY DO NOT USE THIS, it hits all the API's I have acccess to, not just the NH test account

import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

url = "https://nexhealth.info/institutions"

headers = {
    "accept": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.get(
    url,
    headers=headers
)

if response.ok:
    console.print(f"Status Code: {response.status_code}", style="bold green")
else:
    console.print(f"Status Code: {response.status_code}", style="bold red")

console.print(f"Request URL: {response.url}", style="bold magenta")

try:
    console.print_json(data=response.json())
except ValueError:
    console.print(response.text, style="yellow")