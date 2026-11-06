"use client";

import { useEffect, useState, type ReactNode } from "react";
import type { FriendlyError } from "@/lib/errors";

/** Aviso de error para el usuario: título, explicación y, si corresponde, botón Reintentar. */
export default function ErrorNotice({
  error,
  onRetry,
  children,
  compact = false,
}: {
  error: FriendlyError;
  onRetry?: () => void;
  children?: ReactNode;
  compact?: boolean;
}) {
  return (
    <div
      role="alert"
      className={`flex flex-col items-center gap-3 rounded-[var(--radius-card)] border border-border bg-card text-center shadow-sm ${compact ? "p-5" : "p-8"}`}
    >
      <span aria-hidden="true" className="flex size-11 items-center justify-center rounded-full bg-status-risk-bg text-xl font-bold text-status-risk">
        !
      </span>
      <p className="text-lg font-semibold">{error.title}</p>
      <p className="max-w-md text-text-muted">{error.message}</p>
      <div className="flex flex-wrap justify-center gap-2">
        {error.retry && onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex h-11 items-center rounded-[var(--radius-pill)] bg-primary px-6 font-semibold text-primary-contrast hover:opacity-90"
          >
            Reintentar
          </button>
        )}
        {children}
      </div>
    </div>
  );
}

/** true cuando `active` lleva más de `ms` milisegundos (por ejemplo, una carga que tarda). */
export function useSlow(active: boolean, ms = 6000) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    setSlow(false);
    if (!active) return;
    const timer = setTimeout(() => setSlow(true), ms);
    return () => clearTimeout(timer);
  }, [active, ms]);
  return slow;
}

/** Aviso cuando una carga tarda: el plan gratuito del servidor se "duerme" y tarda en despertar. */
export function SlowNotice({ active }: { active: boolean }) {
  const slow = useSlow(active);
  if (!slow) return null;
  return (
    <p role="status" className="rounded-xl bg-brand-indigo-soft px-4 py-3 text-sm text-[#0f172a]">
      Estamos iniciando el servicio. La primera carga puede tardar hasta un minuto; gracias por esperar.
    </p>
  );
}
