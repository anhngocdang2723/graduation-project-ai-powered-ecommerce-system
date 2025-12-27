# Stripe Payment Integration Guide

This guide documents the Stripe payment integration for the Medusa store.

## 1. Backend Setup (my-medusa-store)

### Installed Packages
- `@medusajs/payment-stripe`

### Configuration
Updated `medusa-config.ts` to include the Stripe module:

```typescript
modules: [
  {
    resolve: "@medusajs/medusa/payment",
    options: {
      providers: [
        {
          resolve: "@medusajs/payment-stripe",
          id: "stripe",
          options: {
            apiKey: process.env.STRIPE_API_KEY,
          },
        },
      ],
    },
  },
]
```

### Environment Variables
Ensure `.env` contains:
```
STRIPE_API_KEY=sk_test_...
```

## 2. Frontend Setup (vercel-commerce)

### Installed Packages
- `@stripe/stripe-js`
- `@stripe/react-stripe-js`

### Components
- `lib/stripe.ts`: Stripe loader singleton.
- `components/checkout/stripe-payment-form.tsx`: The payment form component using Stripe Elements.
- `components/checkout/checkout-form.tsx`: Updated to include the payment step.

### Environment Variables
Ensure `.env.local` contains:
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 3. Completion Steps (Required)

To make the payment functional, you must:

1.  **Get Stripe Keys**: Sign up for Stripe and get your Test API Keys (Publishable and Secret).
2.  **Update Env Files**: Replace `pk_test_placeholder` and `sk_test_placeholder` in the `.env` files.
3.  **Backend Logic**:
    The current frontend implementation in `checkout-form.tsx` has a mocked `fetchClientSecret` function.
    You need to implement the API call to your backend to create a Payment Session with Medusa.
    
    Example flow:
    - Frontend calls `POST /api/create-payment-session`
    - Backend calls Medusa `cart.createPaymentSession`
    - Backend returns `client_secret`
    - Frontend passes `client_secret` to `<Elements>` provider.

## 4. Testing

1.  Start Medusa Backend: `npm start` in `my-medusa-store`.
2.  Start Frontend: `npm run dev` in `vercel-commerce`.
3.  Add items to cart and proceed to checkout.
4.  Select "Credit/Debit Card".
5.  Use Stripe Test Cards (e.g., 4242 4242 4242 4242) to test success/failure.
