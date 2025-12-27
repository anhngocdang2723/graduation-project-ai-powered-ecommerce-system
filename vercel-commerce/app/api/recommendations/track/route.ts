import { NextRequest, NextResponse } from 'next/server';

const RECOMMENDATION_SERVICE_URL = process.env.RECOMMENDATION_SERVICE_URL || 'http://localhost:8001';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    console.log('[Track API] Received event:', body);

    // Transform frontend format to backend format
    const trackPayload = {
      user_id: body.userId || body.user_id,
      session_id: body.sessionId || body.session_id || '',
      product_id: body.productId || body.product_id || null,
      product_handle: body.productHandle || body.product_handle || null,
      interaction_type: body.interactionType || body.interaction_type,
      metadata: body.metadata || {}
    };

    console.log('[Track API] Sending to service:', trackPayload);

    // Forward to Python recommendation service
    const response = await fetch(`${RECOMMENDATION_SERVICE_URL}/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(trackPayload),
    });

    if (!response.ok) {
      console.error('[Track API] Service error:', response.status);
      // Don't fail tracking - just log
      return NextResponse.json({ 
        success: false, 
        error: 'Service unavailable',
        logged_locally: true 
      });
    }

    const data = await response.json();
    console.log('[Track API] Service response:', data);
    
    return NextResponse.json({ success: true, data });

  } catch (error) {
    console.error('[Track API] Error:', error);
    // Don't fail the request even if tracking fails
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error',
      logged_locally: true
    });
  }
}
