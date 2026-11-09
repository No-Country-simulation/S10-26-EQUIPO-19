"use client";

import { useState } from "react";
import ErrorNotice, { SlowNotice } from "@/components/ErrorNotice";
import { ApiError, COMPOSE_ENABLED, generateCompose } from "@/lib/api";
import { friendlyError, type FriendlyError } from "@/lib/errors";
import type { ComposeResponse } from "@/types/api";

// docker-compose de arranque (9.2): arma el archivo con las herramientas del stack recomendado,
// usando solo imágenes oficiales del inventario. Las librerías y las herramientas sin datos Docker
// se informan aparte.

type Status = { kind: "idle" } | { kind: "loading" } | { kind: "ok"; data: ComposeResponse } | { kind: "error"; error: FriendlyError };

function composeError(err: unknown): FriendlyError {
  // Validaciones del servidor (cantidad o formato de las herramientas): sus textos ya son para el usuario.
  if (err instanceof ApiError && err.kind === "invalid" && err.detail) {
    return { title: "No pudimos armar el archivo", message: err.detail, retry: false };
  }
  if (err instanceof ApiError && (err.kind === "not_found" || err.kind === "unavailable")) {
    return { title: "Función no disponible", message: "La generación del docker-compose no está disponible en este momento. Inténtalo más tarde.", retry: false };
  }
  return friendlyError(err, "el docker-compose");
}

function download(data: ComposeResponse) {
  const url = URL.createObjectURL(new Blob([data.content], { type: "text/yaml;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = data.filename || "docker-compose.yml";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export default function ComposePanel({ fullNames, onGenerated }: { fullNames: string[]; onGenerated?: (data: ComposeResponse) => void }) {
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [copied, setCopied] = useState(false);

  async function generate() {
    setStatus({ kind: "loading" });
    try {
      const data = await generateCompose(fullNames);
      setStatus({ kind: "ok", data });
      // El chat reutiliza este mismo archivo en la descarga de la propuesta.
      onGenerated?.(data);
    } catch (err) {
      console.warn(err);
      setStatus({ kind: "error", error: composeError(err) });
    }
  }

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  if (!COMPOSE_ENABLED || fullNames.length === 0) return null;

  return (
    <section aria-label="docker-compose de arranque" className="flex flex-col gap-3">
      {status.kind !== "ok" && (
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void generate()}
            disabled={status.kind === "loading"}
            className="inline-flex h-10 items-center gap-2 rounded-[var(--radius-pill)] bg-primary px-4 text-sm font-semibold text-primary-contrast hover:opacity-90 disabled:opacity-50"
          >
            {status.kind === "loading" ? "Generando…" : "Generar docker-compose de arranque"}
          </button>
          <span className="text-sm text-text-muted">Levanta las herramientas del stack en tu computador con un solo comando.</span>
        </div>
      )}

      <SlowNotice active={status.kind === "loading"} />
      {status.kind === "error" && <ErrorNotice error={status.error} compact onRetry={() => void generate()} />}

      {status.kind === "ok" && (
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-semibold">docker-compose de arranque</h2>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => void copy(status.data.content)}
                className="inline-flex h-9 items-center rounded-[var(--radius-pill)] border border-border px-3 text-sm font-semibold hover:border-primary hover:bg-surface-hover"
              >
                {copied ? "✓ Copiado" : "Copiar"}
              </button>
              <button
                type="button"
                onClick={() => download(status.data)}
                className="inline-flex h-9 items-center rounded-[var(--radius-pill)] bg-primary px-3 text-sm font-semibold text-primary-contrast hover:opacity-90"
              >
                ↓ Descargar {status.data.filename || "docker-compose.yml"}
              </button>
            </div>
          </div>

          {status.data.services.length > 0 ? (
            <pre className="max-h-80 overflow-auto rounded-xl bg-[#0f172a] p-4 text-xs leading-relaxed text-[#e2e8f0]">
              <code>{status.data.content}</code>
            </pre>
          ) : (
            <p className="rounded-xl bg-surface-hover px-4 py-3 text-sm">Ninguna herramienta de este stack tiene todavía una imagen Docker oficial revisada en el catálogo.</p>
          )}

          {status.data.warnings.map((w) => (
            <p key={w} className="rounded-xl bg-status-risk-bg px-4 py-2 text-sm text-status-risk">
              ⚠ {w}
            </p>
          ))}

          {status.data.skipped.length > 0 && (
            <div className="text-sm">
              <p className="font-semibold">No incluidas como servicio</p>
              <ul className="mt-1 flex flex-col gap-1 text-text-muted">
                {status.data.skipped.map((s) => (
                  <li key={s.full_name}>
                    <span className="font-semibold text-text">{s.full_name}</span>: {s.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="text-xs text-text-muted">
            Para levantarlo: guarda el archivo, reemplaza cada &lt;secreto&gt; y ejecuta <code className="rounded bg-surface-hover px-1">docker compose up -d</code>.
          </p>
        </div>
      )}
    </section>
  );
}
