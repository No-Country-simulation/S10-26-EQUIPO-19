'use client'
import { useEffect, useState } from 'react'
import { getCategories, searchRepositories } from '@/lib/api'
import type { Category, RepositoryListItem } from '@/types/api'
import SearchBar from '@/components/SearchBar'
import RepositoryCard from '@/components/RepositoryCard'

export default function Home() {
  const [categorias, setCategorias] = useState<Category[]>([])
  const [repos, setRepos] = useState<RepositoryListItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const [q, setQ] = useState('')
  const [categoryId, setCategoryId] = useState<number | ''>('')
  const [language, setLanguage] = useState('')
  const [minStars, setMinStars] = useState(0)

  useEffect(() => {
    getCategories().then(setCategorias).catch(() => {})
  }, [])

  useEffect(() => {
    const t = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await searchRepositories({
          q: q || undefined,
          category_id: categoryId === '' ? undefined : categoryId,
          language: language || undefined,
          min_stars: minStars || undefined,
          page: 1,
          page_size: 12,
        })
        setRepos(data.items)
        setTotal(data.total)
      } catch {
        setRepos([])
      } finally {
        setLoading(false)
      }
    }, 400)
    return () => clearTimeout(t)
  }, [q, categoryId, language, minStars])

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="max-w-7xl mx-auto px-4 pt-10">
        <h1 className="text-4xl md:text-5xl font-bold">OpenBridge</h1>
        <p className="text-slate-400 mt-2 max-w-2xl">
          Catálogo curado open-source. Encontrá la herramienta ideal sin investigar 20 horas ni elegir una librería abandonada.
        </p>
        <SearchBar value={q} onChange={setQ} />
        <div className="flex flex-wrap gap-3 mt-4">
          <select value={categoryId} onChange={e => setCategoryId(e.target.value === '' ? '' : Number(e.target.value))} className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm">
            <option value="">Todas las categorías</option>
            {categorias.map(c => (
              <option key={c.id} value={c.id}>{c.name} ({c.repositories_count})</option>
            ))}
          </select>
          <select value={language} onChange={e => setLanguage(e.target.value)} className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm">
            <option value="">Todos los lenguajes</option>
            <option>Python</option>
            <option>TypeScript</option>
            <option>Rust</option>
            <option>Go</option>
            <option>JavaScript</option>
          </select>
          <select value={minStars} onChange={e => setMinStars(Number(e.target.value))} className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm">
            <option value={0}>Sin mínimo de stars</option>
            <option value={1000}>+1.000 ★</option>
            <option value={5000}>+5.000 ★</option>
            <option value={10000}>+10.000 ★</option>
          </select>
        </div>
      </header>
      <section className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <p className="text-slate-400">Cargando repositorios...</p>
        ) : repos.length === 0 ? (
          <p className="text-slate-400">Sin resultados para esos filtros.</p>
        ) : (
          <>
            <p className="text-slate-400 text-sm mb-4">{total} repositorios encontrados</p>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {repos.map(r => <RepositoryCard key={r.id} repo={r} />)}
            </div>
          </>
        )}
      </section>
    </main>
  )
}
