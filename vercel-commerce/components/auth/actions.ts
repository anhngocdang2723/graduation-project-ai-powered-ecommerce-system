'use server';

import { addAddress, createCustomer, medusaLogin, medusaRegister } from 'lib/medusa';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export async function registerAction(prevState: any, formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;
  const firstName = formData.get('firstName') as string;
  const lastName = formData.get('lastName') as string;

  try {
    // 1. Register (Auth Identity)
    const regRes = await medusaRegister({ email, password });
    const tempToken = regRes.token;

    // 2. Create Customer
    await createCustomer(tempToken, {
      email,
      first_name: firstName,
      last_name: lastName
    });

    // 3. Login to get final token (with actor_id)
    const loginRes = await medusaLogin({ email, password });
    const finalToken = loginRes.token;

    // 4. Set Cookie
    cookies().set('_medusa_jwt', finalToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 7 // 1 week
    });
  } catch (e: any) {
    return { error: e.message };
  }

  redirect('/account');
}

export async function loginAction(prevState: any, formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  try {
    const res = await medusaLogin({ email, password });
    const token = res.token;

    cookies().set('_medusa_jwt', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 7 // 1 week
    });
  } catch (e: any) {
    return { error: e.message };
  }
  
  redirect('/account');
}

export async function logoutAction() {
  cookies().delete('_medusa_jwt');
  redirect('/');
}

export async function addAddressAction(prevState: any, formData: FormData) {
  const token = cookies().get('_medusa_jwt')?.value;
  if (!token) return { error: 'Not authenticated' };

  const address = {
    first_name: formData.get('first_name'),
    last_name: formData.get('last_name'),
    address_1: formData.get('address_1'),
    city: formData.get('city'),
    country_code: formData.get('country_code'),
    postal_code: formData.get('postal_code'),
    phone: formData.get('phone')
  };

  try {
    await addAddress(token, address);
    return { success: true };
  } catch (e: any) {
    return { error: e.message };
  }
}
