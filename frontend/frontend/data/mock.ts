import type { Category, PaginatedRepositories, RepositoryListItem } from '@/types/api'

export const MOCK_CATEGORIES: Category[] = [
  { id: 1, name: 'Bases de Datos Vectoriales', repositories_count: 5 },
  { id: 2, name: 'Frameworks de IA & LLMs', repositories_count: 8 },
  { id: 3, name: 'Herramientas de Observabilidad', repositories_count: 4 },
]

export const MOCK_REPOS: RepositoryListItem[] = [
  {
    id: 101, github_id: 10567832, name: 'qdrant', full_name: 'qdrant/qdrant',
    url: 'https://github.com/qdrant/qdrant',
    description: 'Vector Similarity Search Engine and Vector Database',
    description_es: 'Motor de búsqueda por similitud vectorial y base de datos vectorial para IA de alto rendimiento.',
    language: 'Rust', license: 'Apache-2.0', stars: 19500, forks: 1400,
    topics: ['vector-search', 'database', 'rust', 'machine-learning'],
    pushed_at: '2026-10-21T18:30:00Z',
    category: { id: 1, name: 'Bases de Datos Vectoriales' },
    metrics: { health_score: 95, health_status: 'Activo' }
  },
  {
    id: 102, github_id: 23489110, name: 'chroma', full_name: 'chroma-core/chroma',
    url: 'https://github.com/chroma-core/chroma',
    description: 'the AI-native open-source embedding database',
    description_es: 'Base de datos de embeddings nativa para IA, ligera y de fácil integración.',
    language: 'Python', license: 'Apache-2.0', stars: 14200, forks: 1150,
    topics: ['embedding', 'database', 'python', 'ai'],
    pushed_at: '2026-10-20T14:15:00Z',
    category: { id: 1, name: 'Bases de Datos Vectoriales' },
    metrics: { health_score: 92, health_status: 'Activo' }
  },
  {
    id: 103, github_id: 999, name: 'supabase', full_name: 'supabase/supabase',
    url: 'https://github.com/supabase/supabase',
    description: 'The open source Firebase alternative',
    description_es: 'Alternativa open-source a Firebase: Postgres, Auth, Storage y Realtime.',
    language: 'TypeScript', license: 'Apache-2.0', stars: 68000, forks: 7200,
    topics: ['postgres', 'auth', 'realtime', 'database'],
    pushed_at: '2026-10-22T10:00:00Z',
    category: { id: 2, name: 'Frameworks de IA & LLMs' },
    metrics: { health_score: 98, health_status: 'Activo' }
  }
]

export function filterMock(params: { q?: string, category_id?: number, language?: string, min_stars?: number }): PaginatedRepositories {
  const filtered = MOCK_REPOS.filter(r => {
    if (params.q && !(r.name + r.description_es + r.topics.join(' ')).toLowerCase().includes(params.q.toLowerCase())) return false
    if (params.category_id && r.category.id !== params.category_id) return false
    if (params.language && r.language !== params.language) return false
    if (params.min_stars && r.stars < params.min_stars) return false
    return true
  })
  return { total: filtered.length, page: 1, page_size: 12, total_pages: 1, items: filtered }
}
