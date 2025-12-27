import medusaRequest from 'lib/medusa';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { cartId } = await request.json();

  if (!cartId) {
    return NextResponse.json({ error: 'Missing cartId' }, { status: 400 });
  }

  try {
    // 0. Check and Add Shipping Method if missing
    const cartCheckRes = await medusaRequest({
      method: 'GET',
      path: `/carts/${cartId}`,
      cache: 'no-store'
    });

    if (cartCheckRes.body.cart && (!cartCheckRes.body.cart.shipping_methods || cartCheckRes.body.cart.shipping_methods.length === 0)) {
      // Fetch shipping options
      const optionsRes = await medusaRequest({
        method: 'GET',
        path: `/shipping-options?cart_id=${cartId}`,
        cache: 'no-store'
      });

      if (optionsRes.body.shipping_options && optionsRes.body.shipping_options.length > 0) {
        const optionId = optionsRes.body.shipping_options[0].id;
        // Add shipping method
        await medusaRequest({
          method: 'POST',
          path: `/carts/${cartId}/shipping-methods`,
          payload: { option_id: optionId },
          cache: 'no-store'
        });
      }
    }

    // Medusa v2 flow:
    // 1. Create Payment Collection
    const collectionRes = await medusaRequest({
      method: 'POST',
      path: `/payment-collections`,
      payload: { cart_id: cartId },
      cache: 'no-store'
    });

    if (!collectionRes.body.payment_collection) {
      throw new Error('Failed to create payment collection');
    }

    const collectionId = collectionRes.body.payment_collection.id;

    // 2. Initialize Payment Session
    // We use 'pp_stripe_stripe' as the provider ID for Stripe in Medusa v2
    const sessionRes = await medusaRequest({
      method: 'POST',
      path: `/payment-collections/${collectionId}/payment-sessions`,
      payload: { provider_id: 'pp_stripe_stripe' },
      cache: 'no-store'
    });

    if (!sessionRes.body.payment_collection) {
      throw new Error('Failed to create payment session');
    }

    // 3. Fetch updated cart to return to frontend
    const cartRes = await medusaRequest({
      method: 'GET',
      path: `/carts/${cartId}`,
      cache: 'no-store'
    });

    if (cartRes.body.cart) {
      return NextResponse.json({ cart: cartRes.body.cart });
    } else {
      console.error('Failed to retrieve updated cart:', cartRes.body);
      return NextResponse.json({ error: 'Failed to retrieve updated cart' }, { status: 500 });
    }
  } catch (e: any) {
    console.error('Error creating payment session:', e);
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
