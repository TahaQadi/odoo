import { useTranslations } from 'next-intl'
import Link from 'next/link'

export default function HomePage() {
  const t = useTranslations('auth')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            {t('welcome')}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Advanced Manufacturing Execution System for Chemical Detergents Production
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/en/login"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200"
            >
              English Login
            </Link>
            <Link
              href="/ar/login"
              className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200"
            >
              تسجيل الدخول بالعربية
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
