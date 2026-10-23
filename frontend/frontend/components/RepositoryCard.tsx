import Link from 'next/link'
import type { RepositoryListItem } from '@/types/api'

function colorSalud(score: number) {
  if (score >= 80) return 'bg-emerald-500/20 text-emerald-300'
  if (score >= 60) return 'bg-yellow-500/20 text-yellow-300'
  return 'bg-red-500/20 text-red-300'
}

export default function RepositoryCard({ repo }: { repo: RepositoryListItem }) {
  return (
    <Link
      href={`/repositorio/${repo.id}`}
      className="block bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-emerald-400 transition"
    >
      <div className="flex justify-between gap-2">
        <h3 className="text-lg font-semibold truncate">{repo.name}</h3>
        <span className={`text-xs px-2 py-1 rounded-full shrink-0 ${colorSalud(repo.metrics.health_score)}`}>
          {repo.metrics.health_status} • {repo.metrics.health_score}
        </span>
      </div>
      <p className="text-slate-400 text-xs mt-1">{repo.full_name} • {repo.category.name}</p>
      <p className="text-slate-300 text-sm mt-2 line-clamp-2">
        {repo.description_es || repo.description}
      </p>
      <div className="flex items-center gap-3 text-xs text-slate-400 mt-3">
        <span>★ {repo.stars.toLocaleString()}</span>
        <span>⑂ {repo.forks.toLocaleString()}</span>
        <span>{repo.language ?? 'Sin lenguaje'}</span>
        <span>{repo.license ?? 'Sin licencia'}</span>
      </div>
      <div className="flex flex-wrap gap-1 mt-3">
        {repo.topics.slice(0, 4).map(t => (
          <span key={t} className="text-[11px] bg-slate-800 px-2 py-1 rounded-full">#{t}</span>
        ))}
      </div>
      <p className="text-emerald-400 text-sm mt-4 font-medium">Ver ficha técnica →</p>
    </Link>
  )
}
