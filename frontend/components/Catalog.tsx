"use client";

import { useEffect, useState } from "react";
import CatalogFilters, { EMPTY_FILTERS, type Filters } from "@/components/CatalogFilters";
import RepositoryCard from "@/components/RepositoryCard";
import RepositoryDetailDialog from "@/components/RepositoryDetailDialog";
import { ApiError, getCategories, hasFilters, listRepositories, searchRepositories } from "@/lib/api";
import type { Category, PaginatedRepositories, SearchParams } from "@/types/api";

const PAGE_SIZE = 12;

type Status = { kind: "loading" } | { kind: "ok"; data: PaginatedRepositories } | { kind: "error"; message: string };

function toSearchParams(f: Filters, page: number): SearchParams {
  return {
    q: f.q.trim() || undefined,
    category_id: f.categoryId ?? undefined,
    language: f.language || undefined,
    license: f.license || undefined,
    health_status: f.healthStatus || undefined,
    min_stars: f.minStars || undefined,
    page,
    page_size: PAGE_SIZE,
  };
}

function errorMessage(err: unknown, filtered: boolean) {
  if (err instanceof ApiError && err.status === 404 && filtered) {
    return "La búsqueda con filtros todavía no está disponible en la API. Quita los filtros para ver el catálogo completo.";
  }
  if (err instanceof ApiError && err.status === 0) return "No pudimos conectar con la API. Revisa que el backend esté corriendo.";
  return "Ocurrió un error al cargar los repositorios. Intenta de nuevo en unos minutos.";
}

// Pantalla de catálogo (5.5) con buscador y filtros avanzados (5.7) y ficha técnica (5.6).
// Sin filtros usa el listado paginado (2.2); con filtros, la búsqueda (2.3).
export default function Catalog() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  // Lo que realmente se consulta: los filtros ya aplicados y la página.
  const [request, setRequest] = useState<{ filters: Filters; page: number }>({ filters: EMPTY_FILTERS, page: 1 });
  const [status, setStatus] = useState<Status>({ kind: "loading" });
  const [openId, setOpenId] = useState<number | null>(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  // Espera 300 ms sin cambios antes de consultar (evita una llamada por cada letra) y vuelve a la página 1.
  useEffect(() => {
    const timer = setTimeout(() => {
      setRequest((prev) =>
        JSON.stringify(prev.filters) === JSON.stringify(filters) ? prev : { filters, page: 1 },
      );
    }, 300);
    return () => clearTimeout(timer);
  }, [filters]);

  useEffect(() => {
    let cancelled = false;
    const { filters: applied, page } = request;
    const params = toSearchParams(applied, page);
    const filtered = hasFilters(params);
    setStatus({ kind: "loading" });
    const call = filtered ? searchRepositories(params) : listRepositories({ page, page_size: PAGE_SIZE });
    call
      .then((data) => !cancelled && setStatus({ kind: "ok", data }))
      .catch((err) => !cancelled && setStatus({ kind: "error", message: errorMessage(err, filtered) }));
    return () => {
      cancelled = true;
    };
  }, [request]);

  const goToPage = (page: number) => setRequest((prev) => ({ ...prev, page }));

  const data = status.kind === "ok" ? status.data : null;

  return (
    <section aria-labelledby="resultados" className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[260px_1fr]">
      <CatalogFilters filters={filters} categories={categories} onChange={setFilters} />

      <div className="flex flex-col gap-4">
        <h2 id="resultados" className="text-sm text-text-muted" aria-live="polite">
          {status.kind === "loading" && "Cargando herramientas…"}
          {status.kind === "error" && "No se pudieron cargar las herramientas"}
          {data && `${data.total} herramienta${data.total === 1 ? "" : "s"}`}
        </h2>

        {status.kind === "error" && (
          <p role="alert" className="rounded-[var(--radius-card)] border border-dashed border-border p-8 text-center text-text-muted">
            {status.message}
          </p>
        )}

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
            {data.items.map((repo) => (
              <RepositoryCard key={repo.id} repo={repo} onOpen={setOpenId} />
            ))}
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

      <RepositoryDetailDialog repoId={openId} onClose={() => setOpenId(null)} onSelect={setOpenId} />
    </section>
  );
}
