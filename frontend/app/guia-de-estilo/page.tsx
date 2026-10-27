import HealthBadge from "@/components/HealthBadge";

export const metadata = { title: "Guía de estilo · OpenBridge" };

const BRAND = [
  { name: "Rosa", token: "brand-pink", hex: "#FC0395", cls: "bg-brand-pink" },
  { name: "Índigo", token: "brand-indigo", hex: "#6366F1", cls: "bg-brand-indigo" },
  { name: "Cian", token: "brand-cyan", hex: "#07BCEB", cls: "bg-brand-cyan" },
  { name: "Turquesa", token: "brand-teal", hex: "#1BDBC5", cls: "bg-brand-teal" },
  { name: "Pizarra", token: "brand-slate", hex: "#64748B", cls: "bg-brand-slate" },
  { name: "Rosa suave", token: "brand-pink-soft", hex: "#FFE4F3", cls: "bg-brand-pink-soft" },
  { name: "Índigo suave", token: "brand-indigo-soft", hex: "#EEF0FE", cls: "bg-brand-indigo-soft" },
];

const SEMANTIC = [
  { token: "surface", use: "Fondo de la página", cls: "bg-surface" },
  { token: "surface-muted", use: "Fondos secundarios y hover", cls: "bg-surface-muted" },
  { token: "card", use: "Tarjetas y paneles", cls: "bg-card" },
  { token: "border", use: "Bordes y separadores", cls: "bg-border" },
  { token: "text", use: "Texto principal", cls: "bg-text" },
  { token: "text-muted", use: "Texto secundario", cls: "bg-text-muted" },
  { token: "primary", use: "Botones, enlaces y foco", cls: "bg-primary" },
  { token: "accent", use: "Acentos y etiquetas destacadas", cls: "bg-accent" },
];

export default function StyleGuidePage() {
  return (
    <div className="flex flex-col gap-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold">Guía de estilo y design tokens</h1>
        <p className="max-w-2xl text-text-muted">
          Vista viva de los tokens definidos en <code className="font-mono text-sm">app/globals.css</code>. Las reglas
          de uso están en <code className="font-mono text-sm">docs/guia-de-estilo.md</code>. Cambia a modo oscuro para ver
          cómo se adaptan los colores semánticos.
        </p>
      </header>

      <section className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold">Paleta de marca</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-7">
          {BRAND.map((c) => (
            <div key={c.token} className="overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
              <div className={`h-16 ${c.cls}`} />
              <div className="p-3 text-xs">
                <p className="font-semibold">{c.name}</p>
                <p className="text-text-muted">{c.hex}</p>
                <p className="font-mono text-text-muted">{c.token}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold">Colores semánticos (claro / oscuro)</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {SEMANTIC.map((c) => (
            <div key={c.token} className="flex items-center gap-3 rounded-xl border border-border bg-card p-3">
              <div className={`h-10 w-10 shrink-0 rounded-lg border border-border ${c.cls}`} />
              <div className="text-sm">
                <p className="font-mono font-semibold">{c.token}</p>
                <p className="text-text-muted">{c.use}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold">Tipografía · Poppins</h2>
        <div className="flex flex-col gap-2 rounded-[var(--radius-card)] border border-border bg-card p-5">
          <p className="text-4xl font-bold">Título principal · 36 px · 700</p>
          <p className="text-2xl font-semibold">Título de sección · 24 px · 600</p>
          <p className="text-lg font-semibold">Subtítulo · 18 px · 600</p>
          <p className="text-base">Texto de cuerpo · 16 px · 400</p>
          <p className="text-sm text-text-muted">Texto secundario · 14 px · 400</p>
          <p className="font-mono text-sm">Código · monoespaciada · 14 px</p>
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold">Componentes base</h2>
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" className="h-11 rounded-[var(--radius-pill)] bg-primary px-5 font-semibold text-primary-contrast hover:opacity-90">
            Botón principal
          </button>
          <button type="button" className="h-11 rounded-[var(--radius-pill)] border border-border px-5 font-semibold hover:bg-surface-muted">
            Botón secundario
          </button>
          <a href="#" className="font-semibold text-primary hover:underline">Enlace</a>
        </div>
        <div className="flex flex-wrap gap-2">
          <HealthBadge status="Activo" score={91} />
          <HealthBadge status="En riesgo" score={48} />
          <HealthBadge status="Abandonado" score={12} />
          <HealthBadge status={null} />
        </div>
      </section>
    </div>
  );
}
