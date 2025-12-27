import medusaRequest from 'lib/medusa';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { cartId } = await request.json();

  if (!cartId) {
    return NextResponse.json({ error: 'Missing cartId' }, { status: 400 });
  }

  try {
    // 0. Check and Update Shipping Method if invalid
    const cartRes = await medusaRequest({
      method: 'GET',
      path: `/carts/${cartId}`,
      cache: 'no-store'
    });

    const cart = cartRes.body.cart;
    if (!cart) {
      return NextResponse.json({ error: 'Cart not found' }, { status: 404 });
    }

    // Fetch valid shipping options for current cart state
    const optionsRes = await medusaRequest({
      method: 'GET',
      path: `/shipping-options?cart_id=${cartId}`,
      cache: 'no-store'
    });

    const validOptions = optionsRes.body.shipping_options || [];
    const validOptionIds = validOptions.map((opt: any) => opt.id);

    let needsShippingUpdate = false;
    
    if (!cart.shipping_methods || cart.shipping_methods.length === 0) {
      // No shipping method at all
      needsShippingUpdate = true;
      console.log(`[complete-cart] Cart ${cartId} has no shipping methods`);
    } else {
      // Check if current shipping method is valid
      const currentShippingOptionId = cart.shipping_methods[0]?.shipping_option_id;
      if (!validOptionIds.includes(currentShippingOptionId)) {
        needsShippingUpdate = true;
        console.log(`[complete-cart] Cart ${cartId} has invalid shipping method ${currentShippingOptionId}. Valid options: ${validOptionIds.join(', ')}`);
      }
    }

    if (needsShippingUpdate) {
      if (validOptions.length === 0) {
        return NextResponse.json({ error: 'No shipping options available for this cart' }, { status: 400 });
      }

      const optionId = validOptions[0].id;
      console.log(`[complete-cart] Setting shipping method ${optionId} for cart ${cartId}`);
      
      const shippingRes = await medusaRequest({
        method: 'POST',
        path: `/carts/${cartId}/shipping-methods`,
        payload: { option_id: optionId },
        cache: 'no-store'
      });

      if (!shippingRes.body.cart) {
        console.error(`[complete-cart] Failed to set shipping method:`, shippingRes.body);
        return NextResponse.json({ error: 'Failed to set shipping method' }, { status: 500 });
      }
    }

    // 1. Create Payment Collection
    const collectionRes = await medusaRequest({
      method: 'POST',
      path: `/payment-collections`,
      payload: { cart_id: cartId },
      cache: 'no-store'
    });

    let collectionId;
    if (collectionRes.body.payment_collection) {
      collectionId = collectionRes.body.payment_collection.id;
    } else {
      // If creation fails, maybe one already exists? 
      // For now, let's assume we can create one or we need to find it.
      // But let's proceed with the assumption that we got one or we can't proceed.
      // Actually, if we already created one for Stripe, we might want to use that one?
      // But switching providers might require a new session in the same collection.
      console.error('Failed to create payment collection:', collectionRes.body);
      // If it fails, it might be because one exists. Let's try to list them or just proceed to complete if possible.
      // But for COD, we need a session.
      return NextResponse.json({ error: 'Failed to initialize payment' }, { status: 500 });
    }

    // 2. Initialize Payment Session with System Default (for COD)
    const sessionRes = await medusaRequest({
      method: 'POST',
      path: `/payment-collections/${collectionId}/payment-sessions`,
      payload: { provider_id: 'pp_system_default' },
      cache: 'no-store'
    });

    if (!sessionRes.body.payment_collection) {
      throw new Error('Failed to create COD payment session');
    }

    // 3. Complete the Cart
    const completeRes = await medusaRequest({
      method: 'POST',
      path: `/carts/${cartId}/complete`,
      cache: 'no-store'
    });

    if (completeRes.body.type === 'order') {
      return NextResponse.json({ 
        success: true, 
        orderId: completeRes.body.order.id,
        message: 'Order placed successfully'
      });
    } else {
      console.error('Failed to complete cart:', completeRes.body);
      return NextResponse.json({ error: 'Failed to complete order' }, { status: 500 });
    }

  } catch (e: any) {
    console.error('Error completing order:', e);
    return NextResponse.json({ error: e.message || 'An error occurred' }, { status: 500 });
  }
}
