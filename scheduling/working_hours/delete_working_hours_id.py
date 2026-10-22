# ---------------------------------------------------------
# PLAIN TEXT
#
# DELETE https://nexhealth.info/working_hours/{id}
#
# ---------------------------------------------------------
# WITH
#
# Path Params:
#   id = NexHealth Working Hour ID
#        Required
#
# Query Params:
#   subdomain = NexHealth institution subdomain
#               Required
#
# Body:
#   None
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key or bearer token
#
# Example:
# DELETE https://nexhealth.info/working_hours/123456
#        ?subdomain=nexhealthsmiles
#
# Successful Response:
#   204 No Content
#
# Possible Responses:
#   204 = Successful
#   400 = Bad Request
#   401 = Unauthorized
#   404 = Not Found
#   500 = Internal Server Error
#
# IMPORTANT:
#   Manual working hours can be managed through NexHealth.
#   Synced working hours should be updated in the source EHR.
# ---------------------------------------------------------
# https://docs.nexhealth.com/reference/deleteworkinghoursid

import requests
import os
from rich.console import Console
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")
subdomain = os.getenv("SUBDOMAIN")
working_hour_id = os.getenv("WORKINGHOURID")

if not api_key:
    raise ValueError("APIKEY is missing or empty in .env")

if not subdomain:
    raise ValueError("SUBDOMAIN is missing or empty in .env")

if not working_hour_id:
    raise ValueError("WORKINGHOURID is missing or empty in .env")

working_hour_id = int(working_hour_id)

url = f"https://nexhealth.info/working_hours/{working_hour_id}"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

headers = {
    "accept": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.delete(
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

if response.status_code == 204:
    console.print(
        "Working hour deleted successfully.",
        style="bold green"
    )
else:
    try:
        console.print_json(data=response.json())
    except ValueError:
        console.print(response.text, style="yellow")