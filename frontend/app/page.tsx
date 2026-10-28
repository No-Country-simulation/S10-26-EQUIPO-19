import Catalog from "@/components/Catalog";

export default function HomePage() {
  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-3">
        <p className="text-sm font-semibold uppercase tracking-wider text-accent">Catálogo open source</p>
        <h1 className="max-w-3xl text-3xl font-bold leading-tight text-text sm:text-4xl">
          Encuentra herramientas open source curadas para tu próximo proyecto
        </h1>
        <p className="max-w-2xl text-text-muted">
          Repositorios revisados, con su nivel de mantenimiento e ideas de integración, para que el equipo no invierta
          horas investigando ni adopte librerías abandonadas.
        </p>
      </section>
      <Catalog />
    </div>
  );
}
