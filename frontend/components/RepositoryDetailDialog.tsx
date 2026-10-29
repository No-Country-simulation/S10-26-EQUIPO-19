"use client";

import { useEffect, useRef, useState } from "react";
import HealthBadge from "@/components/HealthBadge";
import { ApiError, getRepository } from "@/lib/api";
import { compactNumber, formatDate, fullNumber, relativeTime } from "@/lib/format";
import type { HealthScoreDetails, Integration, RepositoryDetail } from "@/types/api";

type Status = { kind: "idle" } | { kind: "loading" } | { kind: "ok"; repo: RepositoryDetail } | { kind: "error"; message: string };

// Puntaje máximo de cada componente del health score (documento Health Score de repositorios).
const SCORE_PARTS: { key: keyof HealthScoreDetails; label: string; max: number }[] = [
  { key: "maintenance", label: "Mantenimiento", max: 30 },
  { key: "commit_activity", label: "Actividad de commits", max: 25 },
  { key: "popularity", label: "Popularidad", max: 15 },
  { key: "forks", label: "Forks", max: 10 },
];

function errorMessage(err: unknown) {
  if (err instanceof ApiError && err.status === 404) return "La ficha de este repositorio todavía no está disponible en la API.";
  if (err instanceof ApiError && err.status === 0) return "No pudimos conectar con la API. Revisa que el backend esté corriendo.";
  return "Ocurrió un error al cargar la ficha. Intenta de nuevo en unos minutos.";
}

// Ficha técnica (5.6) en una ventana emergente, como en el prototipo. Usa <dialog>: cierra con Esc,
// mantiene el foco dentro y lo devuelve a la tarjeta al cerrar.
export default function RepositoryDetailDialog({
  repoId,
  onClose,
  onSelect,
}: {
  repoId: number | null;
  onClose: () => void;
  onSelect: (id: number) => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (repoId !== null && !dialog.open) dialog.showModal();
    if (repoId === null && dialog.open) dialog.close();
  }, [repoId]);

  useEffect(() => {
    if (repoId === null) return;
    let cancelled = false;
    setStatus({ kind: "loading" });
    ref.current?.scrollTo({ top: 0 });
    getRepository(repoId)
      .then((repo) => !cancelled && setStatus({ kind: "ok", repo }))
      .catch((err) => !cancelled && setStatus({ kind: "error", message: errorMessage(err) }));
    return () => {
      cancelled = true;
    };
  }, [repoId]);

  const repo = status.kind === "ok" ? status.repo : null;

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={(e) => e.target === ref.current && ref.current?.close()}
      aria-labelledby="ficha-titulo"
      className="m-auto max-h-[90vh] w-[calc(100%-24px)] max-w-2xl rounded-2xl border border-border bg-card p-0 text-text shadow-xl backdrop:bg-[#0f172a]/55"
    >
      <div className="flex flex-col gap-5 p-5 sm:p-6">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 flex-col gap-2">
            {repo && (
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded-md bg-brand-pink-soft px-2 py-0.5 font-medium text-[#0f172a]">{repo.category.name}</span>
                <HealthBadge status={repo.metrics.health_status} score={repo.metrics.health_score} />
                {repo.archived && <span className="rounded-md bg-status-abandoned-bg px-2 py-0.5 font-semibold text-status-abandoned">Archivado</span>}
              </div>
            )}
            <h2 id="ficha-titulo" className="break-words text-2xl font-semibold">
              {repo ? repo.name : status.kind === "error" ? "Ficha no disponible" : "Cargando ficha…"}
            </h2>
            {repo && <p className="text-sm text-text-muted">{repo.full_name}</p>}
          </div>
          <button
            type="button"
            onClick={() => ref.current?.close()}
            aria-label="Cerrar la ficha"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-surface-hover text-lg"
          >
            ✕
          </button>
        </div>

        {status.kind === "loading" && <div className="h-64 animate-pulse rounded-xl bg-surface-muted" aria-hidden />}
        {status.kind === "error" && <p role="alert" className="text-text-muted">{status.message}</p>}
        {repo && <DetailBody repo={repo} onSelect={onSelect} />}
      </div>
    </dialog>
  );
}

