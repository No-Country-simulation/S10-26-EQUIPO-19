// Cliente de la API del catálogo (contrato de API, secciones 2.1 a 2.3).
import type { Category, PaginatedRepositories, SearchParams } from "@/types/api";
import { MOCK_CATEGORIES, filterMock } from "@/data/mock";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
const USE_MOCK = (process.env.NEXT_PUBLIC_USE_MOCK ?? "true") === "true";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`La API respondió ${res.status} en ${path}`);
  return res.json() as Promise<T>;
}

export async function getCategories(): Promise<Category[]> {
  if (USE_MOCK) return MOCK_CATEGORIES;
  return getJson<Category[]>("/categories");
}

export async function searchRepositories(params: SearchParams): Promise<PaginatedRepositories> {
  if (USE_MOCK) return filterMock(params);
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") qs.set(key, String(value));
  }
  return getJson<PaginatedRepositories>(`/repositories/search?${qs.toString()}`);
}
