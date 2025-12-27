import { getCart } from 'lib/medusa';
import { cookies } from 'next/headers';
import CartView from 'components/cart/cart-view';

export const metadata = {
  title: 'Cart',
  description: 'View your cart'
};

export default async function CartPage() {
  const cartId = cookies().get('cartId')?.value;
  let cart;

  if (cartId) {
    cart = await getCart(cartId);
  }

  return <CartView cart={cart || undefined} />;
}
