# NexHealth Python API Test Suite

> **Unofficial developer project. Not an official NexHealth SDK.**

A Python-based test suite and API exploration project for the NexHealth Synchronizer API. The repository is organized to mirror the NexHealth API Reference as closely as practical so individual endpoint scripts are easy to find, test, compare, and eventually refactor into a reusable Python client library.

This project currently targets:

- **Base URL:** `https://nexhealth.info`
- **API version:** `v3.0.0`
- **Python HTTP client:** `requests`
- **Environment management:** `python-dotenv`
- **Terminal output:** `rich`

Official NexHealth API reference: https://docs.nexhealth.com/reference/introduction

---

# Repository goals

This repository is intended to provide:

- Small, readable Python examples for individual NexHealth endpoints.
- Consistent use of `.env` variables instead of hard-coded credentials.
- Consistent separation of path params, query params, headers, and JSON bodies.
- Rich-formatted terminal output for easier API troubleshooting.
- A test harness for learning how NexHealth resources relate to each other.
- A foundation for a future reusable NexHealth Python client/SDK.
- Notes about endpoint quirks, EHR-specific behavior, async writes, pagination, and common errors.

This repository is **not** intended to replace NexHealth's official documentation. NexHealth's API and behavior can change; always verify production behavior against the current API reference.

---

# Security and PHI

This project interacts with healthcare data. Treat credentials, patient information, logs, screenshots, and API responses accordingly.

**Never commit:**

- `.env`
- API keys
- bearer tokens
- webhook secret keys
- real patient names
- DOBs
- phone numbers
- email addresses
- insurance/member IDs
- clinical notes
- treatment data
- production API response dumps containing PHI

Use sandbox data whenever possible.

Recommended `.gitignore`:

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.DS_Store
.vscode/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

Before pushing changes, verify that `.env` is ignored:

```bash
git check-ignore .env
```

---

# Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install requests python-dotenv rich
```

Or, if this repository contains `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

---

# Environment variables

Create a local `.env` file. Do not commit it.

Example:

```env
APIKEY=
SUBDOMAIN=
LOCATIONID=
INSTITUTIONID=
PATIENTID=
PROVIDERID=
APPOINTMENTID=
APPOINTMENTTYPEID=
OPERATORYID=
PROCEDUREID=
WORKINGHOURID=

INSURANCEPLANID=
INSURANCECOVERAGEID=
ADJUSTMENTID=
ADJUSTMENTTYPEID=
FEESCHEDULEID=
PAYMENTPLANID=
PAYMENTTYPEID=
PAYMENTID=
GUARANTORID=
GUARANTORBALANCEID=
INSURANCEBALANCEID=
CHARGEID=
CLAIMID=

DOCUMENTTYPEID=
FILEPATH=

WEBHOOKURL=
WEBHOOKENDPOINTID=
WEBHOOKSUBSCRIPTIONID=
WEBHOOKRESOURCETYPE=
WEBHOOKEVENT=
```

`os.getenv()` returns strings. Convert numeric identifiers before passing them where an integer is expected:

```python
location_id = os.getenv("LOCATIONID")

if location_id is None:
    raise ValueError("LOCATIONID is missing from .env")

location_id = int(location_id)
```

This also keeps Pylance from complaining about `str | None`.

---

# Code conventions used in this repository

Endpoint scripts generally follow this structure:

```python
import requests
import os
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

api_key = os.getenv("APIKEY")

if api_key is None:
    raise ValueError("APIKEY is missing from .env")
```

Query parameters are passed with `params={}`:

```python
params: dict[str, str | int | bool] = {
    "subdomain": subdomain,
    "location_id": location_id
}
```

JSON request bodies are passed separately:

```python
response = requests.post(
    url,
    headers=headers,
    params=params,
    json=payload
)
```

The API decides whether a value belongs in the URL, query string, path, or request body. A documented query parameter cannot generally be moved into the JSON payload.

### Multiple array query parameters

For one value:

```python
params = {
    "location_ids[]": location_id
}
```

For repeated values, use tuples:

```python
params = [
    ("subdomain", subdomain),
    ("include[]", "patient"),
    ("include[]", "provider"),
    ("include[]", "charges")
]
```

### Rich output

Success statuses print green, failures red, and URLs cyan:

```python
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
```

### DELETE endpoints

Many successful DELETE requests return `204 No Content`. Do not assume a JSON body exists:

```python
if response.status_code == 204:
    console.print("Deleted successfully.", style="bold green")
else:
    try:
        console.print_json(data=response.json())
    except ValueError:
        console.print(response.text, style="yellow")
```

### File uploads

Patient document uploads use `multipart/form-data`.

Use:

```python
requests.post(..., data=data, files=files)
```

Do **not** manually set `content-type` for multipart uploads. `requests` generates the multipart boundary.

---

# BASICS

## Introduction

NexHealth provides a single API layer for interacting with multiple health record systems.

All requests use:

```text
https://nexhealth.info
```

This repository targets the stable `v3.0.0` API.

Official reference:

https://docs.nexhealth.com/reference/introduction

---

