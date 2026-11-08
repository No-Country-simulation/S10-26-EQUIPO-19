"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import HealthBadge from "@/components/HealthBadge";
import RepositoryDetailDialog from "@/components/RepositoryDetailDialog";
import { AlertBadges } from "@/components/RiskAlerts";
import ErrorNotice, { SlowNotice } from "@/components/ErrorNotice";
import { ApiError, compareRepositories } from "@/lib/api";
import { friendlyError, type FriendlyError } from "@/lib/errors";
import { compactNumber, formatDate, fullNumber, relativeTime, safeExternalUrl } from "@/lib/format";
import type { CompareResponse, RepositoryDetail } from "@/types/api";

// Comparador de herramientas lado a lado (9.5): consume /repositories/compare.

type Status = { kind: "loading" } | { kind: "ok"; data: CompareResponse } | { kind: "error"; error: FriendlyError };

function compareError(err: unknown): FriendlyError {
  // Validaciones del servidor (cantidad o formato): sus textos ya están pensados para el usuario.
  if (err instanceof ApiError && err.kind === "invalid" && err.status === 400 && err.detail) {
    return { title: "Revisa tu selección", message: err.detail, retry: false };
  }
  if (err instanceof ApiError && err.kind === "not_found") {
    return { title: "Alguna herramienta ya no está disponible", message: "Vuelve al catálogo y elige otra para comparar.", retry: false };
  }
  return friendlyError(err, "la comparación");
}

function parseIds(raw: string | null) {
  return [...new Set((raw ?? "").split(",").map((v) => Number(v.trim())).filter((n) => Number.isInteger(n) && n > 0))];
}

type Row = {
  label: string;
  /** Explicación corta que se abre con "?" (5). */
  help: string;
  value: (r: RepositoryDetail) => ReactNode;
  /** Valor comparable: si es igual en todas las columnas, la fila se oculta con "Mostrar solo diferencias" (9). */
  same: (r: RepositoryDetail) => string;
  best?: (r: RepositoryDetail) => number | null;
};

const alertTitles = (r: RepositoryDetail) => (r.alerts ?? []).map((a) => a.title).join(", ");
const integrationsText = (r: RepositoryDetail) =>
  r.integrations.length ? `${r.integrations.length} (${[...new Set(r.integrations.map((i) => i.integration_type))].join(", ")})` : "Ninguna";

const ROWS: Row[] = [
  { label: "Categoría", help: "Función que cumple la herramienta en un stack, según la taxonomía del catálogo.", value: (r) => r.category.name, same: (r) => r.category.name },
  {
    label: "Health score",
    help: "Puntaje de 0 a 100 que resume mantenimiento, actividad, popularidad y forks. Se recalcula a diario con datos de GitHub.",
    value: (r) => <HealthBadge status={r.metrics.health_status} score={r.metrics.health_score} />,
    same: (r) => `${r.metrics.health_status}-${r.metrics.health_score}`,
    best: (r) => r.metrics.health_score,
  },
  {
    label: "Mantenimiento",
    help: "Puntos (máx. 30) según los días desde el último commit de la rama principal: más puntos cuanto más reciente; 0 si el repositorio está archivado.",
    value: (r) => r.metrics.health_score_details?.maintenance ?? "Sin datos",
    same: (r) => String(r.metrics.health_score_details?.maintenance ?? ""),
    best: (r) => r.metrics.health_score_details?.maintenance ?? null,
  },
  {
    label: "Actividad",
    help: "Puntos (máx. 25) según los commits de los últimos 90 días: más puntos cuanta más actividad tuvo el repositorio.",
    value: (r) => r.metrics.health_score_details?.commit_activity ?? "Sin datos",
    same: (r) => String(r.metrics.health_score_details?.commit_activity ?? ""),
    best: (r) => r.metrics.health_score_details?.commit_activity ?? null,
  },
  { label: "Estrellas", help: "Cuántas personas marcaron el repositorio en GitHub: indica popularidad.", value: (r) => <span title={fullNumber(r.stars)}>★ {compactNumber(r.stars)}</span>, same: (r) => String(r.stars), best: (r) => r.stars },
  { label: "Forks", help: "Copias del repositorio hechas por otras personas: indica adopción y contribuciones externas.", value: (r) => <span title={fullNumber(r.forks)}>{compactNumber(r.forks)}</span>, same: (r) => String(r.forks), best: (r) => r.forks },
  { label: "Última actualización", help: "Último commit en la rama principal del repositorio.", value: (r) => <span title={formatDate(r.last_commit_at)}>{relativeTime(r.last_commit_at)}</span>, same: (r) => relativeTime(r.last_commit_at) },
  { label: "Licencia", help: "Condiciones de uso. Las copyleft fuertes (como AGPL o GPL) imponen obligaciones al distribuir el código o al ofrecerlo como servicio.", value: (r) => r.license ?? "Sin licencia", same: (r) => r.license ?? "" },
  { label: "Alertas de riesgo", help: "Avisos por licencias con obligaciones o por falta de mantenimiento.", value: (r) => (r.alerts?.length ? <AlertBadges alerts={r.alerts} /> : <span className="text-text-muted">Ninguna</span>), same: alertTitles },
  { label: "Lenguaje", help: "Lenguaje principal del código del repositorio.", value: (r) => r.language ?? "Sin datos", same: (r) => r.language ?? "" },
  { label: "Issues abiertos", help: "Reportes abiertos en GitHub. \"Otro sistema\" significa que el proyecto usa otra herramienta para sus reportes.", value: (r) => (r.has_issues ? fullNumber(r.open_issues) : "Otro sistema"), same: (r) => (r.has_issues ? String(r.open_issues) : "otro") },
  { label: "Mantenedor activo", help: "Sí, si el repositorio no está archivado y tiene commits en los últimos 90 días.", value: (r) => (r.maintainer_active === null ? "Sin datos" : r.maintainer_active ? "Sí" : "No"), same: (r) => String(r.maintainer_active) },
  { label: "Ideas de integración", help: "Ideas revisadas del catálogo para conectar esta herramienta con otras.", value: integrationsText, same: integrationsText },
  { label: "Se integra con", help: "Formas de integración sugeridas, como API REST, Docker o SDK.", value: (r) => (r.integration_methods_suggested.length ? r.integration_methods_suggested.join(", ") : "Sin datos"), same: (r) => r.integration_methods_suggested.join(",") },
];

