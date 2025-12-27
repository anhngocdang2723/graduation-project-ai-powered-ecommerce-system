'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Price from 'components/price';
import { Elements } from '@stripe/react-stripe-js';
import { getStripe } from 'lib/stripe';
import { StripePaymentForm } from './stripe-payment-form';
import { Cart } from 'lib/medusa/types';

interface CheckoutFormData {
  email: string;
  firstName: string;
  lastName: string;
  address: string;
  city: string;
  postalCode: string;
  country: string;
  phone: string;
  paymentMethod: 'card' | 'paypal' | 'cod';
}

export function CheckoutForm({ cart, cartId }: { cart?: Cart | null, cartId?: string }) {
  const router = useRouter();
  const cartItems = cart?.lines || [];
  const [formData, setFormData] = useState<CheckoutFormData>({
    email: '',
    firstName: '',
    lastName: '',
    address: '',
    city: '',
    postalCode: '',
    country: 'US',
    phone: '',
    paymentMethod: 'card'
  });
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<1 | 2 | 3>(1); // 1: Info, 2: Shipping, 3: Payment
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Use cart totals if available
  const subtotal = cart?.cost?.subtotalAmount?.amount ? parseFloat(cart.cost.subtotalAmount.amount) : 0;
  const tax = cart?.cost?.totalTaxAmount?.amount ? parseFloat(cart.cost.totalTaxAmount.amount) : 0;
  const total = cart?.cost?.totalAmount?.amount ? parseFloat(cart.cost.totalAmount.amount) : 0;
  const currencyCode = cart?.cost?.totalAmount?.currencyCode || 'USD';

  // If Medusa handles shipping, it should be in the cart total.
  // But if we haven't selected a shipping method in Medusa, it might be 0.
  // For this demo, we'll assume the total from Medusa includes everything if it's set.
  // Otherwise we fallback to manual calculation (which is likely wrong but keeps the UI working).
  
  const shipping = total > subtotal + tax ? total - subtotal - tax : 0;
  const grandTotal = total;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const fetchClientSecret = async () => {
    if (!cartId) {
      console.error("No cart ID available");
      setError("No cart found. Please try refreshing the page.");
      return;
    }

    setError(null);
    try {
      const res = await fetch('/api/create-payment-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cartId })
      });
      
      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      if (data.cart && data.cart.payment_collection && data.cart.payment_collection.payment_sessions) {
        const stripeSession = data.cart.payment_collection.payment_sessions.find(
          (s: any) => s.provider_id === 'pp_stripe_stripe'
        );
        
        if (stripeSession && stripeSession.data.client_secret) {
          setClientSecret(stripeSession.data.client_secret);
        } else {
          console.error("Stripe session not found in cart", data.cart);
          setError("Stripe payment session could not be created.");
        }
      } else {
        console.error("Failed to create payment session", data);
        setError("Failed to retrieve payment details.");
      }
    } catch (error: any) {
      console.error("Error fetching client secret:", error);
      setError(error.message || "An error occurred while initializing payment.");
    }
  };

  useEffect(() => {
    if (step === 3 && formData.paymentMethod === 'card') {
      fetchClientSecret();
    }
  }, [step, formData.paymentMethod]);

  const handlePaymentSuccess = () => {
    // Clear cart
    localStorage.removeItem('cart');
    // Redirect to success page
    router.push(`/checkout/success?order=new_order_${Date.now()}`);
  };

  const handlePaymentError = (error: string) => {
    alert(`Payment failed: ${error}`);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.paymentMethod === 'card') {
      // Handled by StripePaymentForm
      return;
    }
    
    setLoading(true);

    try {
      if (formData.paymentMethod === 'cod') {
        const response = await fetch('/api/complete-cart', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cartId })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          // Clear cart
          // localStorage.removeItem('cart'); // Managed by cookies/server usually
          // Redirect to success page
          router.push(`/checkout/success?order=${data.orderId}`);
        } else {
          alert(data.error || 'Đặt hàng thất bại. Vui lòng thử lại.');
        }
      } else {
        alert('Phương thức thanh toán này chưa được hỗ trợ.');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Đã xảy ra lỗi. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-8 lg:grid-cols-3">
      {/* Checkout Form */}
      <div className="lg:col-span-2">
        <div className="space-y-6">
          {/* Step Indicator */}
          <div className="flex items-center justify-between">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`flex items-center ${s < 3 ? 'flex-1' : ''}`}
              >
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full ${
                    s <= step
                      ? 'bg-blue-600 text-white'
                      : 'bg-neutral-200 text-neutral-600 dark:bg-neutral-800'
                  }`}
                >
                  {s}
                </div>
                {s < 3 && (
                  <div
                    className={`h-1 flex-1 ${
                      s < step ? 'bg-blue-600' : 'bg-neutral-200 dark:bg-neutral-800'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Step 1: Contact Information */}
          {step === 1 && (
            <div className="rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-black">
              <h2 className="mb-4 text-xl font-semibold">Thông tin liên hệ</h2>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium">Email</label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium">Tên</label>
                    <input
                      type="text"
                      name="firstName"
                      required
                      value={formData.firstName}
                      onChange={handleInputChange}
                      className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Họ</label>
                    <input
                      type="text"
                      name="lastName"
                      required
                      value={formData.lastName}
                      onChange={handleInputChange}
                      className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium">Số điện thoại</label>
                  <input
                    type="tel"
                    name="phone"
                    required
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                  />
                </div>
              </div>
              <button
                type="button"
                onClick={() => setStep(2)}
                className="mt-6 w-full rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
              >
                Tiếp tục đến vận chuyển
              </button>
            </div>
          )}

          {/* Step 2: Shipping Address */}
          {step === 2 && (
            <div className="rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-black">
              <h2 className="mb-4 text-xl font-semibold">Địa chỉ giao hàng</h2>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium">Địa chỉ</label>
                  <input
                    type="text"
                    name="address"
                    required
                    value={formData.address}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium">Thành phố</label>
                    <input
                      type="text"
                      name="city"
                      required
                      value={formData.city}
                      onChange={handleInputChange}
                      className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium">Mã bưu chính</label>
                    <input
                      type="text"
                      name="postalCode"
                      required
                      value={formData.postalCode}
                      onChange={handleInputChange}
                      className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium">Quốc gia</label>
                  <select
                    name="country"
                    required
                    value={formData.country}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-neutral-300 px-4 py-2 dark:border-neutral-700 dark:bg-neutral-900"
                  >
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="UK">United Kingdom</option>
                    <option value="VN">Vietnam</option>
                  </select>
                </div>
              </div>
              <div className="mt-6 flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 rounded-lg border border-neutral-300 px-6 py-3 font-semibold transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
                >
                  Quay lại
                </button>
                <button
                  type="button"
                  onClick={() => setStep(3)}
                  className="flex-1 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
                >
                  Tiếp tục thanh toán
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Payment */}
          {step === 3 && (
            <div className="rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-black">
              <h2 className="mb-4 text-xl font-semibold">Phương thức thanh toán</h2>
              <div className="space-y-4">
                <div className="space-y-2">
                  {[
                    { value: 'card', label: 'Thẻ tín dụng/Ghi nợ' },
                    { value: 'paypal', label: 'PayPal' },
                    { value: 'cod', label: 'Thanh toán khi nhận hàng (COD)' }
                  ].map((method) => (
                    <label
                      key={method.value}
                      className="flex items-center rounded-lg border border-neutral-300 p-4 cursor-pointer hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-900"
                    >
                      <input
                        type="radio"
                        name="paymentMethod"
                        value={method.value}
                        checked={formData.paymentMethod === method.value}
                        onChange={handleInputChange}
                        className="mr-3"
                      />
                      <span className="font-medium">{method.label}</span>
                    </label>
                  ))}
                </div>

                {formData.paymentMethod === 'card' && (
                  <div className="mt-4 rounded-lg bg-neutral-50 p-4 dark:bg-neutral-900">
                    {error ? (
                      <div className="text-red-500 p-4 border border-red-200 rounded bg-red-50">
                        <p className="font-bold">Lỗi:</p>
                        <p>{error}</p>
                        <button 
                          onClick={() => fetchClientSecret()}
                          className="mt-2 text-sm text-blue-600 hover:underline"
                        >
                          Thử lại
                        </button>
                      </div>
                    ) : clientSecret ? (
                      <Elements stripe={getStripe()} options={{ clientSecret }}>
                        <StripePaymentForm 
                          onSuccess={handlePaymentSuccess}
                          onError={handlePaymentError}
                        />
                      </Elements>
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-sm text-neutral-500">Đang khởi tạo thanh toán...</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              {formData.paymentMethod !== 'card' && (
                <div className="mt-6 flex gap-4">
                  <button
                    type="button"
                    onClick={() => setStep(2)}
                    className="flex-1 rounded-lg border border-neutral-300 px-6 py-3 font-semibold transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
                  >
                    Quay lại
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="flex-1 rounded-lg bg-green-600 px-6 py-3 font-semibold text-white transition hover:bg-green-700 disabled:opacity-50"
                  >
                    {loading ? 'Đang xử lý...' : `Đặt hàng - ${currencyCode} ${grandTotal.toFixed(2)}`}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Order Summary */}
      <div className="lg:col-span-1">
        <div className="sticky top-4 rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-black">
          <h2 className="mb-4 text-xl font-semibold">Tóm tắt đơn hàng</h2>
          <div className="space-y-4">
            {cartItems.map((item) => (
              <div key={item.id} className="flex gap-4">
                <div className="relative h-16 w-16 overflow-hidden rounded-lg bg-neutral-100 dark:bg-neutral-900">
                  {item.featuredImage?.url && (
                    <img 
                      src={item.featuredImage.url} 
                      alt={item.featuredImage.altText || item.title}
                      className="h-full w-full object-cover"
                    />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium">{item.title}</h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    SL: {item.quantity}
                  </p>
                </div>
                <div className="font-semibold">
                  <Price
                    amount={item.cost?.totalAmount?.amount || '0'}
                    currencyCode={item.cost?.totalAmount?.currencyCode || 'USD'}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 space-y-2 border-t border-neutral-200 pt-4 dark:border-neutral-800">
            <div className="flex justify-between text-sm">
              <span>Tạm tính</span>
              <Price amount={subtotal.toString()} currencyCode={currencyCode} />
            </div>
            <div className="flex justify-between text-sm">
              <span>Phí vận chuyển</span>
              {shipping === 0 ? <span>MIỄN PHÍ</span> : <Price amount={shipping.toString()} currencyCode={currencyCode} />}
            </div>
            <div className="flex justify-between text-sm">
              <span>Thuế</span>
              <Price amount={tax.toString()} currencyCode={currencyCode} />
            </div>
            <div className="flex justify-between border-t border-neutral-200 pt-2 text-lg font-bold dark:border-neutral-800">
              <span>Tổng cộng</span>
              <Price amount={grandTotal.toString()} currencyCode={currencyCode} />
            </div>
          </div>
          {grandTotal > 50 && currencyCode === 'USD' && (
            <p className="mt-4 text-sm text-green-600 dark:text-green-400">
              ✓ Bạn đủ điều kiện được MIỄN PHÍ vận chuyển!
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