## Authentication

### Implemented call

```text
basics/
└── authentication/
    └── post_authenticates.py
```

The documented authentication flow is:

```text
API key
   ↓
POST /authenticates
   ↓
JWT bearer token
   ↓
All other API requests
```

For `/authenticates`, send the raw API key:

```http
Authorization: YOUR_API_KEY
```

For normal API requests, the documented format is:

```http
Authorization: Bearer YOUR_TOKEN
```

NexHealth currently documents bearer-token lifetime as:

- Sandbox: **24 hours**
- Production: **1 hour**

A `401 Unauthorized` generally indicates missing, expired, or invalid authentication.

> **Repository note:** Some sandbox/test scripts may currently place the API credential directly in `Authorization`. Before treating this project as a production SDK, centralize authentication and have the client obtain and refresh bearer tokens automatically.

Suggested future client flow:

```python
client = NexHealth(
    api_key=os.getenv("APIKEY"),
    subdomain=os.getenv("SUBDOMAIN")
)
```

The client should internally obtain, cache, and refresh the JWT.

Official reference:

https://docs.nexhealth.com/reference/authentication-1

---

## Versioning

Every request should send:

```http
Nex-Api-Version: v3.0.0
```

`v3.0.0` and `v20240412` refer to the same API version.

Do not assume beta endpoints use the same version. Some newer NexHealth resources are documented separately under `v3.1.0`.

Official reference:

https://docs.nexhealth.com/reference/versioning

---

## Pagination

Most modern v3 collection endpoints use cursor-based pagination.

Common parameters:

```text
start_cursor
end_cursor
per_page
```

Common response structure:

```json
{
    "page_info": {
        "has_previous_page": false,
        "has_next_page": true,
        "start_cursor": "AAAAA",
        "end_cursor": "BBBBB"
    }
}
```

To move forward, send the previous response's `end_cursor`.

To move backward, send its `start_cursor`.

For many endpoints:

```text
per_page default: 5
per_page maximum: 1000
```

Exceptions exist. For example, Nex Staff currently uses page-number pagination and caps `per_page` at 300.

Official reference:

https://docs.nexhealth.com/reference/pagination

---

## Resource relationships

Related resources can commonly be accessed in two ways:

1. Filtering by an ID such as `patient_id`, `provider_id`, or `appointment_id`.
2. Sideloading related resources with `include[]`.

Example:

```python
params = [
    ("subdomain", subdomain),
    ("include[]", "patient"),
    ("include[]", "procedures")
]
```

Do not assume every `include[]` value works on every endpoint. Follow the endpoint-specific allowed values.

Official reference:

https://docs.nexhealth.com/reference/resource-relationships

---

## Response body

Most NexHealth JSON responses use a common envelope:

```json
{
    "code": true,
    "description": null,
    "error": [],
    "data": {},
    "count": 1
}
```

Important fields:

- `code` — application-level success/failure.
- `data` — returned resource or collection.
- `description` — additional request/result context.
- `error` — errors or warnings.
- `count` — total matching records on collection responses.
- `page_info` — cursor information where pagination applies.

**Important quirk:** NexHealth documents that `code: true` may still be accompanied by content in `error`, such as a warning about an unsupported/unknown parameter. Do not ignore `error` solely because the HTTP status is `2xx`.

Official reference:

https://docs.nexhealth.com/reference/response-body

---

## Response codes

Typical success responses:

| Code | Meaning |
|---|---|
| `200` | Request succeeded |
| `201` | Resource created |
| `202` | Request accepted for asynchronous processing |
| `204` | Request succeeded with no response body |

Typical failures:

| Code | Meaning |
|---|---|
| `400` | Invalid request, parameter, or body |
| `401` | Missing/invalid/expired authentication |
| `403` | Authenticated but not permitted |
| `404` | Resource not found or inaccessible |
| `422` | Semantically invalid request on endpoints that use it |
| `429` | Rate limit reached |
| `500` | Server/integration error |

Always inspect both the HTTP code and NexHealth's JSON `error` / `description` fields.

Official reference:

https://docs.nexhealth.com/reference/response-codes

---

## Errors

Useful troubleshooting order:

1. Print `response.status_code`.
2. Print `response.url`.
3. Pretty-print `response.json()`.
4. Read `error`.
5. Read `description`.
6. Confirm the documented location of each parameter.
7. Confirm the correct API version.
8. Confirm IDs belong to the correct institution/location.
9. Confirm the resource is supported by the connected EHR.
10. For async writes, confirm the eventual insertion result via webhook.

A request may be syntactically valid yet fail because the connected EHR rejects the write.

Official reference:

https://docs.nexhealth.com/reference/errors

---

## Rate limiting

NexHealth currently documents default API-key limits of:

- Patients and appointments endpoints: **1,000 requests/minute**
- Other endpoints: **2,000 requests/minute**

`429` means you are sending requests too quickly.

Production clients should implement retry/backoff rather than immediately repeating the same request.

If frequent polling is creating rate-limit pressure, use webhook subscriptions where possible.

Official reference:

https://docs.nexhealth.com/reference/rate-limiting

