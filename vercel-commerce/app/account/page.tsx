import AccountView from 'components/account/account-view';
import { getCustomer } from 'lib/medusa';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function AccountPage() {
  const token = cookies().get('_medusa_jwt')?.value;

  if (!token) {
    redirect('/login');
  }

  const customer = await getCustomer(token);

  if (!customer) {
    // Token invalid or expired
    redirect('/login');
  }

  return <AccountView customer={customer} />;
}
