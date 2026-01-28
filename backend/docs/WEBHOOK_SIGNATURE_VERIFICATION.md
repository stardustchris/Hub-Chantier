# Webhook Signature Verification Guide

Hub Chantier webhooks use **HMAC-SHA256** signatures to verify that webhook requests are authentic and haven't been tampered with.

## Overview

When your webhook endpoint receives a request from Hub Chantier, the payload includes a signature in the HTTP headers. You **MUST** verify this signature to ensure the request is legitimate.

## Signature Format

The signature is provided in the `X-Hub-Chantier-Signature` header with the format:
```
sha256=<hex_digest>
```

Example:
```
X-Hub-Chantier-Signature: sha256=5d41402abc4b2a76b9719d911017c592
```

## How to Verify

### 1. Extract the Signature

```python
signature_header = request.headers.get('X-Hub-Chantier-Signature', '')
# signature_header = "sha256=abc123..."

# Remove the "sha256=" prefix
received_signature = signature_header.replace("sha256=", "")
```

### 2. Compute Expected Signature

Use the **secret** provided when you created the webhook (shown only once) to compute the HMAC-SHA256 hash of the request body:

```python
import hmac
import hashlib

# Your webhook secret (provided at creation - store securely!)
webhook_secret = "your_webhook_secret_here"

# Raw request body as string
payload = request.get_data(as_text=True)

# Compute HMAC-SHA256
expected_signature = hmac.new(
    webhook_secret.encode('utf-8'),
    payload.encode('utf-8'),
    hashlib.sha256
).hexdigest()
```

### 3. Compare Signatures (Constant-Time)

**CRITICAL**: Use `hmac.compare_digest()` for timing-attack-resistant comparison:

```python
if hmac.compare_digest(expected_signature, received_signature):
    print("✅ Signature valid - webhook is authentic")
    # Process the webhook
else:
    print("❌ Signature invalid - reject the request")
    # Return HTTP 401 Unauthorized
```

**⚠️ DO NOT** use regular string comparison (`==`) as it's vulnerable to timing attacks.

---

## Complete Example (Python/Flask)

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)

# Store this securely (environment variable, secrets manager, etc.)
WEBHOOK_SECRET = "your_webhook_secret_here"