---

# PRACTICE OVERVIEW

```text
practice_overview/
├── institutions/
├── locations/
├── operatories/
├── patients/
├── providers/
└── procedures/
```

---

## Institutions

### Files

```text
institutions/
├── get_institutions.py
└── get_institutions_id.py
```

An institution is the top-level logical grouping for practice data.

The `subdomain` identifies the institution and is one of the most common NexHealth query parameters.

Example:

```python
params = {
    "subdomain": subdomain
}
```

Trying to access an institution outside the caller's permissions generally returns `403`.

Typical success:

```text
GET → 200
```

Common failures:

```text
400 / 401 / 403 / 404 / 500
```

---

## Locations

### Files

```text
locations/
├── get_locations.py
├── get_locations_id.py
└── get_locations_id_appointment_descriptors.py
```

Locations are practice sites within an institution.

`GET /locations` can return institutions with nested locations. Passing `subdomain` scopes the response.

Common identifiers:

```text
location_id
foreign_id
```

`foreign_id` generally represents the corresponding record identifier in the integrated EHR.

The location appointment-descriptor call is stored here or under Scheduling depending on repo preference. Conceptually, descriptors are scheduling configuration even though the route starts under `/locations`.

Typical success:

```text
GET → 200
```

---

## Operatories

### Files

```text
operatories/
├── get_operatories.py
└── get_operatories_id.py
```

Operatories represent rooms/chairs/resources used by the EHR schedule.

Common query scope:

```text
subdomain
location_id
```

Useful includes can include appointment types or appointment categories where supported.

Operatories matter when a practice maps booking availability by room rather than solely by provider.

Typical success:

```text
GET → 200
```

---

## Patients

### Files

```text
patients/
├── get_patients.py
├── get_patients_id.py
│
├── alerts/
│   ├── get_patients_id_alerts.py
│   ├── post_patients_id_alerts.py
│   ├── get_patients_id_alerts_alert_id.py
│   └── patch_patients_id_alerts_alert_id.py
│
└── documents/
    ├── get_patients_id_documents.py
    └── post_patients_id_documents.py
```

### Patient lookup

`GET /patients` is commonly scoped with:

```text
subdomain
location_id
```

Common filters include patient identity information, `foreign_id`, status, update timestamp, and pagination parameters.

Avoid logging real patient information into Git or public terminal captures.

### Patient alerts

Patient alerts are staff-facing alerts associated with a patient.

**Important limitation:** NexHealth currently documents that reading patient alerts returns alerts created through the API, not every pre-existing alert created directly by office staff in the EHR.

An API-created alert can be disabled. Re-enabling behavior is endpoint-specific; follow the current API documentation.

Typical successes:

```text
GET alert(s)   → 200
POST alert     → 201
PATCH alert    → 200
```

### Patient documents

Patient document upload is multipart:

```text
POST /patients/{id}/documents
```

Common inputs:

```text
subdomain
location_id
file
document_type_id (optional)
```

**Important quirks:**

- The uploaded filename is meaningful because it can become the filename shown in the EHR.
- Do not manually define the multipart `content-type`; let `requests` generate it.
- `GET /patients/{id}/documents` currently returns documents uploaded through NexHealth's document endpoint, not every document already present in the EHR.

Typical successes:

```text
GET documents  → 200
POST document  → 201
```

Official references:

https://docs.nexhealth.com/reference/patient-alerts  
https://docs.nexhealth.com/reference/patient-documents

---

## Providers

### Files

```text
providers/
├── get_providers.py
└── get_providers_id.py
```

Providers represent clinicians/resources who can own appointments and availability.

Common filters:

```text
subdomain
location_id
foreign_id
requestable
inactive
updated_since
ids[]
```

Useful `include[]` resources can include:

```text
locations
availabilities
appointment_types
```

Provider IDs are frequently used by:

- appointments
- available slots
- procedures
- working hours
- ledger/financial filters

Typical success:

```text
GET → 200
```

---

## Procedures

### Files

```text
procedures/
├── get_procedures.py
└── get_procedures_id.py
```

Procedures represent scheduled/completed clinical procedures from the integrated health record system.

Collection requests require meaningful filtering. Common filters include:

```text
patient_id
provider_id
appointment_id
updated_since
date ranges
```

Do not assume `location_id` alone is sufficient when the endpoint explicitly requires an additional filter.

Typical success:

```text
GET → 200
```

---

# SCHEDULING

```text
scheduling/
├── appointment_types/
├── appointments/
├── available_slots/
└── working_hours/
```

---

## Appointment types

### Files

```text
appointment_types/
├── get_appointment_types.py
├── post_appointment_types.py
├── patch_appointment_types_id.py
├── delete_appointment_types_id.py
└── get_appointment_types_id_appointment_descriptors.py
```

Appointment Types are a NexHealth concept used to define bookable appointment categories.

**Important:** NexHealth Appointment Types exist in NexHealth; they are not themselves read from or written to the EHR.

They can be scoped to:

```text
Institution
Location
```

Relevant fields include:

