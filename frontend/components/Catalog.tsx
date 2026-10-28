"use client";

import { useEffect, useState } from "react";
import RepositoryCard from "@/components/RepositoryCard";
import { getCategories, searchRepositories } from "@/lib/api";
import type { Category, RepositoryListItem } from "@/types/api";

// Esqueleto del catálogo: búsqueda por texto y filtro por categoría.
// Los filtros completos (5.7) y la pantalla definitiva (5.5) se construyen sobre esta base.
export default function Catalog() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [repos, setRepos] = useState<RepositoryListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [state, setState] = useState<"loading" | "ok" | "error">("loading");

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setState("loading");
      searchRepositories({ q: q || undefined, category_id: categoryId === "" ? undefined : categoryId, page: 1, page_size: 12 })
        .then((data) => {
          setRepos(data.items);
          setTotal(data.total);
          setState("ok");
        })
        .catch(() => setState("error"));
    }, 300);
    return () => clearTimeout(timer);
  }, [q, categoryId]);

  return (
    <section aria-labelledby="catalogo-titulo" className="flex flex-col gap-6">
      <div className="flex flex-col gap-3 sm:flex-row">
        <label className="flex flex-1 flex-col gap-1 text-sm font-medium">
          Buscar
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ej.: autenticación, base vectorial, pagos"
            className="h-11 rounded-xl border border-border bg-card px-4 text-text placeholder:text-text-muted"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium sm:w-72">
          Categoría
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value === "" ? "" : Number(e.target.value))}
            className="h-11 rounded-xl border border-border bg-card px-3 text-text"
          >
            <option value="">Todas las categorías</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name} ({c.repositories_count})</option>
            ))}
          </select>
        </label>
      </div>

      <h2 id="catalogo-titulo" className="text-sm text-text-muted" aria-live="polite">
        {state === "loading" && "Cargando repositorios…"}
        {state === "error" && "No pudimos conectar con la API. Intenta de nuevo en unos minutos."}
        {state === "ok" && `${total} repositorio${total === 1 ? "" : "s"}`}
      </h2>

      {state === "ok" && repos.length === 0 && (
        <p className="rounded-[var(--radius-card)] border border-dashed border-border p-8 text-center text-text-muted">
          No encontramos repositorios con esos filtros.
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {repos.map((repo) => (
          <RepositoryCard key={repo.id} repo={repo} />
        ))}
      </div>
    </section>
  );
}
