import Link from 'next/link';
import { CheckCircleIcon } from '@heroicons/react/24/solid';

export default function CheckoutSuccessPage({
  searchParams
}: {
  searchParams: { order?: string };
}) {
  const orderId = searchParams.order || 'unknown';

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 text-center">
      <div className="mb-8 flex justify-center">
        <CheckCircleIcon className="h-24 w-24 text-green-600" />
      </div>
      
      <h1 className="mb-4 text-3xl font-bold">Đặt hàng thành công!</h1>
      
      <p className="mb-2 text-lg text-neutral-600 dark:text-neutral-400">
        Cảm ơn bạn đã mua hàng!
      </p>
      
      <p className="mb-8 text-sm text-neutral-500 dark:text-neutral-500">
        Mã đơn hàng: <span className="font-mono font-semibold">#{orderId}</span>
      </p>
      
      <div className="mb-8 rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-black">
        <h2 className="mb-4 text-xl font-semibold">Tiếp theo là gì?</h2>
        <ul className="space-y-3 text-left text-sm text-neutral-600 dark:text-neutral-400">
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Bạn sẽ sớm nhận được email xác nhận</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Theo dõi trạng thái đơn hàng trong tài khoản của bạn</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Thời gian giao hàng dự kiến: 3-5 ngày làm việc</span>
          </li>
        </ul>
      </div>
      
      <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
        <Link
          href="/account/orders"
          className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
        >
          Xem chi tiết đơn hàng
        </Link>
        <Link
          href="/search"
          className="rounded-lg border border-neutral-300 px-6 py-3 font-semibold transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-900"
        >
          Tiếp tục mua sắm
        </Link>
      </div>
    </div>
  );
}