```text
name
minutes
parent_type
parent_id
bookable_online
emr_appt_descriptor_ids
```

`emr_appt_descriptor_ids` maps a NexHealth Appointment Type to appointment descriptors from the underlying EHR.

Example:

```python
"emr_appt_descriptor_ids": [37714707]
```

An empty list:

```python
"emr_appt_descriptor_ids": []
```

means no descriptors are associated.

Do not use:

```python
["null"]
```

because that is a literal string.

Typical successes:

```text
GET    → 200
POST   → 201
PATCH  → 200
DELETE → 204
```

Official overview:

https://docs.nexhealth.com/reference/appointment-types

---

## Appointments

### Files

```text
appointments/
├── get_appointments.py
├── get_appointments_id.py
├── post_appointments.py
├── patch_appointments_id.py
└── get_appointments_id_appointment_descriptors.py
```

Appointments connect patients, providers, times, operatories, appointment types, and EHR descriptors.

Collection queries commonly use:

```text
subdomain
location_id
start
end
provider_ids[]
patient_ids[]
operatory_ids[]
appointment_type_id
cancelled
updated_since
```

Use ISO-8601 timestamps and preserve the intended timezone offset.

Example:

```text
2026-11-05T16:00:00-07:00
```

### Async writes

A successful API request does not necessarily mean the downstream EHR write has completed.

For production integrations, use insertion webhooks such as:

```text
appointment_insertion
```

to determine whether the EHR write ultimately completed or failed.

### `foreign_id`

`foreign_id` represents the corresponding appointment identifier in the integrated EHR, and is useful when reconciling NexHealth and EHR records.

Typical successes:

```text
GET   → 200
POST  → creation/accepted status defined by endpoint
PATCH → 200
```

Common failures include EHR-specific validation and write errors even when the HTTP request itself is valid.

---

## Available slots

### Files

```text
available_slots/
└── get_available_slots.py
```

`GET /available_slots` calculates bookable availability.

Common required inputs include:

```text
subdomain
start_date
days
lids[]
```

and either:

```text
pids[]
```

or:

```text
appointment_type_id
```

Useful options include:

```text
working_hour_source
working_hour_label_id
slot_length
slot_interval
overlapping_operatory_slots
appointments_per_timeslot
```

**Core behavior:** available slots are calculated *inside working hours*. If a provider has no applicable working hours, the API can return no slots even when the EHR calendar looks open.

When `appointment_type_id` is supplied, NexHealth can use the appointment type's duration and provider/working-hour mappings.

Typical success:

```text
GET → 200
```

Official reference:

https://docs.nexhealth.com/reference/getavailableslots

---

## Working hours

### Files

```text
working_hours/
├── get_working_hours.py
├── get_working_hours_id.py
├── post_working_hours.py
├── patch_working_hours_id.py
├── delete_working_hours_id.py
└── get_working_hour_labels.py
```

Working hours define the boundaries inside which providers can be booked.

Two sources exist:

```text
manual
synced
```

### Manual working hours

Created/managed through NexHealth.

Editable through:

```text
POST /working_hours
PATCH /working_hours/{id}
DELETE /working_hours/{id}
```

### Synced working hours

Read from supported EHR scheduling configuration.

**Do not edit synced working hours through the NexHealth API.** Change them in the source EHR.

Relevant fields can include:

```text
provider_id
operatory_id
begin_time
end_time
days
specific_date
custom_recurrence
appointment_type_ids
active
```

For creation/update, follow the endpoint rule around mutually exclusive recurrence fields. Do not blindly send `days`, `specific_date`, and `custom_recurrence` together.

`appointment_type_ids` controls which appointment types can be booked within a working-hour record.

Typical successes:

```text
GET    → 200
POST   → creation success
PATCH  → 200
DELETE → 204
```

### Working hour labels

Working-hour-label support is EHR-dependent. The current documentation should be checked before relying on labels across integrations.

Official overview:

https://docs.nexhealth.com/reference/working-hours

---

# PRACTICE FINANCIALS

```text
practice_financials/
├── adjustments/
├── adjustment_types/
├── fee_schedules/
├── payment_plans/
├── payment_types/
├── balances/
├── charges/
├── claims/
├── insurance/
└── payments/
```

> **Financial API note:** NexHealth currently documents that financial data is read from the EHR on request and may require enablement for a production API key. Sandbox locations generally have financial reads enabled. Many financial endpoints currently document support for Dentrix, Eaglesoft, and Open Dental; confirm support on each endpoint before designing around another EHR.

---

## Adjustments

### Files

```text
adjustments/
├── get_adjustments.py
├── get_adjustments_id.py
└── post_adjustments.py
```

Adjustments change a patient's ledger balance.

Collection reads require `subdomain`, `location_id`, and at least one meaningful filter such as:

```text
patient_id
provider_id
guarantor_id
claim_id
charge_id
updated_since
```

Adjustment writes use a caller-defined `transaction_id`.

Do not reuse transaction IDs casually; treat them as reconciliation/idempotency-style identifiers according to the documented workflow.

Debit/credit direction matters. Use Adjustment Types to understand how a specific adjustment changes the balance.

