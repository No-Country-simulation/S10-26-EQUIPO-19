export const metadata = { title: "Asistente · OpenBridge" };

// Esqueleto de la pantalla del asistente. La interfaz de chat es la tarea 5.9
// y el endpoint del asistente, la 4.4.
export default function AssistantPage() {
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-3xl font-bold">Asistente de arquitectura</h1>
      <p className="max-w-2xl text-text-muted">
        Cuéntame qué estás construyendo y te propongo un stack open source con sus conexiones.
      </p>
      <p className="rounded-xl bg-brand-indigo-soft p-4 text-sm text-brand-indigo-strong dark:bg-surface-muted dark:text-text-muted">
        Pantalla en construcción: el chat y el diagrama de la arquitectura se suman en el Sprint 3.
      </p>
    </div>
  );
}
