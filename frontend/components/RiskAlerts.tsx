import type { RepositoryAlert } from "@/types/api";

// Alertas de riesgo por licencia y mantenimiento (9.3). Siempre con texto, para no depender solo del color.

const ICON: Record<string, string> = { license: "⚖", maintenance: "⚠" };

/** Versión compacta para la tarjeta del catálogo: una etiqueta por alerta, con el detalle al pasar el cursor. */
export function AlertBadges({ alerts }: { alerts?: RepositoryAlert[] }) {
  if (!alerts?.length) return null;
  return (
    <span className="flex flex-wrap gap-1.5" aria-label={`${alerts.length} ${alerts.length === 1 ? "alerta de riesgo" : "alertas de riesgo"}`}>
      {alerts.map((a) => (
        <span
          key={`${a.type}-${a.title}`}
          title={a.message}
          className="inline-flex items-center gap-1 rounded-md bg-status-risk-bg px-2 py-0.5 text-xs font-semibold text-status-risk"
        >
          <span aria-hidden="true">{ICON[a.type] ?? "⚠"}</span>
          {a.title}
        </span>
      ))}
    </span>
  );
}

/** Versión completa para la ficha y el asistente: título y explicación de cada alerta. */
export function AlertList({ alerts, compact = false }: { alerts?: RepositoryAlert[]; compact?: boolean }) {
  if (!alerts?.length) return null;
  return (
    <ul className={`flex flex-col ${compact ? "gap-1.5" : "gap-2"}`} aria-label="Alertas de riesgo">
      {alerts.map((a) => (
        <li
          key={`${a.type}-${a.title}`}
          className={`flex gap-2 rounded-xl border border-status-risk/30 bg-status-risk-bg text-status-risk ${compact ? "px-3 py-2 text-xs" : "px-4 py-3 text-sm"}`}
        >
          <span aria-hidden="true">{ICON[a.type] ?? "⚠"}</span>
          <span>
            {/* La API suele empezar el mensaje con el título: en ese caso solo se destaca, sin repetirlo. */}
            {a.message.startsWith(a.title) ? (
              <>
                <strong>{a.title}</strong>
                {a.message.slice(a.title.length)}
              </>
            ) : (
              <>
                <strong>{a.title}.</strong> {a.message}
              </>
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}