/** Botón "?" que muestra la explicación de la métrica; funciona con clic, teclado y pantalla táctil. */
function Help({ id, text }: { id: string; text: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-controls={id}
        aria-label="¿Qué es esto?"
        title="¿Qué es esto?"
        className="group ml-0.5 inline-flex size-6 items-center justify-center align-middle"
      >
        <span className="inline-flex size-[18px] items-center justify-center rounded-full border border-border text-xs font-semibold text-text-muted group-hover:border-primary group-hover:text-primary">
          ?
        </span>
      </button>
      {open && (
        <span id={id} className="mt-1 block text-[13px] leading-snug font-normal text-text-muted">
          {text}
        </span>
      )}
    </>
  );
}

/** Aviso destacado de la columna (12): archivado, abandonado, en riesgo o con alertas de licencia. */
function riskNotice(r: RepositoryDetail): { label: string; abandoned: boolean } | null {
  if (r.archived) return { label: "Archivado", abandoned: true };
  if (r.metrics.health_status === "Abandonado") return { label: "Abandonado", abandoned: true };
  if (r.metrics.health_status === "En riesgo") return { label: "Mantenimiento en riesgo", abandoned: false };
  if (r.alerts?.length) return { label: r.alerts[0].title, abandoned: false };
  return null;
}

/** Mayor valor de cada fila con métrica numérica: solo cuenta si no es un empate entre todas. */
function rowWinners(row: Row, repos: RepositoryDetail[]): number[] {
  if (!row.best) return [];
  const values = repos.map(row.best);
  const numbers = values.filter((v): v is number => typeof v === "number");
  if (numbers.length < 2) return [];
  const max = Math.max(...numbers);
  if (numbers.every((v) => v === max)) return [];
  return repos.filter((_, i) => values[i] === max).map((r) => r.id);
}

/** Resumen (1): quién tiene el mayor valor en más métricas, solo con datos. */
function summaryText(repos: RepositoryDetail[]): string {
  const metricRows = ROWS.filter((r) => r.best);
  const counts = new Map(repos.map((r) => [r.id, [] as string[]]));
  for (const row of metricRows) for (const id of rowWinners(row, repos)) counts.get(id)?.push(row.label.toLowerCase());
  const top = Math.max(...[...counts.values()].map((v) => v.length));
  if (top === 0) return `Empatan en las ${metricRows.length} métricas comparables.`;
  const leaders = repos.filter((r) => counts.get(r.id)!.length === top);
  const names = leaders.map((r) => r.name.charAt(0).toUpperCase() + r.name.slice(1));
  if (leaders.length === 1) {
    return `${names[0]} tiene el mayor valor en ${top} de ${metricRows.length} métricas comparables (${counts.get(leaders[0].id)!.join(", ")}).`;
  }
  return `${names.join(" y ")} empatan: cada una tiene el mayor valor en ${top} de ${metricRows.length} métricas comparables.`;
}

