'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 60) return `${diffMins} minutes ago`;
  if (diffHours < 24) return `${diffHours} hours ago`;
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return date.toLocaleDateString();
}

interface Order {
  id: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total: number;
  currency: string;
  createdAt: string;
  itemCount: number;
  shippingAddress?: {
    city: string;
    country: string;
  };
}

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  processing: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  shipped: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  delivered: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  cancelled: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
};

export function OrderHistory() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/orders');
      if (response.ok) {
        const data = await response.json();
        setOrders(data.orders);
      } else {
        // Mock data for demonstration
        setOrders([
          {
            id: 'order_123456',
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
            id: 'order_123457',
            status: 'shipped',
            total: 89.99,
            currency: 'USD',
            createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            itemCount: 2,
            shippingAddress: {
              city: 'Los Angeles',
              country: 'US'
            }
          },
          {
            id: 'order_123458',
            status: 'processing',
            total: 245.00,
            currency: 'USD',
            createdAt: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            itemCount: 5,
            shippingAddress: {
              city: 'Chicago',
              country: 'US'
            }
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to load orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse rounded-lg border border-neutral-200 p-6 dark:border-neutral-800">
            <div className="h-4 w-32 rounded bg-neutral-200 dark:bg-neutral-800" />
            <div className="mt-3 h-4 w-48 rounded bg-neutral-200 dark:bg-neutral-800" />
          </div>
        ))}
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-neutral-200 bg-white p-12 dark:border-neutral-800 dark:bg-black">
        <h2 className="mb-2 text-xl font-semibold">No orders yet</h2>
        <p className="mb-6 text-neutral-600 dark:text-neutral-400">
          Start shopping to see your orders here!
        </p>
        <Link
          href="/search"
          className="rounded-full bg-blue-600 px-6 py-3 text-white transition hover:bg-blue-700"
        >
          Start Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <div
          key={order.id}
          className="rounded-lg border border-neutral-200 bg-white p-6 transition hover:shadow-lg dark:border-neutral-800 dark:bg-black"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex-1">
              <div className="mb-2 flex items-center gap-3">
                <h3 className="font-mono text-sm font-semibold">#{order.id}</h3>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    statusColors[order.status]
                  }`}
                >
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </span>
              </div>
              
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Placed {formatTimeAgo(order.createdAt)}
              </p>
              
              {order.shippingAddress && (
                <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
                  Shipping to {order.shippingAddress.city}, {order.shippingAddress.country}
                </p>
              )}
              
              <p className="mt-2 text-sm">
                <span className="text-neutral-600 dark:text-neutral-400">
                  {order.itemCount} item{order.itemCount !== 1 ? 's' : ''}
                </span>
                <span className="ml-4 font-semibold">
                  ${order.total.toFixed(2)} {order.currency}
                </span>
              </p>
            </div>
            
            <div className="flex gap-2">
              <Link
                href={`/account/orders/${order.id}`}
                className="rounded-lg border border-neutral-300 px-4 py-2 text-sm font-semibold transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
              >
                View Details
              </Link>
              
              {order.status === 'delivered' && (
                <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
                  Buy Again
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
