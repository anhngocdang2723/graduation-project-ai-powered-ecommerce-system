import ChatWidget from 'components/chat/chat-widget';
import Navbar from 'components/layout/navbar';
import { LanguageProvider } from 'lib/i18n/context';
import { getCustomer } from 'lib/medusa';
import { Inter } from 'next/font/google';
import { cookies } from 'next/headers';
import { ReactNode, Suspense } from 'react';
import './globals.css';

const { TWITTER_CREATOR, TWITTER_SITE, SITE_NAME } = process.env;
const baseUrl = process.env.NEXT_PUBLIC_VERCEL_URL
  ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}`
  : 'http://localhost:3000';

export const metadata = {
  metadataBase: new URL(baseUrl),
  title: {
    default: SITE_NAME!,
    template: `%s | ${SITE_NAME}`
  },
  robots: {
    follow: true,
    index: true
  },
  ...(TWITTER_CREATOR &&
    TWITTER_SITE && {
      twitter: {
        card: 'summary_large_image',
        creator: TWITTER_CREATOR,
        site: TWITTER_SITE
      }
    })
};

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
});

export default async function RootLayout({ children }: { children: ReactNode }) {
  const token = cookies().get('_medusa_jwt')?.value;
  const cartId = cookies().get('cartId')?.value;
  let userType = 'guest';
  let customerId = undefined;
  
  if (token) {
    try {
      const customer = await getCustomer(token);
      if (customer) {
        userType = 'customer';
        customerId = customer.id;
      }
    } catch (e) {
      // Token might be invalid
    }
  }

  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-neutral-50 text-black selection:bg-teal-300 dark:bg-neutral-900 dark:text-white dark:selection:bg-pink-500 dark:selection:text-white">
        <LanguageProvider>
          <Navbar />
          <Suspense>
            <main>{children}</main>
          </Suspense>
          <ChatWidget userType={userType} customerId={customerId} cartId={cartId} />
        </LanguageProvider>
      </body>
    </html>
  );
}