Typical successes:

```text
GET  → 200
POST → commonly asynchronous / accepted
```

For async writes, use the `adjustment_insertion` webhook where appropriate.

---

## Adjustment types

### Files

```text
adjustment_types/
├── get_adjustment_types.py
└── get_adjustment_types_id.py
```

Adjustment types describe why a ledger adjustment exists.

Actions can include:

```text
credit
debit
unknown
```

Conceptually:

- `debit` increases what the patient owes.
- `credit` decreases what the patient owes.
- `unknown` indicates the EHR does not provide a clear direction.

Collection requests use:

```text
subdomain
location_id
```

and can filter `active` / `updated_since`.

Typical success:

```text
GET → 200
```

Official overview:

https://docs.nexhealth.com/reference/adjustment-types

---

## Fee schedules

### Files

```text
fee_schedules/
├── get_fee_schedules.py
├── get_fee_schedules_id.py
└── get_fee_schedule_procedures.py
```

Fee schedules map procedures to prices.

Common use cases:

- estimate procedure cost
- compare pricing between insurance/cash schedules
- support treatment-cost calculations

`GET /fee_schedule_procedures` requires `subdomain`, `location_id`, and an additional selector such as:

```text
fee_schedule_id
updated_since
```

A single fee schedule can optionally include its procedure fees where supported.

Typical success:

```text
GET → 200
```

Official overview:

https://docs.nexhealth.com/reference/fee-schedules

---

## Payment plans

### Files

```text
payment_plans/
├── get_payment_plans.py
└── get_payment_plans_id.py
```

Collection requests commonly require:

```text
subdomain
location_id
```

plus at least one filter such as:

```text
patient_id
guarantor_id
updated_since
```

**Quirk:** `GET /payment_plans/{id}` currently does not document `subdomain` as a query parameter. Follow the endpoint docs rather than forcing every request into the same pattern.

Useful includes for a single payment plan:

```text
patient
guarantor
```

Typical success:

```text
GET → 200
```

---

## Payment types

### Files

```text
payment_types/
├── get_payment_types.py
└── get_payment_types_id.py
```

Payment types represent categories such as cash, card, check, or other EHR-configured payment methods.

Collection requests use:

```text
subdomain
location_id
```

Common filters:

```text
active
updated_since
```

Payment types are important when posting a payment because the EHR needs to know what category/type to assign the transaction.

Typical success:

```text
GET → 200
```

Official overview:

https://docs.nexhealth.com/reference/payment-types

---

## Balances

```text
balances/
├── guarantor/
│   ├── get_guarantor_balances.py
│   └── get_guarantor_balances_id.py
└── insurance/
    ├── get_insurance_balances.py
    └── get_insurance_balances_id.py
```

### Guarantor balances

Collection requests require location scoping plus a selector such as:

```text
guarantor_id
updated_since
```

`show_zero_balances=true` can be useful because zero balances may otherwise be excluded.

**Quirk:** the single guarantor-balance endpoint currently does not document `subdomain` and supports `include[]=guarantor`.

### Insurance balances

Insurance balances represent expected/billed insurance amounts, including aging buckets.

Collection requests require:

```text
subdomain
location_id
```

plus at least one of:

```text
patient_id
guarantor_id
updated_since
```

`location_id` by itself does not satisfy the additional-filter requirement.

The single insurance-balance endpoint **does** require `subdomain`.

Typical success:

```text
GET → 200
```

---

## Charges

### Files

```text
charges/
├── get_charges.py
└── get_charges_id.py
```

Charges are ledger amounts associated with treatment/procedures.

Collection reads require `subdomain`, `location_id`, and a meaningful filter such as:

```text
patient_id
provider_id
procedure_id
guarantor_id
updated_since
```

Useful related resources can include claim payouts or totals, depending on the endpoint.

Typical success:

```text
GET → 200
```

---

## Claims

### Files

```text
claims/
├── get_claims.py
└── get_claims_id.py
```

Claim collection requests require `subdomain`, `location_id`, and at least one filter such as:

```text
patient_id
guarantor_id
provider_id
updated_since
date_of_service
```

Single claim responses can include:

```text
patient
provider
guarantor
charges
charge_payouts
```

**Known API quirk:** NexHealth currently documents that `GET /claims/{id}` may return **HTTP 500 instead of 404** when the claim does not exist or belongs to an inaccessible location. Do not automatically interpret every 500 from that route as a generic infrastructure outage.

Typical success:

```text
GET → 200
```

---

## Insurance

### Files

```text
insurance/
├── get_insurance_plans.py
├── get_insurance_plans_id.py
├── get_insurance_coverages.py
└── get_insurance_coverages_id.py
```

### Insurance plans

Plans describe payer/group-plan configuration in the EHR.

Useful filters include:

```text
payer_id
group_num
updated_since
include_deleted
```

Single plans may allow includes such as related coverages/subscribers/fee schedules depending on the current endpoint contract.

### Insurance coverages

Coverages connect patients/subscribers with insurance plans.

Useful filters include:

```text
patient_id
active
updated_since
```

