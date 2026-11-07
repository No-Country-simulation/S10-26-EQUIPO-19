"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import ArchitectureMap from "@/components/ArchitectureMap";
import ComposePanel from "@/components/ComposePanel";
import HealthBadge from "@/components/HealthBadge";
import Markdown from "@/components/Markdown";
import RepositoryDetailDialog from "@/components/RepositoryDetailDialog";
import { AlertList } from "@/components/RiskAlerts";
import ErrorNotice, { SlowNotice } from "@/components/ErrorNotice";
import { ApiError, askAssistant } from "@/lib/api";
import { friendlyError, type FriendlyError } from "@/lib/errors";
import { downloadProposal } from "@/lib/exportProposal";
import type { ArchitectureComponent, ChatMessage, ChatResponse } from "@/types/api";

// Interfaz del asistente consultor (5.9): el usuario describe su negocio y recibe un stack
// open source justificado, con sus conexiones, alertas de riesgo y fuentes del catálogo (4.4).

const MAX_LENGTH = 2000;

// Casos de negocio del inventario, para probar el asistente con un clic.
const EXAMPLES = [
  "Estoy construyendo una tienda B2B de logística. Necesito gestionar cuentas de empresas, pagos e inventario, además de planificar rutas de reparto, hacer seguimiento de la flota, enviar avisos a los clientes y automatizar procesos operativos.",
  "Una plataforma para que clínicas agenden citas con pago en línea.",
];

type Turn = { role: "user"; content: string } | { role: "assistant"; content: string; response: ChatResponse };

// QA N3 vid-3 (opción A): la última conversación se guarda solo en este navegador (localStorage).
const STORAGE_KEY = "openbridge.asistente.conversacion.v1";
const MAX_SAVED_TURNS = 20;

function isTurn(value: unknown): value is Turn {
  if (!value || typeof value !== "object") return false;
  const t = value as Record<string, unknown>;
  if (typeof t.content !== "string") return false;
  if (t.role === "user") return true;
  return t.role === "assistant" && !!t.response && typeof t.response === "object";
}

/** Recorta a los últimos mensajes y evita empezar con una respuesta sin su pregunta. */
function trimTurns(turns: Turn[]): Turn[] {
  const recent = turns.slice(-MAX_SAVED_TURNS);
  return recent[0]?.role === "assistant" ? recent.slice(1) : recent;
}

function loadTurns(): Turn[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed) || !parsed.every(isTurn)) return [];
    const turns = trimTurns(parsed);
    // Una pregunta sin respuesta (se cerró la página mientras esperaba) no se restaura.
    return turns[turns.length - 1]?.role === "user" ? turns.slice(0, -1) : turns;
  } catch {
    return [];
  }
}

function saveTurns(turns: Turn[]) {
  try {
    if (turns.length === 0) window.localStorage.removeItem(STORAGE_KEY);
    else window.localStorage.setItem(STORAGE_KEY, JSON.stringify(trimTurns(turns)));
  } catch {
    // Almacenamiento lleno o bloqueado (p. ej., navegación privada): la conversación sigue en pantalla.
  }
}

function assistantError(err: unknown): FriendlyError {
  if (err instanceof ApiError && err.kind === "invalid") {
    return { title: "Revisa tu consulta", message: "La consulta no es válida. Revisa que no supere los 2000 caracteres.", retry: false };
  }
  if (err instanceof ApiError && (err.kind === "not_found" || err.kind === "unavailable")) {
    return { title: "Asistente no disponible", message: "El asistente no está disponible en este momento. Inténtalo más tarde.", retry: false };
  }
  return friendlyError(err, "la recomendación");
}

