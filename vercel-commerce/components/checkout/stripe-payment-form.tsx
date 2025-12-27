'use client';

import { PaymentElement, useElements, useStripe } from '@stripe/react-stripe-js';
import { useState } from 'react';

export function StripePaymentForm({ 
  onSuccess, 
  onError 
}: { 
  onSuccess: () => void; 
  onError: (error: string) => void; 
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/checkout/success`,
      },
      redirect: 'if_required'
    });

    if (error) {
      onError(error.message || 'An unexpected error occurred.');
    } else {
      onSuccess();
    }

    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <PaymentElement />
      <button
        type="submit"
        disabled={!stripe || isLoading}
        className="w-full rounded-full bg-blue-600 p-3 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Đang xử lý...' : 'Thanh toán ngay'}
      </button>
    </form>
  );
}
