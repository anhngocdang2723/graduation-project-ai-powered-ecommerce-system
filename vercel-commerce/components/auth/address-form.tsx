'use client';

import { addAddressAction } from 'components/auth/actions';
import { useFormState } from 'react-dom';

export default function AddressForm() {
  const [state, formAction] = useFormState(addAddressAction, null);

  return (
    <form action={formAction} className="space-y-4 mt-4">
      <div className="grid grid-cols-2 gap-4">
        <input name="first_name" placeholder="First Name" required className="border p-2 rounded dark:bg-black dark:border-neutral-700" />
        <input name="last_name" placeholder="Last Name" required className="border p-2 rounded dark:bg-black dark:border-neutral-700" />
      </div>
      <input name="address_1" placeholder="Address" required className="w-full border p-2 rounded dark:bg-black dark:border-neutral-700" />
      <div className="grid grid-cols-2 gap-4">
        <input name="city" placeholder="City" required className="border p-2 rounded dark:bg-black dark:border-neutral-700" />
        <input name="postal_code" placeholder="Postal Code" required className="border p-2 rounded dark:bg-black dark:border-neutral-700" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <select name="country_code" className="border p-2 rounded dark:bg-black dark:border-neutral-700">
          <option value="vn">Vietnam</option>
          <option value="us">United States</option>
          <option value="gb">United Kingdom</option>
        </select>
        <input name="phone" placeholder="Phone" className="border p-2 rounded dark:bg-black dark:border-neutral-700" />
      </div>
      <button type="submit" className="bg-black text-white px-4 py-2 rounded dark:bg-white dark:text-black">
        Add Address
      </button>
      {state?.error && <p className="text-red-500">{state.error}</p>}
      {state?.success && <p className="text-green-500">Address added successfully!</p>}
    </form>
  );
}