Be careful when dynamically adding optional integer filters to a `params` dictionary. Use explicit typing:

```python
params: dict[str, str | int | bool] = {
    "subdomain": subdomain
}

if patient_id is not None:
    params["patient_id"] = int(patient_id)
```

That avoids the Pylance `int is not assignable to str` warning.

Typical success:

```text
GET → 200
```

---

## Payments

### Files

```text
payments/
├── get_payments.py
├── get_payments_id.py
└── post_payments.py
```

Payments reduce a patient's balance.

**Important sign convention:**

```text
Payment → negative amount
Refund  → positive amount
```

Example:

```python
"amount": -125.00
```

for a $125 payment.

Collection reads require `subdomain`, `location_id`, and at least one filter such as:

```text
patient_id
provider_id
guarantor_id
charge_id
claim_id
transaction_id
updated_since
```

Payment writes use a `payment_type_id` and caller-defined `transaction_id`.

Payments can be allocated using splits where supported.

Writes can be asynchronous. Use:

```text
payment_insertion
```

webhooks to determine whether the payment actually reached the EHR.

Official overview:

https://docs.nexhealth.com/reference/payments

---

# ADDITIONAL IMPLEMENTED RESOURCES

These are part of the test suite even though they were not visible in the supplied screenshot section of the reference navigation.

```text
clinical/
documents/
staff/
sync/
webhooks/
```

---

## Clinical notes

### Files

```text
clinical/
└── clinical_notes/
    └── get_clinical_notes.py
```

Clinical notes contain patient visit documentation.

Collection calls require `subdomain`, `location_id`, and at least one meaningful filter such as:

```text
patient_id
procedure_id
entered_before
entered_after
updated_since
```

Procedure associations can vary by EHR/note type.

Never commit real clinical-note response bodies to Git.

Typical success:

```text
GET → 200
```

Official overview:

https://docs.nexhealth.com/reference/clinical-notes

---

## Document types

### Files

```text
documents/
└── document_types/
    ├── get_document_types.py
    └── get_document_types_id.py
```

Document types represent EHR document categories such as forms, treatment plans, imaging, insurance documents, etc.

Collection requests use:

```text
subdomain
location_id
active
```

`active` defaults to active-only behavior.

Document types are useful when uploading a patient document so the file is placed/classified correctly in the EHR.

Typical success:

```text
GET → 200
```

Official overview:

https://docs.nexhealth.com/reference/document-types

---

## Nex Staff

### Files

```text
staff/
└── get_nex_staff.py
```

A Nex Staff record represents a user account in the NexHealth web application.

Common parameters:

```text
subdomain
page
per_page
inactive
location_ids[]
```

This endpoint currently uses page-number pagination rather than the cursor pattern used by many other collection endpoints.

Current documented max:

```text
per_page = 300
```

Typical success:

```text
GET → 200
```

---

## Sync status

### Files

```text
sync/
└── get_sync_status.py
```

Sync status indicates whether NexHealth's integration with the EHR is healthy.

Each sync exposes:

```text
read_status
read_status_at
write_status
write_status_at
```

Statuses are:

```text
green
red
```

Interpret them separately:

- Read health = NexHealth's ability to read data from the EHR.
- Write health = NexHealth's ability to insert/update data in the EHR.

Useful filters:

```text
subdomain
read_status
write_status
location_ids[]
```

`*_status_at` timestamps are useful when assessing how recently the corresponding sync service checked in successfully.

Typical success:

```text
GET → 200
```

Official reference:

https://docs.nexhealth.com/reference/getsyncstatus

---

# WEBHOOKS

```text
webhooks/
├── endpoints/
│   ├── get_webhook_endpoints.py
│   ├── post_webhook_endpoints.py
│   ├── patch_webhook_endpoints_id.py
│   └── delete_webhook_endpoints_id.py
│
└── subscriptions/
    ├── get_webhook_endpoint_subscriptions.py
    ├── post_webhook_endpoint_subscription.py
    ├── patch_webhook_endpoint_subscription.py
    └── delete_webhook_endpoint_subscription.py
```

Webhooks let NexHealth notify your application when something happens instead of requiring your application to continuously poll.

Conceptually:

```text
Something changes
      ↓
NexHealth
      ↓
HTTP POST
      ↓
Your webhook URL
```

This is especially useful for:

- appointment changes
- patient changes
- payment changes
- financial-data changes
- document insertion results
- asynchronous EHR write results
- sync recovery signals

---

## Webhook endpoints

A webhook endpoint defines **where** NexHealth sends webhook events.

Example:

```text
https://yourapp.example.com/nexhealth/webhooks
```

Relevant calls:

```text
GET    /webhook_endpoints
POST   /webhook_endpoints
PATCH  /webhook_endpoints/{id}
DELETE /webhook_endpoints/{id}
```

Production webhook URLs should use HTTPS.

The returned webhook endpoint configuration can contain a secret used to validate signed webhook deliveries. Treat webhook secrets like credentials.

Typical successes:

```text
GET    → 200
POST   → 201
PATCH  → 200
DELETE → 204
```

