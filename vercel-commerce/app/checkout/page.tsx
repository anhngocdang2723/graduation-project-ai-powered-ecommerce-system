import { CheckoutForm } from 'components/checkout/checkout-form';
import Link from 'next/link';
import { getCart } from 'lib/medusa';
import { cookies } from 'next/headers';

export const metadata = {
  title: 'Checkout',
  description: 'Complete your purchase'
};

export default async function CheckoutPage() {
  const cartId = cookies().get('cartId')?.value;
  let cart;

  if (cartId) {
    cart = await getCart(cartId);
  }

  const cartItems = cart?.lines || [];

  return (
    <div className="mx-auto max-w-screen-xl px-4 py-8">
      <div className="mb-8">
        <Link
          href="/cart"
          className="text-sm text-blue-600 hover:underline dark:text-blue-400"
        >
          ← Back to Cart
        </Link>
        <h1 className="mt-2 text-3xl font-bold">Checkout</h1>
      </div>

      <CheckoutForm cart={cart} cartId={cartId} />
    </div>
  );
}
