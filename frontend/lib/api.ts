// Cliente de la API del catálogo (contrato de API, secciones 2.1 a 2.4).
// Con NEXT_PUBLIC_USE_MOCK=true usa los datos de ejemplo de data/mock.ts; con false consulta la API real.
import type {
  Category,
  ChatMessage,
  ChatResponse,
  CompareResponse,
  ComposeResponse,
  ListParams,
  PaginatedRepositories,
  RepositoryDetail,
  SearchParams,
} from "@/types/api";
import { MOCK_CATEGORIES, compareMock, composeMock, getMockDetail, listMock, mockChat, searchMock } from "@/data/mock";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
export const USE_MOCK = (process.env.NEXT_PUBLIC_USE_MOCK ?? "false") === "true";

/** Tipo de falla, para mostrar al usuario un mensaje claro sin detalles técnicos (ver lib/errors.ts). */
export type ApiErrorKind = "offline" | "timeout" | "unreachable" | "server" | "rate_limit" | "not_found" | "invalid" | "unavailable";

/** Error de una consulta al servicio. `message` es interno (consola); al usuario se le muestra friendlyError(). */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public kind: ApiErrorKind = kindFromStatus(status),
    /** Texto del campo "detail" del servidor, solo para validaciones (400) que se pueden mostrar tal cual. */
    public detail: string | null = null,
  ) {
    super(message);
  }
}

function kindFromStatus(status: number): ApiErrorKind {
  if (status === 429) return "rate_limit";
  if (status === 404) return "not_found";
  if (status === 405) return "unavailable";
  if (status === 400 || status === 422) return "invalid";
  if (status >= 500) return "server";
  return "unreachable";
}

/** Tiempo máximo de espera. El plan gratuito de Render tarda ~50 s en despertar el servidor. */
const TIMEOUT_MS = 60_000;
const ASSISTANT_TIMEOUT_MS = 90_000;

/** Hace la consulta con tiempo máximo y convierte cualquier falla en un ApiError clasificado. */
async function request<T>(path: string, init: RequestInit = {}, timeoutMs = TIMEOUT_MS): Promise<T> {
  if (typeof navigator !== "undefined" && navigator.onLine === false) {
    throw new ApiError(0, `Sin conexión a internet (${path})`, "offline");
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { cache: "no-store", ...init, signal: controller.signal });
  } catch (err) {
    if (controller.signal.aborted) throw new ApiError(0, `Tiempo de espera agotado (${path})`, "timeout");
    if (typeof navigator !== "undefined" && navigator.onLine === false) throw new ApiError(0, `Sin conexión a internet (${path})`, "offline");
    throw new ApiError(0, `Sin respuesta del servicio (${path}): ${String(err)}`, "unreachable");
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    const detail = await errorDetail(res);
    throw new ApiError(res.status, `HTTP ${res.status} en ${path}`, kindFromStatus(res.status), detail);
  }
  return res.json() as Promise<T>;
}

function toQuery(params: Record<string, unknown>) {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") qs.set(key, String(value));
  }
  const text = qs.toString();
  return text ? `?${text}` : "";
}

function getJson<T>(path: string): Promise<T> {
  return request<T>(path);
}

/** Simula la latencia de la red con los datos de ejemplo, para ver los estados de carga. */
const delay = <T,>(value: T) => new Promise<T>((resolve) => setTimeout(() => resolve(value), 250));

export async function getCategories(): Promise<Category[]> {
  if (USE_MOCK) return delay(MOCK_CATEGORIES);
  return getJson<Category[]>("/categories");
}

/** 2.2 · Listado paginado del catálogo (sin filtros). */
export async function listRepositories(params: ListParams = {}): Promise<PaginatedRepositories> {
  if (USE_MOCK) return delay(listMock(params));
  return getJson<PaginatedRepositories>(`/repositories${toQuery(params)}`);
}

/** 2.3 · Búsqueda por texto con filtros. */
export async function searchRepositories(params: SearchParams): Promise<PaginatedRepositories> {
  if (USE_MOCK) return delay(searchMock(params));
  return getJson<PaginatedRepositories>(`/repositories/search${toQuery(params)}`);
}

/** 2.4 · Ficha técnica de un repositorio. */
export async function getRepository(id: number): Promise<RepositoryDetail> {
  if (USE_MOCK) {
    const detail = getMockDetail(id);
    if (!detail) throw new ApiError(404, `Repositorio ${id} no encontrado (datos de ejemplo)`);
    return delay(detail);
  }
  return getJson<RepositoryDetail>(`/repositories/${id}`);
}

/** true si el usuario aplicó algún filtro: entonces se usa la búsqueda (2.3) en vez del listado (2.2). */
export function hasFilters(params: SearchParams) {
  return Boolean(
    params.q || params.category_id || params.language || params.license || params.health_status || params.min_stars,
  );
}

/** Detalle que entrega FastAPI en los errores ({"detail": "..."}), si viene como texto. */
async function errorDetail(res: Response): Promise<string | null> {
  try {
    const body = await res.json();
    return typeof body?.detail === "string" ? body.detail : null;
  } catch {
    return null;
  }
}

/** 4.4 · Asistente consultor: descripción del negocio → stack recomendado y justificado. */
export async function askAssistant(message: string, history: ChatMessage[] = []): Promise<ChatResponse> {
  if (USE_MOCK) return new Promise((resolve) => setTimeout(() => resolve(mockChat(message)), 600));
  return request<ChatResponse>(
    "/assistant/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // El servicio acepta hasta 20 mensajes de historial, de hasta 4000 caracteres cada uno.
      body: JSON.stringify({
        message,
        conversation_history: history.slice(-20).map((m) => ({ role: m.role, content: m.content.slice(0, 4000) })),
      }),
    },
    ASSISTANT_TIMEOUT_MS,
  );
}

/** 9.2 · docker-compose de arranque para las herramientas del stack recomendado. */
export async function generateCompose(fullNames: string[]): Promise<ComposeResponse> {
  if (USE_MOCK) return delay(composeMock(fullNames));
  return request<ComposeResponse>("/compose", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repositories: fullNames.slice(0, 10) }),
  });
}

/** 9.2 · El botón del docker-compose se muestra solo si está activado (cuando exista el servicio /compose). */
export const COMPOSE_ENABLED = USE_MOCK || process.env.NEXT_PUBLIC_ENABLE_COMPOSE === "true";

/** 9.5 · Comparación lado a lado de 2 o 3 repositorios. */
export async function compareRepositories(ids: number[]): Promise<CompareResponse> {
  if (USE_MOCK) {
    const result = compareMock(ids);
    if (!result) throw new ApiError(404, "Repositorios no encontrados (datos de ejemplo)");
    return delay(result);
  }
  return request<CompareResponse>(`/repositories/compare?ids=${ids.join(",")}`);
}
