import type { Category, PaginatedRepositories, RepositoryDetail } from '@/types/api'
import { MOCK_CATEGORIES, filterMock } from '@/data/mock'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
// Cambiar a false cuando el backend esté listo y corriendo
const USE_MOCK = true

export async function getCategories(): Promise<Category[]> {
  if (USE_MOCK) return MOCK_CATEGORIES
  const res = await fetch(`${BASE}/categories`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Error categorías')
  return res.json()
}

export async function searchRepositories(params: {
  q?: string
  category_id?: number
  language?: string
  min_stars?: number
  page?: number
  page_size?: number
}): Promise<PaginatedRepositories> {
  if (USE_MOCK) return filterMock(params)
  const qs = new URLSearchParams()
  if (params.q) qs.set('q', params.q)
  if (params.category_id) qs.set('category_id', String(params.category_id))
  if (params.language) qs.set('language', params.language)
  if (params.min_stars) qs.set('min_stars', String(params.min_stars))
  qs.set('page', String(params.page ?? 1))
  qs.set('page_size', String(params.page_size ?? 12))
  const res = await fetch(`${BASE}/repositories/search?${qs.toString()}`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Error búsqueda')
  return res.json()
}

export async function getRepository(id: number): Promise<RepositoryDetail | null> {
  if (USE_MOCK) return null
  const res = await fetch(`${BASE}/repositories/${id}`, { cache: 'no-store' })
  if (res.status === 404) return null
  if (!res.ok) throw new Error('Error detalle')
  return res.json()
}
