import { NextResponse } from 'next/server';

const MEDUSA_BACKEND_URL = process.env.NEXT_PUBLIC_MEDUSA_BACKEND_API || 'http://localhost:9000';
const ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3Rvcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMiLCJhY3Rvcl90eXBlIjoidXNlciIsImF1dGhfaWRlbnRpdHlfaWQiOiJhdXRoaWRfMDFLQ0JIOU5RUTkzNEVNR1RaMzdTODIxRkoiLCJhcHBfbWV0YWRhdGEiOnsidXNlcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMifSwidXNlcl9tZXRhZGF0YSI6e30sImlhdCI6MTc2NjY3NTY5OCwiZXhwIjoxNzY2NzYyMDk4fQ.8ufPhyL7piP2uz1rqL3mjpVxgaIb_z0UNYdEpda9NNk";

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id;

  // Check if it's a mock order
  if (id.startsWith('order_mock_')) {
    // Return mock data
    return NextResponse.json({
      order: {
        id,
        status: 'delivered',
        total: 125.50,
        currency: 'USD',
        createdAt: new Date().toISOString(),
        items: [
          { title: 'Mock Item 1', quantity: 2, unit_price: 50.00, thumbnail: '' },
          { title: 'Mock Item 2', quantity: 1, unit_price: 25.50, thumbnail: '' }
        ],
        shippingAddress: {
          first_name: 'John',
          last_name: 'Doe',
          address_1: '123 Mock St',
          city: 'New York',
          country_code: 'us',
          postal_code: '10001'
        }
      }
    });
  }

  try {
    const response = await fetch(`${MEDUSA_BACKEND_URL}/admin/orders/${id}?fields=+currency_code,+items.*,+shipping_address.*,+summary`, {
      headers: {
        'Authorization': `Bearer ${ADMIN_TOKEN}`,
        'Content-Type': 'application/json',
      },
      next: { revalidate: 0 }
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Order not found' }, { status: 404 });
    }

    const data = await response.json();
    const order = data.order;

    // Normalize
    let total = order.total;
    const currency = order.currency_code?.toUpperCase() || 'USD';
    if (!['VND', 'JPY', 'KRW'].includes(currency)) {
      total = total / 100;
    }

    const normalizedOrder = {
      id: order.id,
      status: order.status,
      total,
      currency,
      createdAt: order.created_at,
      items: order.items.map((item: any) => ({
        title: item.title,
        quantity: item.quantity,
        unit_price: ['VND', 'JPY', 'KRW'].includes(currency) ? item.unit_price : item.unit_price / 100,
        thumbnail: item.thumbnail
      })),
      shippingAddress: order.shipping_address
    };

    return NextResponse.json({ order: normalizedOrder });
  } catch (error) {
    console.error('Error fetching order:', error);
    return NextResponse.json({ error: 'Failed to fetch order' }, { status: 500 });
  }
}
