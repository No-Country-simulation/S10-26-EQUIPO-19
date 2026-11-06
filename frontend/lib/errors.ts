import { ApiError } from "@/lib/api";

// Mensajes para el usuario final: sin términos técnicos (API, backend, códigos HTTP).
// Cada pantalla indica qué estaba cargando ("las herramientas", "la ficha", etc.).

export type FriendlyError = { title: string; message: string; retry: boolean };

export function friendlyError(err: unknown, what: string): FriendlyError {
  const kind = err instanceof ApiError ? err.kind : "unreachable";
  switch (kind) {
    case "offline":
      return { title: "Sin acceso a internet", message: `Revisa tu conexión. Cuando vuelva, podrás cargar ${what} de nuevo.`, retry: true };
    case "timeout":
      return { title: "Está tardando más de lo normal", message: "El servicio puede estar iniciándose. Espera unos segundos e inténtalo de nuevo.", retry: true };
    case "server":
      return { title: "Algo salió mal", message: `Tuvimos un problema al cargar ${what}. Inténtalo de nuevo en unos minutos.`, retry: true };
    case "rate_limit":
      return { title: "Demasiadas consultas seguidas", message: "Espera un minuto antes de volver a intentarlo.", retry: false };
    case "not_found":
      return { title: "No lo encontramos", message: `No pudimos encontrar ${what}. Puede que ya no esté en el catálogo.`, retry: false };
    case "invalid":
      return { title: "Revisa los datos", message: `No pudimos procesar la solicitud de ${what}. Revisa los datos e inténtalo de nuevo.`, retry: false };
    case "unavailable":
      return { title: "Función no disponible", message: "Esta función no está disponible en este momento. Inténtalo más tarde.", retry: false };
    default:
      return { title: "No pudimos conectarnos", message: "El servicio no responde en este momento. Inténtalo de nuevo en unos minutos.", retry: true };
  }
}