function DetailBody({ repo, onSelect }: { repo: RepositoryDetail; onSelect: (id: number) => void }) {
  const description = repo.description_es || repo.description || "Sin descripción.";
  const details = repo.metrics.health_score_details;
  const noActivity = repo.metrics.commit_activity_status === "unavailable";

  return (
    <>
      <p className="text-text-muted">{description}</p>

      <dl className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <Stat label="Estrellas" value={`★ ${compactNumber(repo.stars)}`} title={fullNumber(repo.stars)} />
        <Stat label="Última actualización" value={relativeTime(repo.last_commit_at)} title={formatDate(repo.last_commit_at)} />
        <Stat label="Licencia" value={repo.license ?? "Sin licencia"} />
        <Stat label="Lenguaje" value={repo.language ?? "Sin datos"} />
        <Stat label="Forks" value={compactNumber(repo.forks)} title={fullNumber(repo.forks)} />
        <Stat label="Issues abiertos" value={repo.has_issues ? fullNumber(repo.open_issues) : "Otro sistema"} />
        <Stat label="Health score" value={`${repo.metrics.health_score}/100`} />
        <Stat
          label="Mantenedor activo"
          value={repo.maintainer_active === null ? "Sin datos" : repo.maintainer_active ? "Sí" : "No"}
        />
      </dl>

      <section aria-labelledby="desglose" className="flex flex-col gap-2">
        <h3 id="desglose" className="font-semibold">Desglose del health score</h3>
        {details ? (
          <ul className="grid gap-2 sm:grid-cols-2">
            {SCORE_PARTS.map((part) => (
              <ScoreBar key={part.key} label={part.label} value={details[part.key]} max={part.max} />
            ))}
          </ul>
        ) : (
          <p className="text-sm text-text-muted">Sin desglose disponible.</p>
        )}
        {noActivity && (
          <p className="text-xs text-text-muted">
            Sin datos de actividad de commits: el puntaje se calculó con los demás componentes.
          </p>
        )}
      </section>

      {(repo.detected_stack.length > 0 || repo.integration_methods_suggested.length > 0) && (
        <section className="grid gap-3 sm:grid-cols-2">
          <ChipList title="Stack detectado" items={repo.detected_stack} />
          <ChipList title="Cómo se integra" items={repo.integration_methods_suggested} />
        </section>
      )}

      <section aria-labelledby="ideas" className="flex flex-col gap-3">
        <h3 id="ideas" className="font-semibold">
          {repo.integrations.length === 1 ? "Idea de integración" : `Ideas de integración (${repo.integrations.length})`}
        </h3>
        {repo.integrations.length === 0 && <p className="text-sm text-text-muted">Todavía no hay ideas de integración para este repositorio.</p>}
        {repo.integrations.map((idea) => (
          <IntegrationIdea key={idea.id} idea={idea} onSelect={onSelect} />
        ))}
      </section>

      <div className="flex flex-wrap gap-3 border-t border-border pt-4">
        <a
          href={repo.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex h-11 items-center rounded-[var(--radius-pill)] bg-primary px-5 font-semibold text-primary-contrast hover:opacity-90"
        >
          Ver en GitHub
        </a>
        {repo.homepage && (
          <a
            href={repo.homepage}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-11 items-center rounded-[var(--radius-pill)] border border-border px-5 font-semibold hover:bg-surface-hover"
          >
            Sitio oficial
          </a>
        )}
        {!repo.has_issues && repo.issues_url && (
          <a href={repo.issues_url} target="_blank" rel="noreferrer" className="inline-flex h-11 items-center font-semibold text-primary hover:underline">
            Sistema de incidencias
          </a>
        )}
      </div>
    </>
  );
}

function Stat({ label, value, title }: { label: string; value: string; title?: string }) {
  return (
    <div className="flex flex-col-reverse rounded-xl bg-surface px-3 py-2" title={title}>
      <dt className="text-xs text-text-muted">{label}</dt>
      <dd className="font-semibold">{value}</dd>
    </div>
  );
}

function ScoreBar({ label, value, max }: { label: string; value: number | null; max: number }) {
  const pct = value === null ? 0 : Math.round((value / max) * 100);
  return (
    <li className="flex flex-col gap-1 text-sm">
      <span className="flex justify-between gap-2">
        <span>{label}</span>
        <span className="text-text-muted">{value === null ? "Sin datos" : `${value}/${max}`}</span>
      </span>
      <span className="h-2 overflow-hidden rounded-full bg-border" role="img" aria-label={`${label}: ${value ?? "sin datos"} de ${max}`}>
        <span className="block h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
      </span>
    </li>
  );
}

function ChipList({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="flex flex-col gap-1.5">
      <h3 className="text-sm font-semibold">{title}</h3>
      <ul className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <li key={item} className="rounded-md bg-surface-hover px-2 py-0.5 text-xs font-medium">{item}</li>
        ))}
      </ul>
    </div>
  );
}

