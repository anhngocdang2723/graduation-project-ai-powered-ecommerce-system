import { WishlistGrid } from './wishlist-grid';

export const metadata = {
  title: 'Wishlist',
  description: 'View your saved products'
};

export default async function WishlistPage() {
  return (
    <div className="mx-auto max-w-screen-2xl px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">My Wishlist</h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Save your favorite products to buy later
        </p>
      </div>
      <WishlistGrid />
    </div>
  );
}
