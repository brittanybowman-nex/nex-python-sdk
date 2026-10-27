# NexHealth Webhooks: Developer Guide

Webhooks allow NexHealth to notify your application when an event occurs instead of requiring your application to repeatedly poll the API for changes.

At a high level:

```text
Polling:
Your app ──GET──> NexHealth
          "Anything new?"
          "Anything new?"
          "Anything new?"

Webhooks:
NexHealth ──POST──> Your app
          "This changed."
```

For integrations built on the NexHealth Synchronizer API, webhooks are especially useful for two jobs:

1. **Change tracking** — reacting when NexHealth detects that data changed in the connected health record system.
2. **Asynchronous write confirmation** — determining whether a write accepted by the NexHealth API was ultimately completed in the underlying health record system.

NexHealth recommends webhooks as the default approach when an application wants changes as they happen and wants to reduce unnecessary API calls. Polling with `updated_since` remains a valid alternative when an application cannot receive inbound HTTPS requests.

Official references:

- https://docs.nexhealth.com/docs/webhooks
- https://docs.nexhealth.com/docs/data-pipelines
- https://docs.nexhealth.com/reference/webhook-subscriptions
- https://docs.nexhealth.com/docs/how-a-write-reaches-the-ehr

---

## Mental Model

There are three separate concepts to keep straight:

```text
1. Webhook endpoint
   "Where should NexHealth send events?"

2. Webhook subscription
   "Which events should NexHealth send there?"

3. Your HTTPS route
   "Where does my application actually receive the POST request?"
```

A complete flow looks like this:

```text
Your application
      |
      | POST /webhook_endpoints
      v
NexHealth registers:
https://yourapp.example.com/nexhealth/webhooks
      |
      | POST /webhook_endpoints/{id}/webhook_subscriptions
      v
Subscription examples:
Appointment / appointment_updated
Patient     / patient_updated
Payment     / payment_created
Document    / document_insertion
      |
      | Event occurs
      v
NexHealth POSTs JSON
      |
      v
https://yourapp.example.com/nexhealth/webhooks
```

The important distinction is that your webhook receiver is **not calling NexHealth**. NexHealth is calling your application.

---

## Why Use Webhooks Instead of Polling?

Without webhooks, an application might repeatedly do something like:

```python
while True:
    requests.get("/appointments")
    requests.get("/patients")
    requests.get("/payments")
```

That creates unnecessary API traffic and introduces delay between an event occurring and your application learning about it.

With webhooks, NexHealth can notify your application when subscribed events occur.

Polling is still useful when:

- your application cannot expose a public HTTPS endpoint;
- you are running scheduled reconciliation jobs;
- you want a fallback mechanism;
- you are rebuilding local state after downtime.

For polling, NexHealth commonly supports `updated_since` on collection endpoints.

A production integration can use both approaches:

```text
Webhooks
   |
   +---- Real-time event handling

Polling / reconciliation
   |
   +---- Periodic verification and recovery
```

---

# Asynchronous Writes

One of the most important reasons to use NexHealth webhooks is that a successful write request does not always mean the corresponding record has already been written into the connected health record system.

For example:

```http
POST /appointments
```

may be accepted by NexHealth before the appointment has been successfully inserted into Dentrix, Eaglesoft, Open Dental, or another supported system.

The write flow is conceptually:

```text
POST /appointments
       |
       v
NexHealth accepts the request
       |
       v
NexHealth attempts the EHR write
       |
       +------ success
       |          |
       |          v
       | appointment_insertion.complete
       |
       +------ failure
       |          |
       |          v
       | appointment_insertion.failed
       |
       +------ timeout
                  |
                  v
          appointment_insertion.timed_out
```

Application code should therefore treat the initial API response as **accepted**, not necessarily **fully written to the health record system**.

For appointment writes, subscribe to:

```text
resource_type: Appointment
event: appointment_insertion
```

The resulting webhook event name reports the write state:

```text
appointment_insertion.complete
appointment_insertion.failed
appointment_insertion.timed_out
```

NexHealth documents similar insertion events for other asynchronous writes, including:

```text
adjustment_insertion
payment_insertion
document_insertion
form_response_insertion
```

A robust integration should store the NexHealth resource ID returned by the original API request and correlate later webhook events back to that record.

---

# Common Webhook Events

NexHealth supports webhook subscriptions across many resources. Examples include:

```text
appointment_created
appointment_updated
appointment_insertion

patient_created
patient_updated

payment_created
payment_updated
payment_deleted
payment_insertion

claim_created
claim_updated
claim_deleted

procedure_created
procedure_updated

form_request_completed
form_response_insertion

document_insertion

adjustment_created
adjustment_updated
adjustment_deleted
adjustment_insertion
```

The complete and current list should always be taken from:

https://docs.nexhealth.com/reference/webhook-subscriptions

Do not assume every event exists for every resource.

---

# Webhook Setup

The setup process is:

```text
1. Register a webhook endpoint
2. Save the webhook_endpoint_id and secret_key
3. Create one or more subscriptions
4. Receive HTTPS POST requests from NexHealth
5. Verify every webhook signature
6. Parse and process the event
7. Return HTTP 2xx promptly
```

## 1. Register a Webhook Endpoint

Register a public HTTPS URL with:

```http
POST /webhook_endpoints
```

Example request body:

```json
{
  "target_url": "https://yourapp.example.com/nexhealth/webhooks"
}
```

NexHealth returns a webhook endpoint record that includes an endpoint ID and a `secret_key`. Save both.

Because webhook payloads may contain Protected Health Information (PHI), NexHealth requires a valid HTTPS target URL.

The secret key is security-sensitive and should be treated like a credential. Do not commit it to Git.

---

## 2. Create a Webhook Subscription

Subscriptions are created underneath a registered endpoint:

```http
POST /webhook_endpoints/{id}/webhook_subscriptions
```

For an institution-scoped resource, `subdomain` belongs in the **query string**:

```text
?subdomain=demo-practice
```

The `resource_type` and `event` belong in the JSON body:

```json
{
  "resource_type": "Appointment",
  "event": "appointment_updated"
}
```

Important:

- `resource_type` is case-sensitive.
- `event` must exactly match a supported event.
- For v3.0.0, institution-owned subscriptions use `subdomain`.
- Some non-institution resources, such as `Onboarding`, have different subdomain requirements. Check the endpoint reference before creating those subscriptions.
- Putting `subdomain` in the JSON body instead of the query string can cause the request to fail.

---

# API Version Pinning

Webhook subscriptions are pinned to the API version used when they are created.

For example, a subscription created with:

```http
Nex-Api-Version: v3.0.0
```

receives payloads using the v3.0.0 entity contract.

This matters when NexHealth introduces newer API versions or beta resources. Do not assume an existing subscription automatically changes its payload schema because your application begins using a newer API version elsewhere.

---

# Receiving Webhooks

Your application needs a public HTTPS route capable of accepting POST requests.

For example, using FastAPI:

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/nexhealth/webhooks")
async def nexhealth_webhook(request: Request):
    payload = await request.json()

    print(payload)

    return {
        "received": True
    }
```

That is the basic shape only. A production handler should verify the NexHealth signature **before trusting or processing the payload**.

---

# Webhook Payload Structure

A webhook payload generally includes metadata about the institution, subscription, resource, event, and event data.

For example:

```json
{
  "institution_id": 1,
  "subdomain": "demo-practice",
  "webhook_subscription_id": 2,
  "resource_type": "Appointment",
  "event_name": "appointment_updated",
  "event_time": "2026-10-19T15:42:00Z",
  "data": {
    "appointment": {
      "id": 123456
    }
  }
}
```

Treat examples as illustrative rather than exhaustive. Always use the current webhook subscription reference when building payload models:

https://docs.nexhealth.com/reference/webhook-subscriptions

---

# Signature Verification

Never trust a webhook solely because it reached the correct URL.

NexHealth signs every webhook event. Webhook requests include:

```text
timestamp
signature
content-type
```

NexHealth uses HMAC SHA-256 with the `secret_key` associated with the webhook endpoint.

The verification process is:

```text
Incoming POST
      |
      v
Read raw request body
      |
      v
Base64 encode raw body
      |
      v
Build:
timestamp + "." + base64_body
      |
      v
HMAC-SHA256 using endpoint secret_key
      |
      v
Compare expected signature
with signature header
      |
      +---- mismatch ---> Reject request
      |
      v
Process webhook
      |
      v
Return HTTP 2xx
```

The body should be verified exactly as received. Do **not** parse the JSON and then serialize it again before signature verification; byte-level differences can change the signature.

A Python implementation can look like:

```python
import base64
import hashlib
import hmac


