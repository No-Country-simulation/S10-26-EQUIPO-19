import type { HealthStatus } from "@/types/api";

const STYLES: Record<HealthStatus | "Sin datos", string> = {
  Activo: "bg-status-active-bg text-status-active",
  "En riesgo": "bg-status-risk-bg text-status-risk",
  Abandonado: "bg-status-abandoned-bg text-status-abandoned",
  "Sin datos": "bg-status-unknown-bg text-status-unknown",
};

// Nivel de mantenimiento: siempre con texto, para no depender solo del color.
export default function HealthBadge({ status, score }: { status: HealthStatus | null; score?: number }) {
  const label = status ?? "Sin datos";
  return (
    <span className={`inline-flex items-center gap-1 rounded-[var(--radius-pill)] px-3 py-1 text-xs font-semibold ${STYLES[label]}`}>
      {label}
      {score !== undefined && <span className="font-normal">· {score}/100</span>}
    </span>
  );
}
