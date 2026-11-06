"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import CatalogFilters, { EMPTY_FILTERS, type Filters } from "@/components/CatalogFilters";
import RepositoryCard from "@/components/RepositoryCard";
import ErrorNotice, { SlowNotice } from "@/components/ErrorNotice";
import RepositoryDetailDialog from "@/components/RepositoryDetailDialog";
import { ApiError, getCategories, hasFilters, listRepositories, searchRepositories } from "@/lib/api";
import { friendlyError, type FriendlyError } from "@/lib/errors";
import type { Category, PaginatedRepositories, SearchParams, SortBy, SortOrder } from "@/types/api";

const PAGE_SIZE = 12;
/** El comparador (9.5) acepta de 2 a 3 repositorios. */
const MAX_COMPARE = 3;

type Sort = { sort_by: SortBy; order: SortOrder };
const DEFAULT_SORT: Sort = { sort_by: "stars", order: "desc" };

const SORT_OPTIONS: { value: SortBy; label: string }[] = [
  { value: "stars", label: "Estrellas" },
  { value: "forks", label: "Forks" },
  { value: "last_commit_at", label: "Última actualización" },
  { value: "health_score", label: "Health score" },
];

function orderLabel(sort: Sort) {
  if (sort.sort_by === "last_commit_at") return sort.order === "desc" ? "Más reciente primero" : "Más antiguo primero";
  return sort.order === "desc" ? "Mayor a menor" : "Menor a mayor";
}

type Status =
  | { kind: "loading" }
  | { kind: "ok"; data: PaginatedRepositories; cachedAt?: number }
  | { kind: "error"; error: FriendlyError };

// Copia local del catálogo (vista inicial y categorías): si el servicio no responde, se muestra la última
// versión guardada en el navegador, con un aviso. Solo guarda datos públicos del catálogo.
const CACHE_KEY = "openbridge:catalogo:v1";
const CATEGORIES_KEY = "openbridge:categorias:v1";

function readCache<T>(key: string): { data: T; savedAt: number } | null {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as { data: T; savedAt: number }) : null;
  } catch {
    return null;
  }
}

function writeCache<T>(key: string, data: T) {
  try {
    localStorage.setItem(key, JSON.stringify({ data, savedAt: Date.now() }));
  } catch {
    // Sin espacio o almacenamiento bloqueado: se sigue sin copia local.
  }
}

/** Fallas en las que conviene mostrar la copia local (no aplica a errores de datos). */
function canUseCache(err: unknown) {
  return err instanceof ApiError && ["offline", "timeout", "unreachable", "server"].includes(err.kind);
}

const savedAtText = (ms: number) =>
  new Date(ms).toLocaleString("es-CL", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });

function toSearchParams(f: Filters, page: number, sort: Sort): SearchParams {
  return {
    q: f.q.trim() || undefined,
    category_id: f.categoryId ?? undefined,
    language: f.language || undefined,
    license: f.license || undefined,
    health_status: f.healthStatus || undefined,
    min_stars: f.minStars || undefined,
    page,
    page_size: PAGE_SIZE,
    ...sort,
  };
}

function catalogError(err: unknown, filtered: boolean): FriendlyError {
  if (err instanceof ApiError && err.kind === "not_found" && filtered) {
    return { title: "Búsqueda no disponible", message: "La búsqueda con filtros no está disponible en este momento. Quita los filtros para ver el catálogo completo.", retry: false };
  }
  return friendlyError(err, "las herramientas");
}

