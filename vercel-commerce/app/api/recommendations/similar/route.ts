import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const productId = searchParams.get('productId');

    if (!productId) {
      return NextResponse.json(
        { error: 'productId is required' },
        { status: 400 }
      );
    }

    // Call recommendation service for similar products
    const response = await fetch(`${process.env.RECOMMENDATION_SERVICE_URL}/api/v1/recommendations/similar?product_id=${productId}&limit=5`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Recommendation service error: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching similar products:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch similar products' },
      { status: 500 }
    );
  }
}