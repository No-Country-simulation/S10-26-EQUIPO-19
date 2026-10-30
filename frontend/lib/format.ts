// Formatos de números y fechas en español (Chile como referencia regional).

/** 19500 → "19,5 k"; 100000 → "100 k". */
export function compactNumber(value: number) {
  // Formato propio para que siempre diga "k" en minúscula (Intl mezcla "k" y "K" según el tamaño).
  if (Math.abs(value) < 1000) return fullNumber(value);
  const k = new Intl.NumberFormat("es-CL", { maximumFractionDigits: value < 100000 ? 1 : 0 }).format(value / 1000);
  return `${k} k`;
}

export function fullNumber(value: number) {
  return value.toLocaleString("es-CL");
}

/** Fecha corta: "21-10-2026". */
export function formatDate(iso: string | null) {
  if (!iso) return "Sin datos";
  return new Date(iso).toLocaleDateString("es-CL", { day: "2-digit", month: "2-digit", year: "numeric" });
}

/** "hoy", "hace 1 día", "hace 3 meses"… a partir de la fecha del último commit. */
export function relativeTime(iso: string | null, now = Date.now()) {
  if (!iso) return "Sin datos";
  const days = Math.floor((now - Date.parse(iso)) / 86_400_000);
  if (days <= 0) return "hoy";
  if (days === 1) return "hace 1 día";
  if (days < 30) return `hace ${days} días`;
  const months = Math.floor(days / 30);
  if (months < 12) return months === 1 ? "hace 1 mes" : `hace ${months} meses`;
  const years = Math.floor(days / 365);
  return years === 1 ? "hace 1 año" : `hace ${years} años`;
}

// documentation_url puede traer varios enlaces separados por " ; " (uno por cada repo de la integración).
export function splitUrls(value: string | null | undefined): string[] {
  if (!value) return [];
  return value
    .split(";")
    .map((url) => url.trim())
    .filter((url) => /^https?:\/\//.test(url));
}

// Nombre corto del sitio para mostrar en el enlace (sin "www.").
export function urlHost(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
