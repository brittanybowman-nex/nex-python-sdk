# ---------------------------------------------------------
# PLAIN TEXT
#
# POST https://nexhealth.info/authenticates
#
# ---------------------------------------------------------
# WITH
#
# Query Params:
#   None
#
# Body:
#   None
#
# Headers:
#   accept = application/json
#   Nex-Api-Version = v3.0.0
#   Authorization = NexHealth API key
#
# IMPORTANT:
#   Do NOT add "Bearer" in front of the API key for this request.
#
#   This endpoint exchanges the API key for a JWT bearer token.
#   The returned bearer token is used for subsequent NexHealth
#   API requests and expires after 1 hour.
#
# Example:
# POST https://nexhealth.info/authenticates
#
# Authorization: YOUR_API_KEY
# Nex-Api-Version: v3.0.0
# ---------------------------------------------------------


import requests
import os
from dotenv import load_dotenv, find_dotenv
from rich.console import Console

load_dotenv(find_dotenv())

console = Console()

api_key = os.getenv("APIKEY")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")

url = "https://nexhealth.info/authenticates"

params: dict[str, str | int | bool] = {
}

headers = {
    "accept": "application/json",
    "Nex-Api-Version": "v3.0.0",
    "Authorization": api_key
}

response = requests.post(
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
    response_data = response.json()
    console.print_json(data=response_data)

    if response.ok:
        bearer_token = response_data["data"]["token"]

        console.print(
            "Bearer token retrieved successfully.",
            style="bold green"
        )

except ValueError:
    console.print(response.text, style="yellow")

# Comments: Because the API key is your long-lived root credential, while the JWT is a short-lived session credential. That separation is intentional.

# For NexHealth specifically, the flow is:
# API key
#    ↓
# POST /authenticates
#    ↓
# short-lived JWT bearer token
#    ↓
# use JWT for normal API calls

# The main benefits are security and control. If a bearer token leaks, the blast radius is smaller because it expires; NexHealth currently says tokens last 24 hours in sandbox and 1 hour in production. Your API key, by contrast, is the credential used to mint new tokens and should be guarded much more carefully. NexHealth Synchronizer

# JWTs also carry claims such as identity/scope and expiration inside the token itself. That lets NexHealth validate a request efficiently without you sending the master API key around on every request. Their example JWT includes claims like sub, scp, iat, exp, and jti. NexHealth Synchronizer

# So conceptually:
# APIKEY
# = "I am authorized to obtain access"

# JWT bearer token
# = "I have temporary access right now"

# This is similar to using your password to sign into a site, then receiving a session cookie. You don't send your password with every click afterward.