// Pantalla de catálogo (5.5) con buscador y filtros avanzados (5.7) y ficha técnica (5.6).
// Sin filtros usa el listado paginado (2.2); con filtros, la búsqueda (2.3).
export default function Catalog() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  // Lo que realmente se consulta: los filtros ya aplicados y la página.
  const [request, setRequest] = useState<{ filters: Filters; page: number; sort: Sort }>({ filters: EMPTY_FILTERS, page: 1, sort: DEFAULT_SORT });
  const [status, setStatus] = useState<Status>({ kind: "loading" });
  const [openId, setOpenId] = useState<number | null>(null);
  // Cada clic en "Reintentar" vuelve a consultar con los mismos filtros.
  const [attempt, setAttempt] = useState(0);
  const retry = () => setAttempt((n) => n + 1);
  // Repositorios elegidos para comparar: se mantienen al cambiar de página o de filtros.
  const [compare, setCompare] = useState<{ id: number; name: string }[]>([]);

  function toggleCompare(id: number, name: string) {
    setCompare((prev) =>
      prev.some((c) => c.id === id) ? prev.filter((c) => c.id !== id) : prev.length < MAX_COMPARE ? [...prev, { id, name }] : prev,
    );
  }

  useEffect(() => {
    getCategories()
      .then((list) => {
        setCategories(list);
        writeCache(CATEGORIES_KEY, list);
      })
      .catch(() => setCategories(readCache<Category[]>(CATEGORIES_KEY)?.data ?? []));
  }, [attempt]);

  // Espera 300 ms sin cambios antes de consultar (evita una llamada por cada letra) y vuelve a la página 1.
  useEffect(() => {
    const timer = setTimeout(() => {
      setRequest((prev) =>
        JSON.stringify(prev.filters) === JSON.stringify(filters) ? prev : { ...prev, filters, page: 1 },
      );
    }, 300);
    return () => clearTimeout(timer);
  }, [filters]);

  useEffect(() => {
    let cancelled = false;
    const { filters: applied, page, sort } = request;
    const params = toSearchParams(applied, page, sort);
    const filtered = hasFilters(params);
    setStatus({ kind: "loading" });
    const call = filtered ? searchRepositories(params) : listRepositories({ page, page_size: PAGE_SIZE, ...sort });
    // Solo la vista inicial (sin filtros, página 1 y orden por defecto) se guarda y se recupera de la copia local.
    const isDefaultView = !filtered && page === 1 && sort.sort_by === DEFAULT_SORT.sort_by && sort.order === DEFAULT_SORT.order;
    call
      .then((data) => {
        if (cancelled) return;
        setStatus({ kind: "ok", data });
        if (isDefaultView) writeCache(CACHE_KEY, data);
      })
      .catch((err) => {
        if (cancelled) return;
        console.warn(err);
        const cached = isDefaultView && canUseCache(err) ? readCache<PaginatedRepositories>(CACHE_KEY) : null;
        setStatus(cached ? { kind: "ok", data: cached.data, cachedAt: cached.savedAt } : { kind: "error", error: catalogError(err, filtered) });
      });
    return () => {
      cancelled = true;
    };
  }, [request, attempt]);

  const goToPage = (page: number) => setRequest((prev) => ({ ...prev, page }));
  const changeSort = (sort: Sort) => setRequest((prev) => ({ ...prev, sort, page: 1 }));

  const data = status.kind === "ok" ? status.data : null;

  return (
    <section aria-labelledby="resultados" className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[260px_1fr]">
      <CatalogFilters filters={filters} categories={categories} onChange={setFilters} />

      <div className="flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 id="resultados" className="text-sm text-text-muted" aria-live="polite">
            {status.kind === "loading" && "Cargando herramientas…"}
            {status.kind === "error" && "No se pudieron cargar las herramientas"}
            {data && `${data.total} herramienta${data.total === 1 ? "" : "s"}`}
          </h2>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-xs font-medium">
              Ordenar por
              <select
                value={request.sort.sort_by}
                onChange={(e) => changeSort({ ...request.sort, sort_by: e.target.value as SortBy })}
                className="h-10 rounded-xl border border-border bg-card px-3 text-sm text-text"
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </label>
            <button
              type="button"
              onClick={() => changeSort({ ...request.sort, order: request.sort.order === "desc" ? "asc" : "desc" })}
              aria-label={`Orden: ${orderLabel(request.sort)}. Cambiar orden`}
              className="h-10 whitespace-nowrap rounded-xl border border-border bg-card px-3 text-sm text-text hover:bg-surface-hover"
            >
              {request.sort.order === "desc" ? "↓" : "↑"} {orderLabel(request.sort)}
            </button>
          </div>
        </div>

        {status.kind === "error" && <ErrorNotice error={status.error} onRetry={retry} />}

        {status.kind === "ok" && status.cachedAt && (
          <div role="status" className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-status-risk-bg px-4 py-3 text-sm text-status-risk">
            <span>
              No pudimos actualizar el catálogo. Te mostramos los datos de tu última visita ({savedAtText(status.cachedAt)}), que pueden no estar al día.
            </span>
            <button type="button" onClick={retry} className="font-semibold underline underline-offset-2">
              Reintentar
            </button>
          </div>
        )}

        <SlowNotice active={status.kind === "loading"} />

        {data && data.items.length === 0 && (
          <div className="flex flex-col items-center gap-3 rounded-[var(--radius-card)] border border-dashed border-border p-8 text-center text-text-muted">
            <p>No encontramos herramientas con esos filtros.</p>
            <button type="button" onClick={() => setFilters(EMPTY_FILTERS)} className="text-sm font-semibold text-primary hover:underline">
              Limpiar filtros
            </button>
          </div>
        )}

        {status.kind === "loading" && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3" aria-hidden>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-56 animate-pulse rounded-[var(--radius-card)] border border-border bg-card" />
            ))}
          </div>
        )}

        {data && data.items.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {data.items.map((repo) => {
              const selected = compare.some((c) => c.id === repo.id);
              const full = !selected && compare.length >= MAX_COMPARE;
              return (
                <div key={repo.id} className="relative min-w-0">
                  <RepositoryCard repo={repo} onOpen={setOpenId} reserveCorner />
                  <button
                    type="button"
                    onClick={() => toggleCompare(repo.id, repo.name)}
                    disabled={full}
                    aria-pressed={selected}
                    title={full ? `Puedes comparar hasta ${MAX_COMPARE} herramientas` : undefined}
                    className={`absolute right-3 top-3 inline-flex items-center gap-1 rounded-[var(--radius-pill)] border px-3 py-1 text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-50 ${
                      selected ? "border-primary bg-primary text-primary-contrast" : "border-border bg-card text-text hover:border-primary"
                    }`}
                  >
                    {selected ? "✓ Comparar" : "+ Comparar"}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {data && data.total_pages > 1 && (
          <nav aria-label="Paginación" className="flex items-center justify-center gap-3 pt-2 text-sm">
            <button
              type="button"
              onClick={() => goToPage(request.page - 1)}
              disabled={request.page <= 1}
              className="h-11 rounded-[var(--radius-pill)] border border-border px-4 font-semibold hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              ← Anterior
            </button>
            <span className="text-text-muted">
              Página {data.page} de {data.total_pages}
            </span>
            <button
              type="button"
              onClick={() => goToPage(request.page + 1)}
              disabled={request.page >= data.total_pages}
              className="h-11 rounded-[var(--radius-pill)] border border-border px-4 font-semibold hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-50"
            >
              Siguiente →
            </button>
          </nav>
        )}
      </div>

      {compare.length > 0 && (
        <div className="sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-3 rounded-[var(--radius-card)] border border-border bg-card p-4 shadow-lg lg:col-span-2">
          <p className="text-sm">
            <strong>Comparar:</strong> <span className="first-letter:uppercase">{compare.map((c) => c.name).join(", ")}</span>
            {compare.length < 2 && <span className="text-text-muted"> · elige al menos una más</span>}
          </p>
          <div className="flex items-center gap-2">
            <button type="button" onClick={() => setCompare([])} className="h-10 rounded-[var(--radius-pill)] px-4 text-sm font-semibold text-text-muted hover:bg-surface-hover">
              Limpiar
            </button>
            {compare.length >= 2 ? (
              <Link
                href={`/comparar?ids=${compare.map((c) => c.id).join(",")}`}
                className="inline-flex h-10 items-center rounded-[var(--radius-pill)] bg-primary px-5 text-sm font-semibold text-primary-contrast hover:opacity-90"
              >
                Comparar ({compare.length})
              </Link>
            ) : (
              <span className="inline-flex h-10 items-center rounded-[var(--radius-pill)] bg-primary px-5 text-sm font-semibold text-primary-contrast opacity-50">
                Comparar ({compare.length})
              </span>
            )}
          </div>
        </div>
      )}

      <RepositoryDetailDialog repoId={openId} onClose={() => setOpenId(null)} onSelect={setOpenId} />
    </section>
  );
}
