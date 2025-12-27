import { addToCart, createCart, getCart } from 'lib/medusa';
import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { merchandiseId, quantity = 1 } = body;

    if (!merchandiseId) {
      return NextResponse.json(
        { error: 'merchandiseId is required' },
        { status: 400 }
      );
    }

    // Get existing cart or create new one
    const cookieStore = cookies();
    let cartId = cookieStore.get('cartId')?.value;
    
    if (!cartId) {
      // Create new cart
      const newCart = await createCart();
      if (!newCart) {
        throw new Error('Failed to create cart');
      }
      cartId = newCart.id;
      
      // Set cookie (will be handled by the response)
      cookieStore.set('cartId', cartId!, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7 // 7 days
      });
    }

    // Add item to cart
    const result = await addToCart(cartId!, {
      variantId: merchandiseId,
      quantity: quantity
    });

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error adding to cart:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to add to cart' },
      { status: 500 }
    );
  }
}
