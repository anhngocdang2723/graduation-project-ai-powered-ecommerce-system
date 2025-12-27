import { GridTileImage } from 'components/grid/tile';
import { Gallery } from 'components/product/gallery';
import { EditItemView } from 'components/cart/edit-item-view';
import { getCart, getProduct } from 'lib/medusa';
import { Image } from 'lib/medusa/types';
import { cookies } from 'next/headers';
import { notFound, redirect } from 'next/navigation';

export const runtime = 'edge';

export default async function EditCartItemPage({ params }: { params: { lineId: string } }) {
  const cartId = cookies().get('cartId')?.value;
  let cart;

  if (cartId) {
    cart = await getCart(cartId);
  }

  if (!cart) {
    redirect('/cart');
  }

  const lineItem = cart.lines.find((line) => line.id === params.lineId);

  if (!lineItem || !lineItem.merchandise.product.handle) {
    redirect('/cart');
  }

  const product = await getProduct(lineItem.merchandise.product.handle);

  if (!product) return notFound();

  return (
    <div className="mx-auto max-w-screen-2xl px-4">
      <div className="flex flex-col rounded-lg border border-neutral-200 bg-white p-8 dark:border-neutral-800 dark:bg-black md:p-12 lg:flex-row">
        <div className="h-full w-full basis-full lg:basis-4/6">
          <Gallery
            images={product.images!.map((image: Image) => ({
              src: image.url,
              altText: image.altText
            }))}
          />
        </div>

        <div className="basis-full lg:basis-2/6">
          <EditItemView
            product={product}
            lineId={params.lineId}
            quantity={lineItem.quantity}
            initialSelectedOptions={lineItem.merchandise.selectedOptions}
          />
        </div>
      </div>
    </div>
  );
}
