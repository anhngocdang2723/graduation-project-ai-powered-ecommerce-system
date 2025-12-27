'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function OrderDetailsPage() {
  const params = useParams();
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params?.id) {
      fetch(`/api/orders/${params.id}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.order) {
            setOrder(data.order);
          }
        })
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [params?.id]);

  if (loading) return <div className="p-8 text-center">Loading order details...</div>;
  if (!order) return <div className="p-8 text-center">Order not found</div>;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Order #{order.id}</h1>
        <Link href="/account/orders" className="text-blue-600 hover:underline">
          &larr; Back to Orders
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border p-6">
          <h2 className="mb-4 text-lg font-semibold">Order Summary</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Status:</span>
              <span className="font-medium capitalize">{order.status}</span>
            </div>
            <div className="flex justify-between">
              <span>Date:</span>
              <span>{new Date(order.createdAt).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span>{order.total.toLocaleString()} {order.currency}</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border p-6">
          <h2 className="mb-4 text-lg font-semibold">Shipping Address</h2>
          {order.shippingAddress ? (
            <address className="not-italic">
              {order.shippingAddress.first_name} {order.shippingAddress.last_name}<br />
              {order.shippingAddress.address_1}<br />
              {order.shippingAddress.city}, {order.shippingAddress.postal_code}<br />
              {order.shippingAddress.country_code?.toUpperCase()}
            </address>
          ) : (
            <p className="text-gray-500">No shipping address</p>
          )}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="mb-4 text-lg font-semibold">Items</h2>
        <div className="rounded-lg border">
          {order.items.map((item: any, index: number) => (
            <div key={index} className="flex items-center gap-4 border-b p-4 last:border-0">
              {item.thumbnail && (
                <img src={item.thumbnail} alt={item.title} className="h-16 w-16 rounded object-cover" />
              )}
              <div className="flex-1">
                <h3 className="font-medium">{item.title}</h3>
                <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
              </div>
              <div className="font-medium">
                {(item.unit_price * item.quantity).toLocaleString()} {order.currency}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
