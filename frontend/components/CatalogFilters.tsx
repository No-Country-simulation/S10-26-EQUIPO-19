"use client";

import { useState } from "react";
import { HEALTH_FILTER_LABEL, HEALTH_STATUSES, LANGUAGES, LICENSES, STARS_MAX, STARS_STEP } from "@/lib/filters";
import { compactNumber } from "@/lib/format";
import type { Category, HealthStatus } from "@/types/api";

export type Filters = {
  q: string;
  categoryId: number | null;
  language: string;
  license: string;
  healthStatus: HealthStatus | "";
  minStars: number;
};

export const EMPTY_FILTERS: Filters = { q: "", categoryId: null, language: "", license: "", healthStatus: "", minStars: 0 };

const VISIBLE_CATEGORIES = 8;

const fieldClass = "h-10 w-full rounded-xl border border-border bg-surface px-3 text-sm text-text";

// Buscador por texto y filtros avanzados (5.7): los 5 filtros de la consigna más estrellas mínimas.
export default function CatalogFilters({
  filters,
  categories,
  onChange,
}: {
  filters: Filters;
  categories: Category[];
  onChange: (next: Filters) => void;
}) {
  const [showAll, setShowAll] = useState(false);
  const set = <K extends keyof Filters>(key: K, value: Filters[K]) => onChange({ ...filters, [key]: value });
  const active = JSON.stringify(filters) !== JSON.stringify(EMPTY_FILTERS);

  // Primero las categorías con repositorios; la seleccionada siempre queda visible.
  const sorted = [...categories].sort((a, b) => (b.repositories_count ?? 0) - (a.repositories_count ?? 0));
  const visible = showAll ? sorted : sorted.slice(0, VISIBLE_CATEGORIES);
  const selected = categories.find((c) => c.id === filters.categoryId);
  if (selected && !visible.includes(selected)) visible.push(selected);

  return (
    <aside aria-label="Filtros del catálogo" className="flex flex-col gap-4 rounded-[var(--radius-card)] border border-border bg-card p-4">
      <label className="flex flex-col gap-1.5 text-xs font-medium">
        Buscar
        <input
          type="search"
          value={filters.q}
          onChange={(e) => set("q", e.target.value)}
          placeholder="Nombre, descripción o tema"
          className={`${fieldClass} placeholder:text-text-muted`}
        />
      </label>

      <fieldset className="flex flex-col gap-1.5">
        <legend className="mb-1.5 text-xs font-medium">Categoría</legend>
        <div className="flex flex-wrap gap-1.5">
          <CategoryChip label="Todas" pressed={filters.categoryId === null} onClick={() => set("categoryId", null)} />
          {visible.map((c) => (
            <CategoryChip
              key={c.id}
              label={c.name}
              count={c.repositories_count}
              pressed={filters.categoryId === c.id}
              onClick={() => set("categoryId", filters.categoryId === c.id ? null : c.id)}
            />
          ))}
        </div>
        {categories.length > VISIBLE_CATEGORIES && (
          <button type="button" onClick={() => setShowAll(!showAll)} className="self-start text-xs font-semibold text-primary hover:underline">
            {showAll ? "Ver menos" : `Ver las ${categories.length} categorías`}
          </button>
        )}
      </fieldset>

      <label className="flex flex-col gap-1.5 text-xs font-medium">
        Lenguaje
        <select value={filters.language} onChange={(e) => set("language", e.target.value)} className={fieldClass}>
          <option value="">Todos</option>
          {LANGUAGES.map((l) => (
            <option key={l}>{l}</option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1.5 text-xs font-medium">
        Licencia
        <select value={filters.license} onChange={(e) => set("license", e.target.value)} className={fieldClass}>
          <option value="">Todas</option>
          {LICENSES.map((l) => (
            <option key={l}>{l}</option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1.5 text-xs font-medium">
        {HEALTH_FILTER_LABEL}
        <select
          value={filters.healthStatus}
          onChange={(e) => set("healthStatus", e.target.value as HealthStatus | "")}
          className={fieldClass}
        >
          <option value="">Todos</option>
          {HEALTH_STATUSES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1.5 text-xs font-medium">
        <span>
          Estrellas mínimas: <strong>{filters.minStars === 0 ? "sin mínimo" : compactNumber(filters.minStars)}</strong>
        </span>
        <input
          type="range"
          min={0}
          max={STARS_MAX}
          step={STARS_STEP}
          value={filters.minStars}
          onChange={(e) => set("minStars", Number(e.target.value))}
          className="w-full accent-[var(--primary)]"
        />
      </label>

      <button
        type="button"
        onClick={() => onChange(EMPTY_FILTERS)}
        disabled={!active}
        className="h-10 rounded-[var(--radius-pill)] border border-border text-sm font-semibold hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-50"
      >
        Limpiar filtros
      </button>
    </aside>
  );
}

function CategoryChip({ label, count, pressed, onClick }: { label: string; count?: number | null; pressed: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={onClick}
      className={`rounded-[var(--radius-pill)] border px-3 py-1 text-xs font-medium transition-colors ${
        pressed ? "border-brand-pink-deep bg-brand-pink-deep text-white" : "border-border bg-card text-text hover:bg-surface-hover"
      }`}
    >
      {label}
      {typeof count === "number" && <span className={pressed ? "text-white/80" : "text-text-muted"}> · {count}</span>}
    </button>
  );
}