---

## Webhook subscriptions

A subscription defines **what** NexHealth sends to an endpoint.

Conceptually:

```text
Webhook Endpoint
      +
Resource Type
      +
Event
```

Example:

```text
Endpoint:      123456
Resource Type: Appointment
Event:         appointment_updated
```

Relevant calls:

```text
GET    /webhook_endpoints/{id}/webhook_subscriptions
POST   /webhook_endpoints/{id}/webhook_subscriptions
PATCH  /webhook_endpoints/{id}/webhook_subscriptions/{subscription_id}
DELETE /webhook_endpoints/{id}/webhook_subscriptions/{subscription_id}
```

`resource_type` and `event` are case-sensitive enums. Use the exact documented values.

Example:

```json
{
    "resource_type": "Appointment",
    "event": "appointment_updated",
    "active": true
}
```

Do not use:

```json
{
    "resource_type": "appointment"
}
```

if the enum expects `Appointment`.

### Useful insertion events

Insertion events are particularly valuable because NexHealth writes to EHRs asynchronously.

Examples include:

```text
appointment_insertion
adjustment_insertion
payment_insertion
document_insertion
```

These can report whether an EHR insertion ultimately:

```text
complete
failed
```

### Sync status webhook quirk

The current webhook documentation says:

```text
sync_status_read_change
sync_status_write_change
```

fire when status recovers from:

```text
red → green
```

They currently do **not** fire for:

```text
green → red
```

For outage/degradation monitoring, inspect:

```text
read_status_at
write_status_at
```

from the sync status endpoint as well.

### Version pinning

Webhook subscriptions are pinned to the API version used when the subscription is created.

If created with:

```http
Nex-Api-Version: v3.0.0
```

the subscription payload contract follows that API version.

Typical successes:

```text
GET    → 200
POST   → 201
PATCH  → 200
DELETE → 204
```

Official reference:

https://docs.nexhealth.com/reference/webhook-subscriptions

---

# Suggested repository structure

```text
nexhealth-python-api-tests/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── basics/
│   └── authentication/
│       └── post_authenticates.py
│
├── practice_overview/
│   ├── institutions/
│   │   ├── get_institutions.py
│   │   └── get_institutions_id.py
│   │
│   ├── locations/
│   │   ├── get_locations.py
│   │   ├── get_locations_id.py
│   │   └── get_locations_id_appointment_descriptors.py
│   │
│   ├── operatories/
│   │   ├── get_operatories.py
│   │   └── get_operatories_id.py
│   │
│   ├── patients/
│   │   ├── get_patients.py
│   │   ├── get_patients_id.py
│   │   ├── alerts/
│   │   │   ├── get_patients_id_alerts.py
│   │   │   ├── post_patients_id_alerts.py
│   │   │   ├── get_patients_id_alerts_alert_id.py
│   │   │   └── patch_patients_id_alerts_alert_id.py
│   │   └── documents/
│   │       ├── get_patients_id_documents.py
│   │       └── post_patients_id_documents.py
│   │
│   ├── providers/
│   │   ├── get_providers.py
│   │   └── get_providers_id.py
│   │
│   └── procedures/
│       ├── get_procedures.py
│       └── get_procedures_id.py
│
├── scheduling/
│   ├── appointment_types/
│   │   ├── get_appointment_types.py
│   │   ├── post_appointment_types.py
│   │   ├── patch_appointment_types_id.py
│   │   ├── delete_appointment_types_id.py
│   │   └── get_appointment_types_id_appointment_descriptors.py
│   │
│   ├── appointments/
│   │   ├── get_appointments.py
│   │   ├── get_appointments_id.py
│   │   ├── post_appointments.py
│   │   ├── patch_appointments_id.py
│   │   └── get_appointments_id_appointment_descriptors.py
│   │
│   ├── available_slots/
│   │   └── get_available_slots.py
│   │
│   └── working_hours/
│       ├── get_working_hours.py
│       ├── get_working_hours_id.py
│       ├── post_working_hours.py
│       ├── patch_working_hours_id.py
│       ├── delete_working_hours_id.py
│       └── get_working_hour_labels.py
│
├── practice_financials/
│   ├── adjustments/
│   │   ├── get_adjustments.py
│   │   ├── get_adjustments_id.py
│   │   └── post_adjustments.py
│   │
│   ├── adjustment_types/
│   │   ├── get_adjustment_types.py
│   │   └── get_adjustment_types_id.py
│   │
│   ├── fee_schedules/
│   │   ├── get_fee_schedules.py
│   │   ├── get_fee_schedules_id.py
│   │   └── get_fee_schedule_procedures.py
│   │
│   ├── payment_plans/
│   │   ├── get_payment_plans.py
│   │   └── get_payment_plans_id.py
│   │
│   ├── payment_types/
│   │   ├── get_payment_types.py
│   │   └── get_payment_types_id.py
│   │
│   ├── balances/
│   │   ├── guarantor/
│   │   │   ├── get_guarantor_balances.py
│   │   │   └── get_guarantor_balances_id.py
│   │   └── insurance/
│   │       ├── get_insurance_balances.py
│   │       └── get_insurance_balances_id.py
│   │
│   ├── charges/
│   │   ├── get_charges.py
│   │   └── get_charges_id.py
│   │
│   ├── claims/
│   │   ├── get_claims.py
│   │   └── get_claims_id.py
│   │
│   ├── insurance/
│   │   ├── get_insurance_plans.py
│   │   ├── get_insurance_plans_id.py
│   │   ├── get_insurance_coverages.py
│   │   └── get_insurance_coverages_id.py
│   │
│   └── payments/
│       ├── get_payments.py
│       ├── get_payments_id.py
│       └── post_payments.py
│
├── clinical/
│   └── clinical_notes/
│       └── get_clinical_notes.py
│
├── documents/
│   └── document_types/
│       ├── get_document_types.py
│       └── get_document_types_id.py
│
├── staff/
│   └── get_nex_staff.py
│
├── sync/
│   └── get_sync_status.py
│
└── webhooks/
    ├── endpoints/
    │   ├── get_webhook_endpoints.py
    │   ├── post_webhook_endpoints.py
    │   ├── patch_webhook_endpoints_id.py
    │   └── delete_webhook_endpoints_id.py
    │
    └── subscriptions/
        ├── get_webhook_endpoint_subscriptions.py
        ├── post_webhook_endpoint_subscription.py
        ├── patch_webhook_endpoint_subscription.py
        └── delete_webhook_endpoint_subscription.py
```

