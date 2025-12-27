import { OrderHistory } from 'components/account/order-history';
import { getServerTranslation } from 'lib/i18n/server';

export async function generateMetadata() {
  const { t } = await getServerTranslation();
  return {
    title: t('orderHistory.title'),
    description: t('orderHistory.noOrders')
  };
}

export default async function OrderHistoryPage() {
  const { t } = await getServerTranslation();
  
  return (
    <div className="mx-auto max-w-screen-lg px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">{t('orderHistory.title')}</h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          {t('orderHistory.viewTrackOrders')}
        </p>
      </div>

      <OrderHistory />
    </div>
  );
}
