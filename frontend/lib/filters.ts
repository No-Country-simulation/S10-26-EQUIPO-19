// Opciones de los filtros del catálogo (5.7).
// La API no tiene un endpoint de lenguajes ni de licencias: estas listas salen del inventario de repositorios
// aprobados. Si se agrega un lenguaje o una licencia nueva al catálogo, hay que sumarla aquí.
import type { HealthStatus } from "@/types/api";

export const LANGUAGES = [
  "C", "C#", "C++", "Clojure", "Dart", "Elixir", "Go", "Java", "JavaScript", "Kotlin", "PHP", "Python", "Ruby",
  "Rust", "Scala", "Swift", "TypeScript",
];

export const LICENSES = [
  "Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0", "LGPL-3.0", "GPL-2.0", "GPL-3.0",
  "AGPL-3.0", "Unlicense",
];

export const HEALTH_STATUSES: HealthStatus[] = ["Activo", "En riesgo", "Abandonado"];

/** Nombre visible del filtro de nivel de mantenimiento (en el prototipo: "Estado"). */
export const HEALTH_FILTER_LABEL = "Estado";

/** Estrellas mínimas: el control va de 0 a 100 k, en pasos de 5 k. */
export const STARS_STEP = 5000;
export const STARS_MAX = 100000;
