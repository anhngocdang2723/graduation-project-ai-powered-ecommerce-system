import FooterContent from 'components/layout/footer-content';
import { getMenu } from 'lib/medusa';

const { COMPANY_NAME, SITE_NAME } = process.env;

export default async function Footer() {
  const currentYear = new Date().getFullYear();
  const copyrightDate = 2023 + (currentYear > 2023 ? `-${currentYear}` : '');
  const menu = await getMenu('next-js-frontend-footer-menu');
  const copyrightName = COMPANY_NAME || SITE_NAME || '';

  return (
    <FooterContent
      menu={menu}
      copyrightDate={copyrightDate.toString()}
      copyrightName={copyrightName}
      siteName={SITE_NAME || ''}
    />
  );
}
