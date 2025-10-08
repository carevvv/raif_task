import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getReceiptList, Receipt } from '../services/api'

export function ReceiptList() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const navigate = useNavigate()

  useEffect(() => {
    loadReceipts()
  }, [page])

  const loadReceipts = async () => {
    setLoading(true)
    try {
      const data = await getReceiptList(page, 20)
      setReceipts(data.items)
      setTotalPages(data.total_pages)
    } catch (error) {
      console.error('Failed to load receipts:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatAmount = (amount?: number, currency?: string) => {
    if (amount === undefined || amount === null) return '—'
    return `${amount.toFixed(2)} ${currency || 'RUB'}`
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">Мои чеки</h2>
        <span className="text-sm text-gray-600">Страница {page} из {totalPages}</span>
      </div>

      {receipts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Нет загруженных чеков
          </h3>
          <p className="text-gray-600 mb-4">
            Загрузите свой первый чек для начала работы
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition"
          >
            Загрузить чек
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {receipts.map((receipt) => (
              <div
                key={receipt.id}
                onClick={() => navigate(`/receipt/${receipt.id}`)}
                className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {receipt.vendor || 'Без названия'}
                      </h3>
                      {!receipt.processed && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          Обработка...
                        </span>
                      )}
                      {receipt.processing_error && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                          Ошибка
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                      <div>
                        <span className="text-gray-500">Дата:</span>{' '}
                        {receipt.date || formatDate(receipt.upload_ts)}
                      </div>
                      <div>
                        <span className="text-gray-500">Сумма:</span>{' '}
                        {formatAmount(receipt.total, receipt.currency)}
                      </div>
                    </div>

                    {receipt.category && (
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {receipt.category}
                        </span>
                      </div>
                    )}
                  </div>

                  <svg
                    className="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center space-x-2 pt-4">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Назад
              </button>
              <span className="px-4 py-2 text-gray-700">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Вперёд
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
