import { NextResponse } from 'next/server';

const MEDUSA_BACKEND_URL = process.env.NEXT_PUBLIC_MEDUSA_BACKEND_API || 'http://localhost:9000';
// Hardcoded for demo purposes - in production this should be handled via proper auth
const ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3Rvcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMiLCJhY3Rvcl90eXBlIjoidXNlciIsImF1dGhfaWRlbnRpdHlfaWQiOiJhdXRoaWRfMDFLQ0JIOU5RUTkzNEVNR1RaMzdTODIxRkoiLCJhcHBfbWV0YWRhdGEiOnsidXNlcl9pZCI6InVzZXJfMDFLQ0JIOU5LNFZOV1AzVDAzMUtHQ0VWMFMifSwidXNlcl9tZXRhZGF0YSI6e30sImlhdCI6MTc2NjY3NTY5OCwiZXhwIjoxNzY2NzYyMDk4fQ.8ufPhyL7piP2uz1rqL3mjpVxgaIb_z0UNYdEpda9NNk";

export async function GET() {
  try {
    const response = await fetch(`${MEDUSA_BACKEND_URL}/admin/orders?fields=+currency_code,+items.*,+shipping_address.city,+shipping_address.country_code&limit=20&offset=0`, {
      headers: {
        'Authorization': `Bearer ${ADMIN_TOKEN}`,
        'Content-Type': 'application/json',
      },
      next: { revalidate: 0 } // Disable cache
    });

    if (!response.ok) {
      throw new Error(`Medusa API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Transform Medusa orders to the format expected by the frontend
    const orders = data.orders.map((order: any) => {
      // Determine status mapping
      let status = 'pending';
      if (order.status === 'completed') status = 'delivered';
      else if (order.status === 'canceled') status = 'cancelled';
      else if (order.fulfillment_status === 'shipped') status = 'shipped';
      else if (order.payment_status === 'captured') status = 'processing';
      
      // Normalize amount (Medusa returns smallest unit)
      // For VND, it's usually 1-1, for USD it's cents.
      // Simple heuristic: if currency is not VND/JPY/KRW, divide by 100
      let total = order.total;
      const currency = order.currency_code?.toUpperCase() || 'USD';
      if (!['VND', 'JPY', 'KRW'].includes(currency)) {
        total = total / 100;
      }

      return {
        id: order.id,
        status,
        total,
        currency,
        createdAt: order.created_at,
        itemCount: order.items?.length || 0,
        shippingAddress: order.shipping_address ? {
          city: order.shipping_address.city,
          country: order.shipping_address.country_code?.toUpperCase()
        } : undefined
      };
    });

    // Add some mock orders if list is short, to make it look populated (as requested "keep some dummy orders")
    const mockOrders = [
      {
        id: 'order_mock_123456',
        status: 'delivered',
        total: 125.50,
        currency: 'USD',
        createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        itemCount: 3,
        shippingAddress: {
          city: 'New York',
          country: 'US'
        }
      },
      {
        id: 'order_mock_123457',
        status: 'shipped',
        total: 89.99,
        currency: 'USD',
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        itemCount: 2,
        shippingAddress: {
          city: 'Los Angeles',
          country: 'US'
        }
      }
    ];

    return NextResponse.json({ orders: [...orders, ...mockOrders] });
  } catch (error) {
    console.error('Error fetching orders:', error);
    return NextResponse.json({ error: 'Failed to fetch orders' }, { status: 500 });
  }
}
