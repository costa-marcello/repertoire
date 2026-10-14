# billing

Stripe subscriptions and one-time payments for shopfront.

- Webhooks need `STRIPE_WEBHOOK_SECRET`. Without it, `handleWebhook` rejects every event.
- Every Stripe call that creates or changes an object passes an idempotency key, so a retried request never charges a customer twice.