// Bloque de la idea de integración, con el estilo del prototipo (borde rosa sobre fondo rosa suave).
function IntegrationIdea({ idea, onSelect }: { idea: Integration; onSelect: (id: number) => void }) {
  return (
    <article className="flex flex-col gap-3 rounded-r-xl border-l-4 border-brand-pink bg-brand-pink-soft p-4 text-[#0f172a]">
      <div className="flex flex-col gap-1">
        <span className="text-xs font-semibold text-brand-pink-deep">{idea.code}</span>
        <h4 className="font-semibold">{idea.purpose}</h4>
      </div>
      <div className="flex flex-wrap gap-1.5 text-xs">
        <span className="rounded-md bg-brand-indigo-soft px-2 py-0.5 font-medium">{idea.integration_type}</span>
        <span className="rounded-md bg-brand-indigo-soft px-2 py-0.5 font-medium">Dificultad {idea.difficulty.toLowerCase()}</span>
      </div>
      {idea.role && (
        <p className="text-sm"><strong>Rol en la integración:</strong> {idea.role}</p>
      )}
      {idea.triggers_or_webhooks && (
        <p className="text-sm"><strong>Disparadores:</strong> {idea.triggers_or_webhooks}</p>
      )}
      {idea.compatible_stack.length > 0 && (
        <p className="text-sm"><strong>Compatible con:</strong> {idea.compatible_stack.join(", ")}</p>
      )}
      {idea.main_steps.length > 0 && (
        <div className="text-sm">
          <strong>Pasos principales</strong>
          <ol className="mt-1 list-decimal pl-5">
            {idea.main_steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}
      {idea.example_snippet && (
        <pre className="overflow-x-auto rounded-xl bg-[#0f172a] p-3 font-mono text-sm leading-relaxed text-[#e2e8f0]">
          <code>{idea.example_snippet}</code>
        </pre>
      )}
      {idea.related_repositories.length > 0 && (
        <div className="text-sm">
          <strong>Se combina con</strong>
          <ul className="mt-1 flex flex-col gap-1">
            {idea.related_repositories.map((rel) => (
              <li key={rel.id}>
                <button type="button" onClick={() => onSelect(rel.id)} className="font-semibold text-brand-indigo-strong underline-offset-2 hover:underline">
                  {rel.full_name}
                </button>
                {rel.role && <span>: {rel.role}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
      {idea.business_cases.length > 0 && (
        <div className="text-sm">
          <strong>Casos de negocio</strong>
          <ul className="mt-1 list-disc pl-5">
            {idea.business_cases.map((bc) => (
              <li key={bc.id}>{bc.name}</li>
            ))}
          </ul>
        </div>
      )}
      {idea.documentation_url && (
        <a href={idea.documentation_url} target="_blank" rel="noreferrer" className="self-start text-sm font-semibold text-brand-indigo-strong hover:underline">
          Documentación oficial de la integración ↗
        </a>
      )}
    </article>
  );
}
