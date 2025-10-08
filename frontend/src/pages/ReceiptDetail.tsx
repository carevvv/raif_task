import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getReceipt, generateTemplate, downloadReceipt, deleteReceipt, Receipt } from '../services/api'

export function ReceiptDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [receipt, setReceipt] = useState<Receipt | null>(null)
  const [loading, setLoading] = useState(true)
  const [template, setTemplate] = useState<{ subject: string; body: string } | null>(null)
  const [loadingTemplate, setLoadingTemplate] = useState(false)
  const [showRawText, setShowRawText] = useState(false)

  useEffect(() => {
    loadReceipt()
    const interval = setInterval(() => {
      if (receipt && !receipt.processed) {
        loadReceipt()
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [id])

  const loadReceipt = async () => {
    try {
      const data = await getReceipt(Number(id))
      setReceipt(data)
    } catch (error) {
      console.error('Failed to load receipt:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateTemplate = async () => {
    setLoadingTemplate(true)
    try {
      const data = await generateTemplate(Number(id))
      setTemplate(data)
    } catch (error) {
      console.error('Failed to generate template:', error)
      alert('Ошибка генерации шаблона')
    } finally {
      setLoadingTemplate(false)
    }
  }

  const handleDownload = async () => {
    try {
      const blob = await downloadReceipt(Number(id))
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = receipt?.filename || 'receipt'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to download:', error)
      alert('Ошибка загрузки файла')
    }
  }

  const handleDelete = async () => {
    if (!confirm('Вы уверены, что хотите удалить этот чек?')) return
    
    try {
      await deleteReceipt(Number(id))
      navigate('/list')
    } catch (error) {
      console.error('Failed to delete:', error)
      alert('Ошибка удаления')
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Скопировано в буфер обмена')
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!receipt) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-600">Чек не найден</p>
        <button
          onClick={() => navigate('/list')}
          className="mt-4 text-primary-600 hover:text-primary-700"
        >
          Вернуться к списку
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <button
          onClick={() => navigate('/list')}
          className="text-primary-600 hover:text-primary-700 mb-3 flex items-center"
        >
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Назад к списку
        </button>

        <h2 className="text-xl font-bold text-gray-900 mb-2">
          {receipt.vendor || 'Без названия'}
        </h2>

        {!receipt.processed && !receipt.processing_error && (
          <div className="flex items-center space-x-2 text-yellow-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
            <span className="text-sm">Обработка...</span>
          </div>
        )}

        {receipt.processing_error && (
          <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
            Ошибка обработки: {receipt.processing_error}
          </div>
        )}
      </div>

      {/* Main Info */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="font-semibold text-gray-800 mb-3">Основная информация</h3>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-gray-600">Продавец:</dt>
            <dd className="font-medium text-gray-900">{receipt.vendor || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-600">Дата:</dt>
            <dd className="font-medium text-gray-900">{receipt.date || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-600">Сумма:</dt>
            <dd className="font-medium text-gray-900">
              {receipt.total ? `${receipt.total} ${receipt.currency || 'RUB'}` : '—'}
            </dd>
          </div>
          <div>
            <dt className="text-gray-600">Категория:</dt>
            <dd className="font-medium text-gray-900">{receipt.category || '—'}</dd>
          </div>
        </dl>
      </div>

      {/* Classification */}
      {receipt.llm_summary && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="font-semibold text-gray-800 mb-2">Классификация</h3>
          <p className="text-sm text-gray-700 mb-3">{receipt.llm_summary}</p>
          {receipt.tax_deduction_possible && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Налоговый вычет:</span>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  receipt.tax_deduction_possible === 'yes'
                    ? 'bg-green-100 text-green-800'
                    : receipt.tax_deduction_possible === 'no'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {receipt.tax_deduction_possible === 'yes' && 'Возможен'}
                {receipt.tax_deduction_possible === 'no' && 'Невозможен'}
                {receipt.tax_deduction_possible === 'maybe' && 'Требует проверки'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Raw Text */}
      {receipt.raw_text && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <button
            onClick={() => setShowRawText(!showRawText)}
            className="w-full flex justify-between items-center font-semibold text-gray-800"
          >
            <span>Распознанный текст</span>
            <svg
              className={`w-5 h-5 transition-transform ${showRawText ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {showRawText && (
            <pre className="mt-3 text-xs bg-gray-50 p-3 rounded overflow-x-auto whitespace-pre-wrap">
              {receipt.raw_text}
            </pre>
          )}
        </div>
      )}

      {/* Template Generation */}
      {receipt.processed && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="font-semibold text-gray-800 mb-3">Шаблон письма</h3>
          {!template ? (
            <button
              onClick={handleGenerateTemplate}
              disabled={loadingTemplate}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 transition"
            >
              {loadingTemplate ? 'Генерация...' : 'Сгенерировать письмо'}
            </button>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Тема:</label>
                <div className="mt-1 flex items-center space-x-2">
                  <input
                    type="text"
                    value={template.subject}
                    readOnly
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                  <button
                    onClick={() => copyToClipboard(template.subject)}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Текст письма:</label>
                <div className="mt-1 flex flex-col space-y-2">
                  <textarea
                    value={template.body}
                    readOnly
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                  <button
                    onClick={() => copyToClipboard(template.body)}
                    className="self-end px-4 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700"
                  >
                    Скопировать текст
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="font-semibold text-gray-800 mb-3">Действия</h3>
        <div className="space-y-2">
          <button
            onClick={handleDownload}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Скачать оригинал
          </button>
          <button
            onClick={handleDelete}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Удалить чек
          </button>
        </div>
      </div>
    </div>
  )
}
