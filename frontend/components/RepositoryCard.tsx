import HealthBadge from "@/components/HealthBadge";
import { compactNumber } from "@/lib/format";
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
      <span className="flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-md bg-brand-pink-soft px-2 py-0.5 font-medium text-[#0f172a]">{repo.category.name}</span>
        {repo.language && <span className="text-text-muted">{repo.language}</span>}
      </span>
      <span className="flex flex-col">
        <span className="truncate text-lg font-semibold text-text">{repo.name}</span>
        <span className="truncate text-xs text-text-muted">{repo.full_name}</span>
      </span>
      <span className="line-clamp-3 flex-1 text-sm text-text-muted">{description}</span>
      <span className="flex flex-wrap items-center justify-between gap-2 text-xs text-text-muted">
        <span className="flex items-center gap-2">
          <span aria-label={`${repo.stars} estrellas`}>★ {compactNumber(repo.stars)}</span>
          <span className="rounded-md bg-surface-hover px-2 py-0.5 font-medium text-text">{repo.license ?? "Sin licencia"}</span>
        </span>
        <HealthBadge status={repo.metrics.health_status} score={repo.metrics.health_score} />
      </span>
    </button>
  );
}
