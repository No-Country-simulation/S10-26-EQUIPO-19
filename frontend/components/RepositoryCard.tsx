import HealthBadge from "@/components/HealthBadge";
import { compactNumber, formatDate, fullNumber, relativeTime } from "@/lib/format";
import type { RepositoryListItem } from "@/types/api";

// Tarjeta del catálogo (5.5), según el prototipo: al hacer clic abre la ficha técnica (5.6).
export default function RepositoryCard({ repo, onOpen }: { repo: RepositoryListItem; onOpen: (id: number) => void }) {
  const description = repo.description_es || repo.description || "Sin descripción.";
  return (
    <button
      type="button"
      onClick={() => onOpen(repo.id)}
      aria-label={`Ver la ficha de ${repo.name}`}
      className="flex h-full flex-col gap-3 rounded-[var(--radius-card)] border border-border bg-card p-5 text-left shadow-sm transition-colors hover:border-primary hover:bg-surface-hover"
    >
      <span className="flex min-w-0 items-center gap-2 text-xs">
        <span title={repo.category.name} className="min-w-0 truncate rounded-md bg-brand-pink-soft px-2 py-0.5 font-medium text-[#0f172a]">
          {repo.category.name}
        </span>
        {repo.language && <span className="shrink-0 text-text-muted">{repo.language}</span>}
      </span>
      <span className="flex flex-col">
        {/* El nombre viene de GitHub tal cual; solo se muestra con la primera letra en mayúscula. */}
        <span className="truncate font-display text-lg font-semibold text-text first-letter:uppercase">{repo.name}</span>
        <span className="truncate text-xs text-text-muted">{repo.full_name}</span>
      </span>
      <span className="line-clamp-3 flex-1 text-sm text-text-muted">{description}</span>
      <span className="text-xs text-text-muted" title={formatDate(repo.last_commit_at)}>
        {repo.last_commit_at ? `Actualizado ${relativeTime(repo.last_commit_at)}` : "Sin fecha de actualización"}
      </span>
      <span className="flex flex-wrap items-center justify-between gap-2 text-xs text-text-muted">
        <span className="flex items-center gap-2">
          <span aria-label={`${fullNumber(repo.stars)} estrellas`}>★ {compactNumber(repo.stars)}</span>
          <span aria-label={`${fullNumber(repo.forks)} forks`}>{compactNumber(repo.forks)} forks</span>
          <span className="rounded-md bg-surface-hover px-2 py-0.5 font-medium text-text">{repo.license ?? "Sin licencia"}</span>
        </span>
        <HealthBadge status={repo.metrics.health_status} score={repo.metrics.health_score} />
      </span>
    </button>
  );
}