export default function CompareView() {
  const params = useSearchParams();
  const ids = parseIds(params.get("ids"));
  const key = ids.join(",");
  const [status, setStatus] = useState<Status>({ kind: "loading" });
  const [openId, setOpenId] = useState<number | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    if (ids.length < 2) {
      setStatus({ kind: "error", error: { title: "Elige al menos 2 herramientas", message: "Vuelve al catálogo y marca entre 2 y 3 herramientas con \"+ Comparar\".", retry: false } });
      return;
    }
    setStatus({ kind: "loading" });
    compareRepositories(ids)
      .then((data) => !cancelled && setStatus({ kind: "ok", data }))
      .catch((err) => {
        if (cancelled) return;
        console.warn(err);
        setStatus({ kind: "error", error: compareError(err) });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, attempt]);

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-2">
        <Link href="/" className="inline-flex h-11 items-center gap-2 self-start rounded-[var(--radius-pill)] border border-border bg-card px-5 text-sm font-semibold hover:bg-surface-hover">
          ← Volver al catálogo
        </Link>
        <h1 className="text-3xl font-bold">Comparar herramientas</h1>
      </header>

      <SlowNotice active={status.kind === "loading"} />
      {status.kind === "loading" && (
        <div className="h-64 animate-pulse rounded-[var(--radius-card)] border border-border bg-card" aria-label="Cargando la comparación" />
      )}

      {status.kind === "error" && (
        <ErrorNotice error={status.error} onRetry={() => setAttempt((n) => n + 1)}>
          <Link href="/" className="inline-flex h-11 items-center rounded-[var(--radius-pill)] border border-border px-6 font-semibold hover:bg-surface-hover">
            Volver al catálogo
          </Link>
        </ErrorNotice>
      )}

      {status.kind === "ok" && <CompareTable data={status.data} onOpen={setOpenId} />}

      <RepositoryDetailDialog repoId={openId} onClose={() => setOpenId(null)} onSelect={setOpenId} />
    </div>
  );
}

/** Columna con el mayor health score: solo si todas son de la misma categoría y no hay empate. */
function bestHealthId(data: CompareResponse): number | null {
  if (!data.same_category) return null;
  const scored = data.repositories.filter((r) => typeof r.metrics.health_score === "number");
  if (scored.length < 2) return null;
  const max = Math.max(...scored.map((r) => r.metrics.health_score as number));
  const top = scored.filter((r) => r.metrics.health_score === max);
  return top.length === 1 ? top[0].id : null;
}

type Frame = { left: number; width: number; height: number };

