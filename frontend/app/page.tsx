import Catalog from "@/components/Catalog";
import { USE_MOCK } from "@/lib/api";

// Pantalla de catálogo (5.5), según el prototipo de diseño (5.3).
export default function HomePage() {
  return (
    <div className="flex flex-col gap-6">
      <section className="flex flex-col gap-2">
        <h1 className="max-w-3xl text-3xl font-bold leading-tight text-text sm:text-4xl">
          El camino corto a tu stack open source
        </h1>
        <p className="max-w-2xl text-text-muted">Encuentra la pieza correcta para tu stack y mira cómo integrarla.</p>
      </section>
      {USE_MOCK && (
        <p className="rounded-xl bg-surface-muted px-4 py-2 text-xs text-text-muted">
          Datos de ejemplo: las métricas y el health score no son reales. Para usar la API, cambia NEXT_PUBLIC_USE_MOCK a false en .env.local.
        </p>
      )}
      <Catalog />
    </div>
  );
}
