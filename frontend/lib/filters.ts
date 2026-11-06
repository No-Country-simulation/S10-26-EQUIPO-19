// Opciones de los filtros del catálogo (5.7).
// La API no tiene un endpoint de lenguajes ni de licencias: estas listas salen de los 159 repositorios cargados
// en la base (verificado con la API desplegada el 01/11). Si se agrega un lenguaje o una licencia nueva al
// catálogo, hay que sumarla aquí.
import type { HealthStatus } from "@/types/api";

export const LANGUAGES = [
  "C", "C#", "C++", "Elixir", "Go", "Groovy", "HTML", "Java", "JavaScript", "Lua", "PHP", "PLpgSQL", "Python",
  "Ruby", "Rust", "TypeScript", "Zig",
];

export const LICENSES = [
  "Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0", "LGPL-2.1", "LGPL-3.0", "GPL-2.0",
  "GPL-3.0", "AGPL-3.0", "EPL-1.0", "EPL-2.0", "OSL-3.0", "PostgreSQL",
];

export const HEALTH_STATUSES: HealthStatus[] = ["Activo", "En riesgo", "Abandonado"];

/** Nombre visible del filtro de nivel de mantenimiento (definido por Diseño). */
export const HEALTH_FILTER_LABEL = "Nivel de mantenimiento";

/** Estrellas mínimas: el control va de 0 a 100 k, en pasos de 5 k. */
export const STARS_STEP = 5000;
export const STARS_MAX = 100000;
