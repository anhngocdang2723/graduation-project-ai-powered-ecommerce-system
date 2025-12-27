import { createCart, getCart } from 'lib/medusa';
import { cookies } from 'next/headers';
import CartModal from './modal';

export default async function Cart() {
  const cartId = cookies().get('cartId')?.value;
  console.log("Cart component - cartId from cookie:", cartId);
  let cart;

  if (cartId) {
    cart = await getCart(cartId);
  }

  // If the `cartId` from the cookie is not set or the cart is empty
  // (old carts becomes `null` when you checkout), then get a new `cartId`
  //  and re-fetch the cart.
  if (!cartId || !cart) {
    // Note: This creates a cart but cannot set the cookie in a Server Component.
    // The cookie must be set by a Server Action or Middleware.
    // We only create it here to display an empty cart if needed, 
    // but ideally the client should trigger creation via action if it wants to persist it.
    cart = await createCart();
  }

  return <CartModal cart={cart || undefined} />;
}
