import { NextResponse } from 'next/server';

const ENDPOINT = process.env.NEXT_PUBLIC_MEDUSA_BACKEND_API ?? 'http://localhost:9000';
const MEDUSA_API_KEY = process.env.MEDUSA_API_KEY ?? '';

export async function GET() {
  try {
    const res = await fetch(`${ENDPOINT}/store/regions`, {
      headers: {
        'Content-Type': 'application/json',
        'x-publishable-api-key': MEDUSA_API_KEY
      },
      next: { revalidate: 3600 } // Cache for 1 hour
    });
    
    if (!res.ok) {
      console.error('Medusa regions API error:', res.status, res.statusText);
      return NextResponse.json({ regions: [] }, { status: 200 });
    }
    
    const data = await res.json();
    return NextResponse.json({ regions: data.regions || [] });
  } catch (error) {
    console.error('Failed to fetch regions:', error);
    return NextResponse.json({ regions: [] }, { status: 200 });
  }
}
