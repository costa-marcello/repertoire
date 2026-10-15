import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY ?? "");

// The key comes from the order, so a retry of the same order reuses it.
export async function createCheckout(orderId: string, priceId: string, customerId: string) {
  return stripe.checkout.sessions.create(
    { mode: "subscription", customer: customerId, line_items: [{ price: priceId, quantity: 1 }] },
    { idempotencyKey: `checkout-${orderId}` },
  );
}