def verify_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """
    Verify HMAC-SHA256 signature from Hub Chantier webhook.

    Args:
        payload: Raw request body (bytes)
        signature_header: Value of X-Hub-Chantier-Signature header

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature_header.startswith('sha256='):
        return False

    received_signature = signature_header.replace("sha256=", "")

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, received_signature)

@app.route('/webhooks/hub-chantier', methods=['POST'])
def handle_webhook():
    # Get raw body (important: before parsing JSON)
    payload = request.get_data()

    # Get signature header
    signature = request.headers.get('X-Hub-Chantier-Signature', '')

    # Verify signature
    if not verify_webhook_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    # Parse and process webhook
    event = request.get_json()
    event_type = request.headers.get('X-Hub-Chantier-Event')

    print(f"Received event: {event_type}")
    print(f"Data: {json.dumps(event, indent=2)}")

    # Process the event based on type
    if event_type == 'heures.validated':
        # Sync to payroll system
        pass
    elif event_type == 'chantier.created':
        # Notify management
        pass

    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    app.run(port=8000, ssl_context='adhoc')  # HTTPS required!
```

---

## Complete Example (Node.js/Express)

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();

// Store this securely (environment variable)
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'your_webhook_secret_here';

// IMPORTANT: Use express.raw() to get raw body for signature verification
app.use('/webhooks', express.raw({type: 'application/json'}));

function verifyWebhookSignature(payload, signatureHeader) {
    if (!signatureHeader || !signatureHeader.startsWith('sha256=')) {
        return false;
    }

    const receivedSignature = signatureHeader.replace('sha256=', '');

    const expectedSignature = crypto
        .createHmac('sha256', WEBHOOK_SECRET)
        .update(payload)
        .digest('hex');

    // Use timing-safe comparison
    return crypto.timingSafeEqual(
        Buffer.from(expectedSignature, 'hex'),
        Buffer.from(receivedSignature, 'hex')
    );
}

app.post('/webhooks/hub-chantier', (req, res) => {
    const signature = req.headers['x-hub-chantier-signature'];
    const eventType = req.headers['x-hub-chantier-event'];

    // Verify signature
    if (!verifyWebhookSignature(req.body, signature)) {
        return res.status(401).json({ error: 'Invalid signature' });
    }

    // Parse payload
    const event = JSON.parse(req.body.toString('utf-8'));

    console.log(`Received event: ${eventType}`);
    console.log('Data:', JSON.stringify(event, null, 2));

    // Process event
    switch (eventType) {
        case 'heures.validated':
            // Sync to payroll
            break;
        case 'chantier.created':
            // Notify management
            break;
    }

    res.status(200).json({ status: 'received' });
});

app.listen(8000, () => {
    console.log('Webhook endpoint listening on port 8000 (HTTPS required!)');
});
```

---

## Testing Your Implementation

### Test with cURL

```bash
# 1. Get your webhook secret from Hub Chantier dashboard
SECRET="your_secret_here"

# 2. Create test payload
PAYLOAD='{"event_type":"test.event","data":{"foo":"bar"}}'

# 3. Compute signature
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')

# 4. Send test request
curl -X POST https://your-domain.com/webhooks/hub-chantier \
  -H "Content-Type: application/json" \
  -H "X-Hub-Chantier-Signature: sha256=$SIGNATURE" \
  -H "X-Hub-Chantier-Event: test.event" \
  -d "$PAYLOAD"
```

### Expected Response
- ✅ Valid signature: HTTP 200
- ❌ Invalid signature: HTTP 401

---

## Security Best Practices

### ✅ DO

- **Always verify signatures** before processing webhooks
- **Use constant-time comparison** (`hmac.compare_digest()` or `crypto.timingSafeEqual()`)
- **Store secrets securely** (environment variables, secrets manager)
- **Use HTTPS** for webhook endpoints (required by Hub Chantier)
- **Validate event types** before processing
- **Implement idempotency** (same event may be delivered multiple times)
- **Log verification failures** for security monitoring

### ❌ DON'T

- Don't use regular string comparison (`==`) for signatures (timing attack vulnerability)
- Don't log or expose your webhook secret
- Don't accept HTTP URLs (HTTPS only)
- Don't trust the payload without signature verification
- Don't parse JSON before verifying the signature (signature applies to raw body)

---

## Troubleshooting

### Signature Always Fails

1. **Check you're using the raw request body**
   - Don't parse JSON before computing the signature
   - Signature applies to the exact bytes received

2. **Verify your secret**
   - Ensure you copied the complete secret from creation response
   - Check for extra spaces or newlines

3. **Check header format**
   - Header should be: `X-Hub-Chantier-Signature: sha256=<hex>`
   - Remove "sha256=" prefix before comparison

4. **Encoding issues**
   - Ensure you're encoding strings as UTF-8
   - Use `.encode('utf-8')` in Python

### Need Help?

Contact Hub Chantier support with:
- Your webhook ID
- Example payload and signature that failed
- Code snippet showing your verification logic

---

## Webhook Payload Structure

All webhooks follow this structure:

```json
{
  "event_type": "chantier.created",
  "timestamp": "2026-01-28T10:30:00Z",
  "data": {
    "chantier_id": 123,
    "nom": "Rénovation Rue de la Paix",
    "statut": "ouvert",
    ...
  }
}
```

Headers:
- `X-Hub-Chantier-Signature`: `sha256=<hex_digest>`
- `X-Hub-Chantier-Event`: Event type (e.g., `chantier.created`)
- `Content-Type`: `application/json`
- `User-Agent`: `Hub-Chantier-Webhooks/1.0`

---

## Event Types

Common event types you may receive:

| Event Type | Description |
|------------|-------------|
| `chantier.created` | New construction site created |
| `chantier.updated` | Site details updated |
| `chantier.statut_changed` | Site status changed |
| `heures.validated` | Time entries validated (critical for payroll) |
| `affectation.created` | Worker assigned to site |
| `signalement.created` | Issue reported on site |
| `document.uploaded` | Document added to site |

Use wildcard patterns when subscribing:
- `*` - All events
- `chantier.*` - All chantier events
- `heures.*` - All time tracking events

---

## Rate Limits & Retry Policy

- **Timeout**: 10 seconds per delivery
- **Retries**: Up to 3 attempts with exponential backoff (2, 4, 8 seconds)
- **Auto-disable**: Webhook disabled after 10 consecutive failures
- **Delivery**: Events delivered in near real-time (seconds after occurrence)

---

## Additional Resources

- [Hub Chantier API Documentation](https://hub-chantier.example.com/docs)
- [HMAC-SHA256 Specification (RFC 2104)](https://tools.ietf.org/html/rfc2104)
- [Webhook Best Practices](https://hub-chantier.example.com/docs/webhooks/best-practices)

---

**Last Updated**: 2026-01-28
**Version**: 1.0
