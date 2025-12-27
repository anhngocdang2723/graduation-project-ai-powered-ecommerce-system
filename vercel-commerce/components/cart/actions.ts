'use server';

import { addToCart, createCart, getCart, removeFromCart, updateCart } from 'lib/medusa';
import { cookies } from 'next/headers';
import { revalidateTag } from 'next/cache';

export const addItem = async (variantId: string | undefined, quantity: number = 1): Promise<String | undefined> => {
  console.log(`[addItem] Called with variantId: ${variantId}, quantity: ${quantity}`);
  let cartId = cookies().get('cartId')?.value;
  let cart;

  if (cartId) {
    console.log(`[addItem] Found existing cartId: ${cartId}`);
    cart = await getCart(cartId);
    console.log(`[addItem] Existing cart:`, cart ? `${cart.lines.length} items` : 'null');
  }

  if (!cartId || !cart) {
    console.log(`[addItem] Creating new cart...`);
    try {
      cart = await createCart();
    } catch (e) {
      console.error("[addItem] Error in createCart:", e);
      return 'Error creating cart (exception)';
    }

    if (!cart) {
      console.error("[addItem] createCart returned null");
      return 'Error creating cart';
    }
    cartId = cart.id!;
    console.log("[addItem] Created new cart:", cartId);
    cookies().set('cartId', cartId, {
      path: '/',
      maxAge: 60 * 60 * 24 * 30,
      sameSite: 'lax',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production'
    });
  }

  if (!variantId) {
    console.error("[addItem] Missing variantId");
    return 'Missing product variant ID';
  }

  console.log(`[addItem] About to call addToCart with cartId: ${cartId}, variantId: ${variantId}, quantity: ${quantity}`);
  
  try {
    const result = await addToCart(cartId, { variantId, quantity });
    if (!result) {
      console.error("[addItem] addToCart returned null");
      return 'Failed to add item to cart';
    }
    console.log("[addItem] Item added successfully. Cart now has:", result.totalQuantity, "items");
    revalidateTag('cart');
  } catch (e: any) {
    console.error("[addItem] Exception in addToCart:", e);
    return `Error adding item to cart: ${e.message || e}`;
  }
};

export const removeItem = async (lineId: string): Promise<String | undefined> => {
  const cartId = cookies().get('cartId')?.value;

  if (!cartId) {
    return 'Missing cart ID';
  }
  try {
    const cart = await getCart(cartId);
    if (!cart) {
      // Cart is invalid or completed (reshapeCart returns null for completed carts)
      // Clear cookie and return success (effectively "removed" since cart is gone)
      cookies().delete('cartId');
      revalidateTag('cart');
      return;
    }
    await removeFromCart(cartId, lineId);
    revalidateTag('cart');
  } catch (e) {
    return 'Error removing item from cart';
  }
};

export const updateItemQuantity = async ({
  lineId,
  variantId,
  quantity
}: {
  lineId: string;
  variantId: string;
  quantity: number;
}): Promise<String | undefined> => {
  const cartId = cookies().get('cartId')?.value;

  if (!cartId) {
    return 'Missing cart ID';
  }
  try {
    const cart = await getCart(cartId);
    if (!cart) {
      // Cart is invalid or completed
      cookies().delete('cartId');
      revalidateTag('cart');
      return 'Cart is no longer valid';
    }
    await updateCart(cartId, {
      lineItemId: lineId,
      quantity
    });
    revalidateTag('cart');
  } catch (e) {
    return 'Error updating item quantity';
  }
};

export const updateLineItemVariant = async (
  lineId: string,
  variantId: string,
  quantity: number
): Promise<String | undefined> => {
  const cartId = cookies().get('cartId')?.value;
  if (!cartId) return 'Missing cart ID';

  try {
    // Since Medusa doesn't support direct variant swap on a line item,
    // we remove the old one and add the new one.
    await removeFromCart(cartId, lineId);
    await addToCart(cartId, { variantId, quantity });
    revalidateTag('cart');
  } catch (e: any) {
    console.error("Error updating line item variant:", e);
    return `Error updating item: ${e.message || e}`;
  }
};