---

# Recommended future refactor: turn scripts into a client

The current repo is intentionally endpoint-oriented and easy to test manually.

A future SDK should remove repeated plumbing.

Instead of:

```python
requests.get(
    url,
    headers=headers,
    params=params
)
```

the public API could become:

```python
client.institutions.list()

client.patients.get(patient_id)

client.appointments.list(
    location_id=location_id,
    start=start,
    end=end
)

client.webhooks.subscribe(
    endpoint_id=webhook_endpoint_id,
    resource_type="Appointment",
    event="appointment_updated"
)
```

Suggested package layout:

```text
src/
└── nexhealth_client/
    ├── client.py
    ├── auth.py
    ├── exceptions.py
    ├── models/
    └── resources/
        ├── institutions.py
        ├── locations.py
        ├── patients.py
        ├── providers.py
        ├── appointments.py
        ├── working_hours.py
        ├── financials.py
        └── webhooks.py
```

The base client should eventually own:

- bearer-token retrieval
- token refresh
- base URL
- API version
- default headers
- retries/backoff
- 429 handling
- pagination
- consistent exceptions
- response-envelope parsing
- optional logging
- webhook signature verification helpers

---

# Testing recommendations

Eventually split tests into:

```text
tests/
├── unit/
└── integration/
```

### Unit tests

Do not call NexHealth. Mock HTTP responses and validate:

- URL generation
- query parameters
- headers
- request bodies
- token refresh
- exception handling
- pagination logic

### Integration tests

Call only the NexHealth sandbox and test:

- authentication
- read endpoints
- safe create/update/delete workflows
- asynchronous insert behavior
- webhook delivery

Avoid integration tests that can accidentally mutate production data.

---

# Useful tooling

Possible future additions:

- **pytest** — automated testing
- **Ruff** — linting/formatting
- **Pyright/Pylance** — type checking
- **httpx** — potential future HTTP layer with async support
- **Pydantic** — typed request/response models
- **Redocly CLI** — OpenAPI validation
- **Schemathesis** — schema-driven API testing
- **GitHub Actions** — CI
- **OpenAPI Generator** — generated models/client scaffolding
- **Scalar/Redoc** — generated interactive API documentation

---

# Troubleshooting checklist

Before assuming NexHealth is broken:

```text
[ ] Is the correct .env loaded?
[ ] Is the credential present?
[ ] Is the bearer token current?
[ ] Is Nex-Api-Version set correctly?
[ ] Is subdomain correct?
[ ] Is location_id correct?
[ ] Does the ID belong to this institution/location?
[ ] Is the parameter in the correct place?
    - path
    - params
    - JSON body
    - multipart form
[ ] Are numeric env vars converted to int where needed?
[ ] Does this collection endpoint require an additional filter?
[ ] Does the EHR support this resource/write?
[ ] Is the working hour manual vs synced?
[ ] Is the API response warning in error even though code=true?
[ ] Is this an async write that requires an insertion webhook?
[ ] Is the API returning 429?
[ ] Is sync status read/write green?
```

When debugging, always print:

```python
console.print(f"Status Code: {response.status_code}")
console.print(f"Request URL: {response.url}")
console.print_json(data=response.json())
```

---

# Disclaimer

This repository is an independent developer/test project.

It is:

- not an official NexHealth SDK
- not endorsed by NexHealth
- not a substitute for current NexHealth documentation
- not intended to contain production credentials or PHI

NexHealth API behavior, supported EHRs, request parameters, API versions, and endpoint availability can change. Validate critical production behavior against the current official documentation.

Official documentation:

https://docs.nexhealth.com/reference/introduction

