"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import HealthBadge from "@/components/HealthBadge";
import RepositoryDetailDialog from "@/components/RepositoryDetailDialog";
import { AlertBadges } from "@/components/RiskAlerts";
import { ApiError, compareRepositories } from "@/lib/api";
import { compactNumber, formatDate, fullNumber, relativeTime } from "@/lib/format";
import type { CompareResponse, RepositoryDetail } from "@/types/api";

// Comparador de herramientas lado a lado (9.5): consume /repositories/compare.

type Status = { kind: "loading" } | { kind: "ok"; data: CompareResponse } | { kind: "error"; message: string };

function errorMessage(err: unknown) {
  if (err instanceof ApiError && err.status === 400) return err.message;
  // 422: la API todavía no tiene la ruta /compare y la toma como si fuera /{id}.
  if (err instanceof ApiError && err.status === 422) return "El comparador todavía no está disponible en esta versión de la API.";
  if (err instanceof ApiError && err.status === 404) return err.message;
  if (err instanceof ApiError && err.status === 0) return "No pudimos conectar con la API. Revisa que el backend esté corriendo.";
  return "Ocurrió un error al cargar la comparación. Intenta de nuevo en unos minutos.";
}

function parseIds(raw: string | null) {
  return [...new Set((raw ?? "").split(",").map((v) => Number(v.trim())).filter((n) => Number.isInteger(n) && n > 0))];
}

type Row = { label: string; hint?: string; value: (r: RepositoryDetail) => ReactNode; best?: (r: RepositoryDetail) => number | null };

const ROWS: Row[] = [
  { label: "Categoría", value: (r) => r.category.name },
  {
    label: "Health score",
    value: (r) => <HealthBadge status={r.metrics.health_status} score={r.metrics.health_score} />,
    best: (r) => r.metrics.health_score,
  },
  { label: "Mantenimiento", hint: "Puntos (máx. 30) según los días desde el último commit", value: (r) => r.metrics.health_score_details?.maintenance ?? "Sin datos", best: (r) => r.metrics.health_score_details?.maintenance ?? null },
  { label: "Actividad", hint: "Puntos (máx. 25) según los commits de los últimos 90 días", value: (r) => r.metrics.health_score_details?.commit_activity ?? "Sin datos", best: (r) => r.metrics.health_score_details?.commit_activity ?? null },
  { label: "Estrellas", value: (r) => <span title={fullNumber(r.stars)}>★ {compactNumber(r.stars)}</span>, best: (r) => r.stars },
  { label: "Forks", value: (r) => <span title={fullNumber(r.forks)}>{compactNumber(r.forks)}</span>, best: (r) => r.forks },
  { label: "Última actualización", value: (r) => <span title={formatDate(r.last_commit_at)}>{relativeTime(r.last_commit_at)}</span> },
  { label: "Licencia", value: (r) => r.license ?? "Sin licencia" },
  { label: "Alertas de riesgo", value: (r) => (r.alerts?.length ? <AlertBadges alerts={r.alerts} /> : <span className="text-text-muted">Ninguna</span>) },
  { label: "Lenguaje", value: (r) => r.language ?? "Sin datos" },
  { label: "Issues abiertos", value: (r) => (r.has_issues ? fullNumber(r.open_issues) : "Otro sistema") },
  { label: "Mantenedor activo", value: (r) => (r.maintainer_active === null ? "Sin datos" : r.maintainer_active ? "Sí" : "No") },
  { label: "Ideas de integración", value: (r) => (r.integrations.length ? `${r.integrations.length} (${[...new Set(r.integrations.map((i) => i.integration_type))].join(", ")})` : "Ninguna") },
  { label: "Se integra con", value: (r) => (r.integration_methods_suggested.length ? r.integration_methods_suggested.join(", ") : "Sin datos") },
];

export default function CompareView() {
  const params = useSearchParams();
  const ids = parseIds(params.get("ids"));
  const key = ids.join(",");
  const [status, setStatus] = useState<Status>({ kind: "loading" });
  const [openId, setOpenId] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (ids.length < 2) {
      setStatus({ kind: "error", message: "Elige al menos 2 herramientas en el catálogo para compararlas." });
      return;
    }
    setStatus({ kind: "loading" });
    compareRepositories(ids)
      .then((data) => !cancelled && setStatus({ kind: "ok", data }))
      .catch((err) => !cancelled && setStatus({ kind: "error", message: errorMessage(err) }));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-2">
        <Link href="/" className="inline-flex h-11 items-center gap-2 self-start rounded-[var(--radius-pill)] border border-border bg-card px-5 text-sm font-semibold hover:bg-surface-hover">
          ← Volver al catálogo
        </Link>
        <h1 className="text-3xl font-bold">Comparar herramientas</h1>
      </header>

      {status.kind === "loading" && (
        <div className="h-64 animate-pulse rounded-[var(--radius-card)] border border-border bg-card" aria-label="Cargando la comparación" />
      )}

      {status.kind === "error" && (
        <p role="alert" className="rounded-[var(--radius-card)] border border-dashed border-border p-8 text-center text-text-muted">
          {status.message}
        </p>
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
  const [frame, setFrame] = useState<Frame | null>(null);

  // Mide la columna destacada para dibujar el recuadro encima (se recalcula al cambiar el tamaño).
  useLayoutEffect(() => {
    const wrap = wrapRef.current;
    const th = bestRef.current;
    if (!wrap || !th) {
      setFrame(null);
      return;
    }
    const measure = () => {
      const w = wrap.getBoundingClientRect();
      const c = th.getBoundingClientRect();
      setFrame({ left: c.left - w.left + wrap.scrollLeft, width: c.width, height: wrap.scrollHeight });
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(wrap);
    ro.observe(th);
    return () => ro.disconnect();
  }, [bestId, repos.length]);

  return (
    <>
      <p className={`rounded-xl px-4 py-3 text-sm ${data.same_category ? "bg-surface-hover" : "bg-status-risk-bg text-status-risk"}`}>
        {data.same_category
          ? `Todas son de la categoría ${data.category_name}: cumplen la misma función y se pueden comparar directamente.`
          : "Son de categorías distintas: cumplen funciones diferentes, así que la comparación es solo referencial."}
      </p>
      <div ref={wrapRef} className="relative overflow-x-auto rounded-[var(--radius-card)] border border-border bg-card">
        <table className="w-full min-w-[640px] border-collapse text-sm">
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
                    <span className="font-display text-lg font-semibold first-letter:uppercase">{r.name}</span>
                    <span className="text-xs font-normal text-text-muted">{r.full_name}</span>
                    <span className="flex flex-wrap gap-3 text-xs font-semibold">
                      <button type="button" onClick={() => onOpen(r.id)} className="text-primary hover:underline">
                        Ver ficha
                      </button>
                      <a href={r.url} target="_blank" rel="noreferrer" className="text-primary hover:underline">
                        GitHub ↗
                      </a>
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map((row) => {
              const values = row.best ? repos.map(row.best) : [];
              const numbers = values.filter((v): v is number => typeof v === "number");
              const max = numbers.length > 1 ? Math.max(...numbers) : null;
              const tie = max !== null && numbers.filter((v) => v === max).length === numbers.length;
              return (
                <tr key={row.label} className="border-t border-border">
                  <th scope="row" className="p-4 text-left align-top font-semibold">
                    {row.label}
                    {row.hint && <span className="block text-xs font-normal text-text-muted">{row.hint}</span>}
                  </th>
                  {repos.map((r, i) => {
                    const isBest = max !== null && !tie && values[i] === max;
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