function CompareTable({ data, onOpen }: { data: CompareResponse; onOpen: (id: number) => void }) {
  const repos = data.repositories;
  const bestId = bestHealthId(data);
  const wrapRef = useRef<HTMLDivElement>(null);
  const bestRef = useRef<HTMLTableCellElement>(null);
  const tableRef = useRef<HTMLTableElement>(null);
  const [frame, setFrame] = useState<Frame | null>(null);
  const [onlyDiff, setOnlyDiff] = useState(false);
  const visibleRows = onlyDiff ? ROWS.filter((row) => new Set(repos.map(row.same)).size > 1) : ROWS;

  // Mide la columna destacada para dibujar el recuadro encima (se recalcula al cambiar el tamaño).
  useLayoutEffect(() => {
    const wrap = wrapRef.current;
    const th = bestRef.current;
    const table = tableRef.current;
    if (!wrap || !th || !table) {
      setFrame(null);
      return;
    }
    const measure = () => {
      const w = wrap.getBoundingClientRect();
      const c = th.getBoundingClientRect();
      setFrame({ left: c.left - w.left + wrap.scrollLeft, width: c.width, height: table.offsetHeight });
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(wrap);
    ro.observe(th);
    ro.observe(table);
    return () => ro.disconnect();
  }, [bestId, repos.length]);

  return (
    <>
      <p className={`rounded-xl px-4 py-3 text-sm ${data.same_category ? "bg-surface-hover" : "bg-status-risk-bg text-status-risk"}`}>
        {data.same_category
          ? `Todas son de la categoría ${data.category_name}: cumplen la misma función y se pueden comparar directamente.`
          : "Son de categorías distintas: cumplen funciones diferentes, así que la comparación es solo referencial."}
      </p>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-semibold">{summaryText(repos)}</p>
        <label className="inline-flex cursor-pointer items-center gap-2 text-sm">
          <input type="checkbox" checked={onlyDiff} onChange={(e) => setOnlyDiff(e.target.checked)} className="size-4 accent-[var(--color-brand-indigo)]" />
          Mostrar solo diferencias
        </label>
      </div>
      <p className="text-xs text-text-muted md:hidden">Desliza la tabla hacia el lado para ver todas las herramientas →</p>
      <div ref={wrapRef} className="relative overflow-x-auto rounded-[var(--radius-card)] border border-border bg-card">
        <table ref={tableRef} className="w-full min-w-[640px] table-fixed border-collapse text-sm break-words">
          <caption className="sr-only">Comparación lado a lado de {repos.length} herramientas</caption>
          <thead>
            <tr>
              <th scope="col" className="w-44 p-4 text-left text-xs font-semibold uppercase text-text-muted">Herramienta</th>
              {repos.map((r) => (
                <th key={r.id} ref={r.id === bestId ? bestRef : undefined} scope="col" className="p-4 pt-5 text-left align-top">
                  <div className="flex flex-col gap-1">
                    {r.id === bestId && (
                      <span className="self-start rounded-[var(--radius-pill)] bg-brand-indigo-strong px-2.5 py-0.5 text-xs font-semibold text-white">
                        Mejor puntaje de salud
                      </span>
                    )}
                    {(() => {
                      const notice = riskNotice(r);
                      return notice ? (
                        <span
                          className={`self-start rounded-md px-2 py-0.5 text-xs font-semibold ${
                            notice.abandoned ? "bg-status-abandoned-bg text-status-abandoned" : "bg-status-risk-bg text-status-risk"
                          }`}
                        >
                          ⚠ {notice.label}
                        </span>
                      ) : null;
                    })()}
                    <span className="font-display text-lg font-semibold first-letter:uppercase">{r.name}</span>
                    <span className="text-xs font-normal text-text-muted">{r.full_name}</span>
                    <span className="flex flex-wrap gap-3 text-xs font-semibold">
                      <button type="button" onClick={() => onOpen(r.id)} className="text-primary hover:underline">
                        Ver ficha
                      </button>
                      <a href={safeExternalUrl(r.url) ?? undefined} target="_blank" rel="noreferrer" className="text-primary hover:underline">
                        GitHub ↗
                      </a>
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, rowIndex) => {
              const winners = rowWinners(row, repos);
              return (
                <tr key={row.label} className="border-t border-border">
                  <th scope="row" className="p-4 text-left align-top font-semibold">
                    {row.label}
                    <Help id={`ayuda-${rowIndex}`} text={row.help} />
                  </th>
                  {repos.map((r) => {
                    const isBest = winners.includes(r.id);
                    return (
                      <td key={r.id} className={`p-4 align-top ${isBest ? "font-semibold" : ""}`}>
                        <span className="flex flex-wrap items-center gap-2">
                          {row.value(r)}
                          {isBest && <span className="rounded-md bg-status-active-bg px-1.5 py-0.5 text-xs text-status-active">Mayor</span>}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
            {visibleRows.length === 0 && (
              <tr className="border-t border-border">
                <td colSpan={repos.length + 1} className="p-6 text-center text-text-muted">
                  No hay diferencias: todas las filas tienen los mismos valores.
                </td>
              </tr>
            )}
          </tbody>
        </table>
        {frame && (
          <div
            aria-hidden="true"
            className="pointer-events-none absolute top-1 rounded-xl border-2 border-brand-indigo bg-brand-indigo/[0.05] shadow-[0_8px_24px_-8px_rgba(99,102,241,0.45)] dark:bg-brand-indigo/10 dark:shadow-[0_0_28px_2px_rgba(99,102,241,0.55)]"
            style={{ left: frame.left + 4, width: frame.width - 8, height: frame.height - 8 }}
          />
        )}
      </div>
    </>
  );
}
