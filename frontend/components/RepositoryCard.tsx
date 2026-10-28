import HealthBadge from "@/components/HealthBadge";
import type { RepositoryListItem } from "@/types/api";

function formatDate(iso: string | null) {
  if (!iso) return "Sin datos";
  return new Date(iso).toLocaleDateString("es-CL", { day: "2-digit", month: "2-digit", year: "numeric" });
}

export default function RepositoryCard({ repo }: { repo: RepositoryListItem }) {
  const description = repo.description_es || repo.description || "Sin descripción.";
  return (
    <article className="flex h-full flex-col gap-3 rounded-[var(--radius-card)] border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-lg font-semibold text-text">{repo.name}</h3>
          <p className="truncate text-xs text-text-muted">{repo.full_name}</p>
        </div>
        <HealthBadge status={repo.metrics.health_status} score={repo.metrics.health_score} />
      </div>
      <p className="line-clamp-3 text-sm text-text-muted">{description}</p>
      <dl className="mt-auto grid grid-cols-2 gap-x-3 gap-y-1 text-xs text-text-muted">
        <div><dt className="inline font-semibold text-text">Lenguaje: </dt><dd className="inline">{repo.language ?? "Sin datos"}</dd></div>
        <div><dt className="inline font-semibold text-text">Licencia: </dt><dd className="inline">{repo.license ?? "Sin datos"}</dd></div>
        <div><dt className="inline font-semibold text-text">Estrellas: </dt><dd className="inline">{repo.stars.toLocaleString("es-CL")}</dd></div>
        <div><dt className="inline font-semibold text-text">Actualizado: </dt><dd className="inline">{formatDate(repo.last_commit_at)}</dd></div>
      </dl>
      <div className="flex items-center justify-between gap-2 border-t border-border pt-3">
        <span className="rounded-[var(--radius-pill)] bg-brand-indigo-soft px-3 py-1 text-xs font-medium text-brand-indigo-strong dark:bg-surface-hover dark:text-primary">
          {repo.category.name}
        </span>
        <a href={repo.url} target="_blank" rel="noreferrer" className="text-sm font-semibold text-primary hover:underline">
          Ver en GitHub
        </a>
      </div>
    </article>
  );
}
