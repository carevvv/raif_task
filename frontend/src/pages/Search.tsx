import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchReceipts, SearchResult } from '../services/api'

export function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const navigate = useNavigate()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setSearched(true)
    try {
      const data = await searchReceipts(query)
      setResults(data.results)
    } catch (error) {
      console.error('Search failed:', error)
      alert('Ошибка поиска')
    } finally {
      setLoading(false)
    }
  }

  const formatAmount = (amount?: number, currency?: string) => {
    if (amount === undefined || amount === null) return '—'
    return `${amount.toFixed(2)} ${currency || 'RUB'}`
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-md p-4">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Семантический поиск
        </h2>

        <form onSubmit={handleSearch} className="space-y-3">
          <div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Например: медицинские расходы за март"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Поиск...' : 'Искать'}
          </button>
        </form>

        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            💡 Поиск по смыслу использует искусственный интеллект для поиска релевантных чеков, даже если точные слова не совпадают.
          </p>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
        </div>
      )}

      {!loading && searched && (
        <div className="space-y-3">
          {results.length === 0 ? (
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
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ничего не найдено
              </h3>
              <p className="text-gray-600">
                Попробуйте изменить запрос или загрузите больше чеков
              </p>
            </div>
          ) : (
            <>
              <div className="text-sm text-gray-600 px-1">
                Найдено результатов: {results.length}
              </div>
              {results.map((result) => (
                <div
                  key={result.receipt.id}
                  onClick={() => navigate(`/receipt/${result.receipt.id}`)}
                  className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900">
                          {result.receipt.vendor || 'Без названия'}
                        </h3>
                        <span className="text-xs text-gray-500">
                          • Релевантность: {(result.similarity_score * 100).toFixed(0)}%
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mb-2">
                        <div>
                          <span className="text-gray-500">Дата:</span>{' '}
                          {result.receipt.date || '—'}
                        </div>
                        <div>
                          <span className="text-gray-500">Сумма:</span>{' '}
                          {formatAmount(result.receipt.total, result.receipt.currency)}
                        </div>
                      </div>

                      {result.receipt.category && (
                        <div className="mb-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {result.receipt.category}
                          </span>
                        </div>
                      )}

                      {result.receipt.llm_summary && (
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {result.receipt.llm_summary}
                        </p>
                      )}
                    </div>

                    <svg
                      className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2"
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
            </>
          )}
        </div>
      )}
    </div>
  )
}