export default function AssistantChat() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ error: FriendlyError; message: string; history: ChatMessage[] } | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const [restored, setRestored] = useState(false);

  // Se lee después de montar para que el HTML del servidor y el del navegador coincidan.
  useEffect(() => {
    setTurns(loadTurns());
    setRestored(true);
  }, []);

  useEffect(() => {
    if (restored) saveTurns(turns);
  }, [turns, restored]);

  function newConversation() {
    setTurns([]);
    setError(null);
    setInput("");
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns, loading]);

  async function send(text: string, retryHistory?: ChatMessage[]) {
    const message = text.trim();
    if (!message || loading) return;
    // Al reintentar, la pregunta ya está en pantalla: se reenvía con el mismo historial.
    const history: ChatMessage[] = retryHistory ?? turns.map((t) => ({ role: t.role, content: t.content }));
    if (!retryHistory) setTurns((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setError(null);
    setLoading(true);
    try {
      const response = await askAssistant(message, history);
      setTurns((prev) => [...prev, { role: "assistant", content: response.answer, response }]);
    } catch (err) {
      console.warn(err);
      setError({ error: assistantError(err), message, history });
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void send(input);
  }

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold">Hola, soy Toby 👋</h1>
        <p className="max-w-2xl text-text-muted">
          Soy el asistente de OpenBridge. Cuéntame qué quieres construir, aunque no sepas qué tecnologías necesitas, y te propongo un stack open source con sus conexiones, solo con herramientas de nuestro catálogo revisadas a diario.
        </p>
      </header>

      <section aria-label="Conversación" aria-live="polite" className="flex flex-col gap-4">
        {turns.length === 0 && (
          <div className="flex flex-col gap-3 rounded-[var(--radius-card)] border border-border bg-card p-5">
            <p className="text-text-muted">Por ejemplo:</p>
            <div className="flex flex-col gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  type="button"
                  onClick={() => void send(ex)}
                  className="rounded-xl border border-border px-4 py-3 text-left text-sm hover:border-primary hover:bg-surface-hover"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {turns.map((t, i) =>
          t.role === "user" ? (
            <div key={i} className="max-w-[85%] self-end rounded-2xl bg-primary px-4 py-3 text-primary-contrast">
              {t.content}
            </div>
          ) : (
            <AssistantAnswer
              key={i}
              question={turns[i - 1]?.role === "user" ? turns[i - 1].content : null}
              response={t.response}
              onOpen={setOpenId}
              onAsk={(q) => void send(q)}
              disabled={loading}
            />
          ),
        )}

        {loading && (
          <p className="self-start rounded-2xl border border-border bg-card px-4 py-3 text-text-muted" role="status">
            Buscando en el catálogo y armando la recomendación…
          </p>
        )}
        {loading && <SlowNotice active={loading} />}
        {error && (
          <div className="self-stretch">
            <ErrorNotice error={error.error} compact onRetry={() => void send(error.message, error.history)} />
          </div>
        )}
        <div ref={endRef} />
      </section>

      <form onSubmit={onSubmit} className="sticky bottom-0 flex flex-col gap-2 border-t border-border bg-surface py-3">
        <label htmlFor="consulta" className="sr-only">
          Describe tu negocio o producto
        </label>
        <div className="flex gap-2">
          <textarea
            id="consulta"
            value={input}
            onChange={(e) => setInput(e.target.value.slice(0, MAX_LENGTH))}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send(input);
              }
            }}
            rows={2}
            maxLength={MAX_LENGTH}
            placeholder="Ej.: una app de delivery de comida con repartidores en tiempo real"
            className="min-h-12 flex-1 resize-y rounded-2xl border border-border bg-card px-4 py-3 text-text"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="h-12 self-end rounded-[var(--radius-pill)] bg-primary px-6 font-semibold text-primary-contrast hover:opacity-90 disabled:opacity-50"
          >
            Enviar
          </button>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-xs text-text-muted">
          {turns.length > 0 ? (
            <span className="flex flex-wrap items-center gap-x-3 gap-y-1">
              <button
                type="button"
                onClick={newConversation}
                disabled={loading}
                className="font-semibold text-primary hover:underline disabled:opacity-50"
              >
                + Nueva conversación
              </button>
              <span>Tu conversación se guarda solo en este navegador. Descarga la propuesta si quieres conservarla.</span>
            </span>
          ) : (
            <span />
          )}
          <span>
            {input.length}/{MAX_LENGTH}
          </span>
        </div>
      </form>

      <RepositoryDetailDialog repoId={openId} onClose={() => setOpenId(null)} onSelect={setOpenId} />
    </div>
  );
}

