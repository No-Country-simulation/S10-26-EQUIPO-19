"use client";

import { useEffect, useRef, useState } from "react";
import HealthBadge from "@/components/HealthBadge";
import { ApiError, getRepository } from "@/lib/api";
import { compactNumber, formatDate, fullNumber, relativeTime, splitUrls, urlHost } from "@/lib/format";
import type { HealthScoreDetails, Integration, RepositoryDetail } from "@/types/api";

type Status = { kind: "idle" } | { kind: "loading" } | { kind: "ok"; repo: RepositoryDetail } | { kind: "error"; message: string };

// Componentes del health score con su puntaje máximo (documento Health Score de repositorios).
// La barra muestra el porcentaje logrado de cada componente, como en el prototipo.
const SCORE_PARTS: { key: keyof HealthScoreDetails; label: string; hint: string; max: number }[] = [
  { key: "maintenance", label: "Mantenimiento", hint: "Releases y respuesta a issues", max: 30 },
  { key: "commit_activity", label: "Actividad", hint: "Commits y pull requests recientes", max: 25 },
  { key: "popularity", label: "Popularidad", hint: "Estrellas y uso en la comunidad", max: 15 },
  { key: "forks", label: "Forks", hint: "Adopción y contribuciones externas", max: 10 },
];

const panel = "flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 sm:p-6";

function errorMessage(err: unknown) {
  if (err instanceof ApiError && err.status === 404) return "No encontramos este repositorio, o su ficha todavía no está disponible en la API.";
  if (err instanceof ApiError && err.status === 0) return "No pudimos conectar con la API. Revisa que el backend esté corriendo.";
  return "Ocurrió un error al cargar la ficha. Intenta de nuevo en unos minutos.";
}

// Ficha técnica (5.6) en una ventana emergente grande con scroll interno, como definió el equipo con Diseño:
// "X" arriba para cerrar y "← Volver al catálogo" al final. Usa <dialog>: cierra con Esc, mantiene el foco
// dentro y lo devuelve a la tarjeta al cerrar.
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
  const scrollRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const close = () => ref.current?.close();

  // Abre o cierra la ventana y bloquea el scroll de la página de fondo mientras está abierta.
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (repoId !== null && !dialog.open) dialog.showModal();
    if (repoId === null && dialog.open) dialog.close();
    document.body.style.overflow = repoId !== null ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [repoId]);

  useEffect(() => {
    if (repoId === null) return;
    let cancelled = false;
    setStatus({ kind: "loading" });
    scrollRef.current?.scrollTo({ top: 0 });
    getRepository(repoId)
      .then((repo) => !cancelled && setStatus({ kind: "ok", repo }))
      .catch((err) => !cancelled && setStatus({ kind: "error", message: errorMessage(err) }));
    return () => {
      cancelled = true;
    };
  }, [repoId]);

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={(e) => e.target === ref.current && close()}
      aria-labelledby="ficha-titulo"
      className="m-auto h-[92vh] max-h-[92vh] w-[calc(100%-24px)] max-w-6xl overflow-hidden rounded-3xl border border-border bg-surface p-0 text-text shadow-2xl backdrop:bg-[#0f172a]/60"
    >
      <div ref={scrollRef} className="relative h-full overflow-y-auto overscroll-contain">
        <div className="sticky top-0 z-10 flex justify-end p-3 sm:p-4">
          <button
            type="button"
            onClick={close}
            aria-label="Cerrar la ficha"
            className="flex h-11 w-11 items-center justify-center rounded-full border border-border bg-card text-lg text-text shadow-md hover:bg-surface-hover"
          >
            ✕
          </button>
        </div>
        <div className="-mt-14 flex flex-col gap-6 px-5 pb-8 sm:-mt-16 sm:px-8 sm:pb-10">
          {status.kind === "loading" && (
        <div className="flex flex-col gap-4" aria-busy="true" aria-label="Cargando ficha">
          <div className="h-10 w-64 animate-pulse rounded-xl bg-surface-muted" />
          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
            <div className="h-80 animate-pulse rounded-2xl bg-surface-muted" />
            <div className="h-80 animate-pulse rounded-2xl bg-surface-muted" />
          </div>
        </div>
      )}
      {status.kind === "error" && (
        <div role="alert" className="flex flex-col gap-2 rounded-2xl border border-dashed border-border p-8 text-center">
          <h2 id="ficha-titulo" className="text-2xl font-bold">Ficha no disponible</h2>
          <p className="text-text-muted">{status.message}</p>
        </div>
      )}
          {status.kind === "ok" && <DetailBody repo={status.repo} onSelect={onSelect} />}
          {status.kind !== "ok" && <BackButton onClick={close} />}
          {status.kind === "ok" && (
            <div className="flex justify-center border-t border-border pt-6">
              <BackButton onClick={close} />
            </div>
          )}
        </div>
      </div>
    </dialog>
  );
}

