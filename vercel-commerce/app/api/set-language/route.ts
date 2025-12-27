import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { language } = await request.json();
    
    if (!language || !['EN', 'VI'].includes(language)) {
      return NextResponse.json({ error: 'Invalid language' }, { status: 400 });
    }

    const cookieStore = await cookies();
    cookieStore.set('language', language, {
      path: '/',
      maxAge: 60 * 60 * 24 * 365, // 1 year
      sameSite: 'lax'
    });

    return NextResponse.json({ success: true, language });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to set language' }, { status: 500 });
  }
}
