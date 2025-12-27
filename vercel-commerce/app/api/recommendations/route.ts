import { NextRequest, NextResponse } from 'next/server';

const RECOMMENDATION_SERVICE_URL = process.env.RECOMMENDATION_SERVICE_URL || 'http://localhost:8001';

// Disable Next.js caching for this route
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const userId = searchParams.get('userId') || '';
    const sessionId = searchParams.get('sessionId') || '';
    const productHandle = searchParams.get('productHandle');
    const context = searchParams.get('context') || 'homepage';
    const limit = parseInt(searchParams.get('limit') || '8');

    console.log('[Recommendations API] Request:', { userId, sessionId, productHandle, context, limit });

    // Build query params
    let queryParams = `user_id=${userId}&session_id=${sessionId}&context=${context}&limit=${limit}`;
    if (productHandle) {
      queryParams += `&product_handle=${productHandle}`;
    }

    const fullUrl = `${RECOMMENDATION_SERVICE_URL}/recommendations?${queryParams}`;
    console.log('[Recommendations API] Calling:', fullUrl);

    // Call Python recommendation service
    const response = await fetch(
      fullUrl,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // Disable fetch caching
      }
    );

    console.log('[Recommendations API] Response status:', response.status);

    if (!response.ok) {
      console.error('[Recommendations API] Service error:', response.status);
      // Fallback to empty recommendations
      return NextResponse.json({ 
        recommendations: [],
        algorithm: 'none',
        error: 'Service unavailable'
      });
    }

    const data = await response.json();
    console.log('[Recommendations API] Returning', data.recommendations?.length || 0, 'products');

    // Return with no-cache headers
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });

  } catch (error) {
    console.error('[Recommendations API] Error:', error);
    return NextResponse.json({ 
      recommendations: [],
      algorithm: 'none',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