function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex h-11 items-center gap-2 self-start rounded-[var(--radius-pill)] border border-border bg-card px-5 text-sm font-semibold text-text hover:bg-surface-hover"
    >
      ← Volver al catálogo
    </button>
  );
}

function DetailBody({ repo, onSelect }: { repo: RepositoryDetail; onSelect: (id: number) => void }) {
  const description = repo.description_es || repo.description || "Sin descripción.";
  const docsUrl = repo.homepage || repo.integrations.flatMap((i) => splitUrls(i.documentation_url))[0] || null;

  // Casos de negocio y repositorios relacionados de todas las ideas, sin repetidos.
  const cases = [...new Map(repo.integrations.flatMap((i) => i.business_cases).map((c) => [c.id, c])).values()];
  const related = [...new Map(repo.integrations.flatMap((i) => i.related_repositories).map((r) => [r.id, r])).values()];

  return (
    <>
      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="rounded-md bg-brand-pink-soft px-2 py-0.5 font-medium text-[#0f172a]">{repo.category.name}</span>
          <HealthBadge status={repo.metrics.health_status} score={repo.metrics.health_score} />
          {repo.archived && <span className="rounded-md bg-status-abandoned-bg px-2 py-0.5 font-semibold text-status-abandoned">Archivado</span>}
        </div>
        <div className="flex flex-col gap-1 pr-14">
          <h2 id="ficha-titulo" className="break-words text-3xl font-bold leading-tight first-letter:uppercase sm:text-4xl">{repo.name}</h2>
          <p className="text-sm text-text-muted">{repo.full_name}</p>
        </div>
        <p className="max-w-[70ch] text-lg text-text-muted">{description}</p>
        <div className="flex flex-wrap gap-3">
          {docsUrl && (
            <a
              href={docsUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-11 items-center gap-2 rounded-[var(--radius-pill)] bg-primary px-5 font-semibold text-primary-contrast hover:opacity-90"
            >
              Documentación oficial ↗
            </a>
          )}
          <a
            href={repo.url}
            target="_blank"
            rel="noreferrer"
            className={`inline-flex h-11 items-center gap-2 rounded-[var(--radius-pill)] px-5 font-semibold ${
              docsUrl ? "border border-border hover:bg-surface-hover" : "bg-primary text-primary-contrast hover:opacity-90"
            }`}
          >
            Ver en GitHub ↗
          </a>
        </div>
      </header>

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
        <div className="flex flex-col gap-5">
          <section aria-labelledby="ideas" className={panel}>
            <h2 id="ideas" className="text-xl font-semibold">
              {repo.integrations.length > 1 ? `Ideas de integración (${repo.integrations.length})` : "Idea de integración"}
            </h2>
            {repo.integrations.length === 0 && (
              <p className="text-text-muted">Todavía no hay ideas de integración para este repositorio.</p>
            )}
            {repo.integrations.map((idea) => (
              <IntegrationIdea key={idea.id} idea={idea} />
            ))}
          </section>

          {cases.length > 0 && (
            <section aria-labelledby="casos" className={panel}>
              <h2 id="casos" className="text-xl font-semibold">Casos de negocio</h2>
              <ul className="flex flex-col gap-3">
                {cases.map((c) => (
                  <li key={c.id} className="rounded-xl bg-surface-hover px-4 py-3">{c.name}</li>
                ))}
              </ul>
            </section>
          )}

          {(repo.detected_stack.length > 0 || repo.integration_methods_suggested.length > 0) && (
            <section aria-labelledby="stack" className={panel}>
              <h2 id="stack" className="text-xl font-semibold">Stack e integración</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                <ChipList title="Stack detectado" items={repo.detected_stack} />
                <ChipList title="Cómo se integra" items={repo.integration_methods_suggested} />
              </div>
            </section>
          )}
        </div>

        <div className="flex flex-col gap-5">
          <HealthPanel repo={repo} />

          <section aria-labelledby="metricas" className={panel}>
            <h2 id="metricas" className="text-xl font-semibold">Métricas</h2>
            <dl className="grid grid-cols-2 gap-2">
              <Stat label="Estrellas" value={`★ ${compactNumber(repo.stars)}`} title={fullNumber(repo.stars)} />
              <Stat label="Última actualización" value={relativeTime(repo.last_commit_at)} title={formatDate(repo.last_commit_at)} />
              <Stat label="Licencia" value={repo.license ?? "Sin licencia"} />
              <Stat label="Lenguaje" value={repo.language ?? "Sin datos"} />
              <Stat label="Issues abiertos" value={repo.has_issues ? fullNumber(repo.open_issues) : "Otro sistema"} />
              <Stat label="Forks" value={compactNumber(repo.forks)} title={fullNumber(repo.forks)} />
              <Stat
                label="Mantenedor activo"
                value={repo.maintainer_active === null ? "Sin datos" : repo.maintainer_active ? "Sí" : "No"}
              />
            </dl>
            {!repo.has_issues && repo.issues_url && (
              <a href={repo.issues_url} target="_blank" rel="noreferrer" className="text-sm font-semibold text-primary hover:underline">
                Sistema de incidencias ↗
              </a>
            )}
          </section>

          {related.length > 0 && (
            <section aria-labelledby="relacionados" className={panel}>
              <h2 id="relacionados" className="text-xl font-semibold">Repositorios relacionados</h2>
              <ul className="flex flex-col gap-3">
                {related.map((rel) => (
                  <li key={rel.id}>
                    <button
                      type="button"
                      onClick={() => onSelect(rel.id)}
                      className="flex w-full flex-col gap-0.5 rounded-xl border border-border px-4 py-3 text-left hover:border-primary hover:bg-surface-hover"
                    >
                      <span className="font-semibold">{rel.full_name}</span>
                      {rel.role && <span className="text-sm text-text-muted">{rel.role}</span>}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>

    </>
  );
}

function HealthPanel({ repo }: { repo: RepositoryDetail }) {
  const details = repo.metrics.health_score_details;
  const noActivity = repo.metrics.commit_activity_status === "unavailable";
  return (
    <section aria-labelledby="health" className={panel}>
      <h2 id="health" className="text-xl font-semibold">Health score</h2>
      <p className="font-display text-5xl font-bold leading-none">
        {repo.metrics.health_score}
        <span className="text-lg font-medium text-text-muted">/100</span>
      </p>
      {details ? (
        <ul className="flex flex-col gap-3">
          {SCORE_PARTS.map((part) => (
            <ScoreBar key={part.key} label={part.label} hint={part.hint} max={part.max} value={details[part.key]} />
          ))}
        </ul>
      ) : (
        <p className="text-sm text-text-muted">Sin desglose disponible.</p>
      )}
      {noActivity && (
        <p className="text-xs text-text-muted">Sin datos de actividad de commits: el puntaje se calculó con los demás componentes.</p>
      )}
    </section>
  );
}

function ScoreBar({ label, hint, value, max }: { label: string; hint: string; value: number | null; max: number }) {
  const pct = value === null ? 0 : Math.round((value / max) * 100);
  return (
    <li className="flex flex-col gap-1.5" title={value === null ? undefined : `${value} de ${max} puntos`}>
      <span className="flex items-baseline justify-between gap-3 text-sm">
        <span>
          <strong>{label}</strong> <span className="text-xs text-text-muted">{hint}</span>
        </span>
        <strong>{value === null ? "Sin datos" : pct}</strong>
      </span>
      <span
        className="h-2 overflow-hidden rounded-full bg-border"
        role="img"
        aria-label={value === null ? `${label}: sin datos` : `${label}: ${pct} de 100 (${value} de ${max} puntos)`}
      >
        <span className="block h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
      </span>
    </li>
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

// Bloque de la idea de integración, con el estilo del prototipo (borde rosa sobre fondo rosa suave, texto oscuro).
function IntegrationIdea({ idea }: { idea: Integration }) {
  return (
    <article className="flex flex-col gap-3 rounded-r-xl border-l-4 border-brand-pink bg-brand-pink-soft p-4 text-[#0f172a] sm:p-5">
      <div className="flex flex-wrap gap-1.5 text-xs">
        <span className="rounded-md bg-brand-indigo-soft px-2 py-0.5 font-medium">{idea.integration_type}</span>
        <span className="rounded-md bg-brand-indigo-soft px-2 py-0.5 font-medium">Dificultad {idea.difficulty.toLowerCase()}</span>
        <span className="px-1 py-0.5 font-semibold text-brand-pink-deep">{idea.code}</span>
      </div>
      <h3 className="text-lg font-semibold">{idea.purpose}</h3>
      {idea.role && <p><strong>Rol en la integración:</strong> {idea.role}</p>}
      {idea.triggers_or_webhooks && <p><strong>Disparadores:</strong> {idea.triggers_or_webhooks}</p>}
      {idea.compatible_stack.length > 0 && <p><strong>Compatible con:</strong> {idea.compatible_stack.join(", ")}</p>}
      {idea.main_steps.length > 0 && (
        <div>
          <strong>Pasos principales</strong>
          <ol className="mt-1 list-decimal pl-5">
            {idea.main_steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}
      {idea.example_snippet && (
        <pre className="overflow-x-auto rounded-xl bg-[#0f172a] p-4 font-mono text-sm leading-relaxed text-[#e2e8f0]">
          <code>{idea.example_snippet}</code>
        </pre>
      )}
      {splitUrls(idea.documentation_url).length > 0 && (
        <div className="flex flex-col gap-1 text-sm">
          <strong>Documentación de la integración</strong>
          <ul className="flex flex-wrap gap-x-4 gap-y-1">
            {splitUrls(idea.documentation_url).map((url) => (
              <li key={url}>
                <a href={url} target="_blank" rel="noreferrer" title={url} className="font-semibold text-brand-indigo-strong hover:underline">
                  {urlHost(url)} ↗
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  );
}
