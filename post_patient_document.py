# https://docs.nexhealth.com/reference/postpatientsiddocuments
#  ---------------------------------------------------------
# PLAIN TEXT
#
# POST https://nexhealth.info/patients/{id}/documents
#
# ---------------------------------------------------------
# WITH
#
# Path Params:
#   id = NexHealth Patient ID
#
# Query Params:
#   subdomain = NexHealth institution subdomain
#   location_id = NexHealth Location ID
#
# Body Params:
#   file = File being uploaded
#   document_type_id = NexHealth Document Type ID (optional)
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = API key
#
# Content Type:
#   multipart/form-data
#
# NOTE:
#   Do NOT manually set content-type.
#   requests will automatically generate the multipart/form-data
#   header and boundary when files={} is used.
#
# Example:
# POST https://nexhealth.info/patients/123456/documents
#      ?subdomain=nexhealthsmiles
#      &location_id=357525
# ---------------------------------------------------------


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
document_type_id = os.getenv("DOCUMENTTYPEID")
file_path = os.getenv("FILEPATH")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

if subdomain is None:
    raise ValueError("SUBDOMAIN is missing from .env")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

if patient_id is None:
    raise ValueError("PATIENTID is missing from .env")

if file_path is None:
    raise ValueError("FILEPATH is missing from .env")

if not os.path.isfile(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

location_id = int(location_id)
patient_id = int(patient_id)

url = f"https://nexhealth.info/patients/{patient_id}/documents"

params: dict[str, str | int | bool] = {
    "subdomain": subdomain,
    "location_id": location_id
}

headers = {
    "accept": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

data: dict[str, str | int] = {}

if document_type_id is not None:
    data["document_type_id"] = int(document_type_id)

with open(file_path, "rb") as document_file:

    files = {
        "file": (
            os.path.basename(file_path),
            document_file
        )
    }

    response = requests.post(
        url,
        headers=headers,
        params=params,
        data=data,
        files=files
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