function AssistantAnswer({
  question,
  response,
  onOpen,
  onAsk,
  disabled,
}: {
  question: string | null;
  response: ChatResponse;
  onOpen: (id: number) => void;
  onAsk: (q: string) => void;
  disabled: boolean;
}) {
  const components = response.architecture?.components ?? [];
  const connections = response.architecture?.connections ?? [];
  const byKey = new Map(components.map((c) => [c.key, c]));
  const name = (key: string) => byKey.get(key)?.full_name.split("/")[1] ?? key;

  return (
    <article className="flex max-w-full flex-col gap-4 self-start rounded-[var(--radius-card)] border border-border bg-card p-5">
      <div className="flex flex-col gap-2 leading-relaxed"><Markdown text={response.answer} /></div>

      {components.length > 0 && (
        <section aria-label="Stack recomendado" className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold">Stack recomendado</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {components.map((c) => (
              <ComponentCard key={c.key} component={c} onOpen={onOpen} />
            ))}
          </div>
        </section>
      )}

      <ArchitectureMap components={components} connections={connections} onOpen={onOpen} />

      {connections.length > 0 && (
        <section aria-label="Cómo se conectan" className="flex flex-col gap-2">
          <h2 className="text-lg font-semibold">Cómo se conectan</h2>
          <ul className="flex flex-col gap-2">
            {connections.map((cn, i) => (
              <li key={i} className="flex flex-col gap-1 rounded-xl bg-surface-hover px-4 py-3 text-sm">
                <span className="font-semibold">
                  <span className="first-letter:uppercase">{name(cn.from)}</span> → <span className="first-letter:uppercase">{name(cn.to)}</span>
                </span>
                <span className="text-text-muted">{cn.label}</span>
                <span className="text-xs font-semibold text-text-muted">
                  {cn.verified ? `Idea de integración del catálogo${cn.integration_code ? ` · ${cn.integration_code}` : ""}` : "Conexión sugerida por el asistente"}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {response.sources.length > 0 && (
        <section aria-label="Fuentes" className="flex flex-col gap-1 text-sm">
          <h2 className="font-semibold">Fuentes del catálogo</h2>
          <ul className="flex flex-wrap gap-x-4 gap-y-1">
            {response.sources.map((s) => (
              <li key={s.repository_id}>
                <a href={s.url} target="_blank" rel="noreferrer" className="font-semibold text-primary hover:underline">
                  {s.full_name} ↗
                </a>{" "}
                <span className="text-text-muted">· {Math.round(s.relevance_score * 100)} % de coincidencia</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {response.suggested_questions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {response.suggested_questions.map((q) => (
            <button
              key={q}
              type="button"
              disabled={disabled}
              onClick={() => onAsk(q)}
              className="rounded-[var(--radius-pill)] border border-border px-3 py-1.5 text-sm hover:border-primary hover:bg-surface-hover disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* vid-1 (QA N3): con varias herramientas y sin conexiones es una comparación de alternativas, no un stack para levantar junto. */}
      {(components.length <= 1 || connections.length > 0) && (
        <ComposePanel fullNames={components.map((c) => c.full_name)} />
      )}

      <div className="flex justify-end border-t border-border pt-3">
        <button
          type="button"
          onClick={() => downloadProposal(question, response)}
          className="inline-flex h-10 items-center gap-2 rounded-[var(--radius-pill)] border border-border px-4 text-sm font-semibold hover:border-primary hover:bg-surface-hover"
        >
          ↓ Descargar propuesta (.md)
        </button>
      </div>
    </article>
  );
}

function ComponentCard({ component: c, onOpen }: { component: ArchitectureComponent; onOpen: (id: number) => void }) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <button
          type="button"
          onClick={() => onOpen(c.repository_id)}
          className="text-left font-display font-semibold text-primary hover:underline"
          aria-label={`Ver la ficha de ${c.full_name}`}
        >
          {c.full_name}
        </button>
        <HealthBadge status={c.health_status} />
      </div>
      <p className="text-sm font-semibold">{c.role}</p>
      <p className="text-sm text-text-muted">{c.justification}</p>
      <span className="self-start rounded-md bg-surface-hover px-2 py-0.5 text-xs font-medium">{c.license ?? "Sin licencia"}</span>
      <AlertList alerts={c.alerts} compact />
    </div>
  );
}
