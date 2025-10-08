import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Receipt {
  id: number
  filename: string
  upload_ts: string
  raw_text?: string
  vendor?: string
  date?: string
  total?: number
  currency?: string
  category?: string
  tax_deduction_possible?: string
  llm_summary?: string
  llm_details?: any
  processed: boolean
  processing_error?: string
  extra_meta?: any
  created_at: string
  updated_at: string
}

export interface ReceiptListResponse {
  items: Receipt[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SearchResult {
  receipt: Receipt
  similarity_score: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
}

export interface TemplateResponse {
  subject: string
  body: string
}

// API Methods
export const uploadReceipt = async (file: File): Promise<any> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const getReceipt = async (id: number): Promise<Receipt> => {
  const response = await api.get(`/process/${id}`)
  return response.data
}

export const getReceiptList = async (page: number = 1, pageSize: number = 20): Promise<ReceiptListResponse> => {
  const response = await api.get('/list', {
    params: { page, page_size: pageSize },
  })
  return response.data
}

export const searchReceipts = async (query: string): Promise<SearchResponse> => {
  const response = await api.get('/search', {
    params: { q: query },
  })
  return response.data
}

export const generateTemplate = async (id: number): Promise<TemplateResponse> => {
  const response = await api.post(`/generate-template/${id}`)
  return response.data
}

export const downloadReceipt = async (id: number): Promise<Blob> => {
  const response = await api.get(`/download/${id}`, {
    responseType: 'blob',
  })
  return response.data
}

export const deleteReceipt = async (id: number): Promise<void> => {
  await api.delete(`/receipt/${id}`)
}

export const healthCheck = async (): Promise<any> => {
  const response = await api.get('/health')
  return response.data
}

export default api