def verify_nexhealth_signature(
    raw_body: bytes,
    timestamp: str,
    received_signature: str,
    secret_key: str
) -> bool:
    encoded_body = base64.b64encode(raw_body).decode("utf-8")

    signed_payload = f"{timestamp}.{encoded_body}"

    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        received_signature
    )
```

A FastAPI handler could then follow this pattern:

```python
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


@app.post("/nexhealth/webhooks")
async def nexhealth_webhook(request: Request):
    raw_body = await request.body()

    timestamp = request.headers.get("timestamp")
    signature = request.headers.get("signature")

    if not timestamp or not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature headers"
        )

    if not verify_nexhealth_signature(
        raw_body=raw_body,
        timestamp=timestamp,
        received_signature=signature,
        secret_key=NEXHEALTH_WEBHOOK_SECRET
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    payload = await request.json()

    # Persist or enqueue the webhook here.

    return {
        "received": True
    }
```

Load the secret from secure configuration or a secrets manager rather than hard-coding it.

---

# Return HTTP 2xx Quickly

Webhook receivers should acknowledge valid events quickly.

```text
Receive event
    |
    v
Verify signature
    |
    v
Persist / enqueue event
    |
    v
Return 2xx
    |
    v
Perform heavier processing separately
```

Avoid making the webhook HTTP request wait on long-running application work. This reduces the chance of retries caused by timeouts or temporary downstream failures.

---

# Retries and Failing Endpoints

If a webhook delivery does not receive a `2xx` response, NexHealth currently retries delivery seven times over roughly eleven hours.

| Retry | Wait after previous attempt | Time since first attempt |
|---:|---:|---:|
| 1 | 30 seconds | 30 seconds |
| 2 | 2 minutes | 2.5 minutes |
| 3 | 5 minutes | 7.5 minutes |
| 4 | 15 minutes | 22.5 minutes |
| 5 | 1 hour | 1 hour 23 minutes |
| 6 | 3 hours | 4 hours 23 minutes |
| 7 | 7 hours | 11 hours 23 minutes |

NexHealth also documents protection behavior for repeatedly failing endpoints.

After more than ten consecutive failed attempts, NexHealth can temporarily pause delivery to the endpoint for 60 minutes. Events due during that pause can be marked `skipped` rather than replayed later.

If a delivery exhausts its retries and the last 100 finished deliveries to the endpoint have all failed, NexHealth can set the endpoint's `active` field to `false`.

Reactivating the endpoint does not necessarily reactivate its subscriptions automatically; inactive subscriptions may also need to be re-enabled.

Because retry behavior can change, treat the live NexHealth webhook guide as the source of truth:

https://docs.nexhealth.com/docs/webhooks

---

# Delivery Semantics

NexHealth's current webhook guide states that webhook payloads do not contain a separate event ID.

An event is normally sent once and is resent when NexHealth does not receive a `2xx` response.

Webhook handlers should therefore be designed to be **idempotent** where practical.

```text
Webhook arrives
      |
      v
Check whether the state/change
has already been processed
      |
      +---- yes ---> safely acknowledge
      |
      v
Apply change
      |
      v
Mark processed
```

---

# Change Events vs. Insertion Events

These are different concepts.

## Change events

Examples:

```text
appointment_created
appointment_updated
patient_created
patient_updated
procedure_updated
```

These fire when NexHealth detects a change while reading from the health record system.

For on-premises systems, NexHealth currently documents that reads commonly occur every 10–15 minutes, so change webhooks can arrive in groups rather than instantly.

## Insertion events

Examples:

```text
appointment_insertion
payment_insertion
adjustment_insertion
document_insertion
```

These report the result of an API-initiated write into the health record system.

Think:

```text
API response       = NexHealth accepted the request
Insertion webhook  = What ultimately happened in the EHR
```

That distinction is critical.

---

# Sync Status Events

NexHealth currently supports:

```text
sync_status_read_change
sync_status_write_change
```

The event name includes the resulting state:

```text
sync_status_read_change.red
sync_status_read_change.green

sync_status_write_change.red
sync_status_write_change.green
```

NexHealth still recommends checking timestamps returned by:

```http
GET /sync_status
```

particularly:

```text
read_status_at
write_status_at
```

Those timestamps help determine how recent the observed sync health actually is.

---

# Endpoint vs. Subscription vs. Incoming Event

This is the most important naming distinction in the webhook API.

## Webhook endpoint

```http
GET /webhook_endpoints
```

This does **not** retrieve webhook events.

It returns the URLs NexHealth is configured to send webhook events to.

```text
Webhook endpoint = destination
```

## Webhook subscription

```http
GET /webhook_endpoints/{id}/webhook_subscriptions
```

This does **not** retrieve delivered event history.

It controls which types of events NexHealth sends to that destination.

```text
Webhook subscription = event configuration
```

## Incoming webhook route

```text
https://yourapp.example.com/nexhealth/webhooks
```

This is where your application actually receives event POSTs from NexHealth.

```text
Incoming route = receiver
```

Together:

```text
/webhook_endpoints
        |
        | defines
        v
WHERE events go
        |
        v
/webhook_subscriptions
        |
        | defines
        v
WHAT events go there
        |
        v
https://yourapp.example.com/nexhealth/webhooks
        |
        | receives
        v
EVENT PAYLOADS
```

---

# Suggested SDK Abstraction

The low-level NexHealth API exposes endpoints and subscriptions directly. A Python SDK can make that easier to use.

For example:

```python
client.webhooks.create_endpoint(
    target_url="https://api.example.com/nexhealth/webhooks"
)
```

Then:

```python
client.webhooks.subscribe(
    endpoint_id=123,
    resource_type="Appointment",
    event="appointment_updated"
)
```

The SDK could also expose management methods:

```python
client.webhooks.list_endpoints()

client.webhooks.list_subscriptions(
    endpoint_id=123
)

client.webhooks.pause_subscription(
    endpoint_id=123,
    subscription_id=456
)

client.webhooks.delete_subscription(
    endpoint_id=123,
    subscription_id=456
)
```

Signature verification could also be provided by the SDK:

```python
client.webhooks.verify_signature(
    raw_body=raw_body,
    timestamp=timestamp,
    signature=signature,
    secret_key=secret_key
)
```

A higher-level framework integration could eventually support:

```python
@nexhealth_webhook("appointment_updated")
def appointment_updated(event):
    print(event.data.appointment.id)
```

That decorator would be an SDK convenience feature, not a native NexHealth API feature.

---

# Recommended Production Pattern

A robust NexHealth webhook consumer should generally:

```text
1. Receive POST
2. Read raw body
3. Verify HMAC signature
4. Reject invalid requests
5. Parse JSON
6. Validate resource_type / event_name
7. Persist or enqueue the event
8. Return 2xx quickly
9. Process asynchronously
10. Make processing idempotent
11. Log failures without exposing PHI
12. Periodically reconcile important resources through the API
```

For asynchronous API writes:

```text
1. Send NexHealth API request
2. Store returned NexHealth resource ID
3. Treat initial success as accepted
4. Wait for the appropriate insertion/update webhook
5. Correlate webhook to stored resource
6. Mark write complete / failed / timed out
7. Handle failures explicitly
```

---

# Security Notes

Webhook payloads can contain PHI.

Production systems should:

- use HTTPS;
- verify every signature;
- keep `secret_key` values out of source control;
- avoid logging full webhook bodies unless logging is appropriately secured;
- avoid storing unnecessary PHI;
- restrict access to webhook logs and queues;
- use secure secrets storage in production;
- validate event/resource values before processing;
- make handlers resilient to malformed or unexpected payloads.

Never place a webhook secret in:

```text
README.md
source code
Git commit history
.env.example
public logs
```

A local `.env` file is acceptable for development when it is excluded from Git.

---

# Summary

Webhooks convert a NexHealth integration from purely request/response behavior into an event-driven integration.

Without webhooks:

```text
Your application asks NexHealth what changed.
```

With webhooks:

```text
NexHealth tells your application what changed.
```

They are particularly important for:

- real-time change tracking;
- reducing unnecessary polling;
- detecting EHR-side changes;
- tracking sync-health changes;
- confirming asynchronous writes;
- determining whether appointments, payments, adjustments, documents, and other records actually reached the connected health record system.

For a reusable Python client, webhook support is therefore more than an optional convenience. It is a core part of building reliable NexHealth integrations.

---

# Official NexHealth References

- Setting up webhooks  
  https://docs.nexhealth.com/docs/webhooks

- Webhook subscriptions  
  https://docs.nexhealth.com/reference/webhook-subscriptions

- Create webhook subscription  
  https://docs.nexhealth.com/reference/postwebhookendpointsidwebhooksubscriptions

- Data pipelines  
  https://docs.nexhealth.com/docs/data-pipelines

- How a write reaches the health record system  
  https://docs.nexhealth.com/docs/how-a-write-reaches-the-ehr
