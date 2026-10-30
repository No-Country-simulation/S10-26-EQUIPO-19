// Cliente de la API del catálogo (contrato de API, secciones 2.1 a 2.4).
// Con NEXT_PUBLIC_USE_MOCK=true usa los datos de ejemplo de data/mock.ts; con false consulta la API real.
import type {
  Category,
  ListParams,
  PaginatedRepositories,
  RepositoryDetail,
  SearchParams,
} from "@/types/api";
import { MOCK_CATEGORIES, getMockDetail, listMock, searchMock } from "@/data/mock";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
export const USE_MOCK = (process.env.NEXT_PUBLIC_USE_MOCK ?? "true") === "true";

/** Error de la API con su código HTTP, para mostrar mensajes distintos (404, sin conexión, etc.). */
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function toQuery(params: Record<string, unknown>) {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") qs.set(key, String(value));
  }
  const text = qs.toString();
  return text ? `?${text}` : "";
}

async function getJson<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { cache: "no-store" });
  } catch {
    throw new ApiError(0, "No pudimos conectar con la API.");
  }
  if (!res.ok) throw new ApiError(res.status, `La API respondió ${res.status} en ${path}`);
  return res.json() as Promise<T>;
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
    if (!detail) throw new ApiError(404, `El repositorio con id ${id} no fue encontrado.`);
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
