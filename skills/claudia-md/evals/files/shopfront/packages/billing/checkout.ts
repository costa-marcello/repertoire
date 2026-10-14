import Stripe from "stripe";
import { randomUUID } from "node:crypto";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY ?? "");

export async function createCheckout(priceId: string, customerId: string) {
  return stripe.checkout.sessions.create(
    { mode: "subscription", customer: customerId, line_items: [{ price: priceId, quantity: 1 }] },
    { idempotencyKey: randomUUID() },
  );
}
