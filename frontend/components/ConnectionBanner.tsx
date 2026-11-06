"use client";

import { useEffect, useState } from "react";

// Aviso global: "Sin acceso a internet" mientras no hay conexión y "Conexión restablecida" al volver.

export default function ConnectionBanner() {
  const [state, setState] = useState<"online" | "offline" | "restored">("online");

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const goOffline = () => {
      clearTimeout(timer);
      setState("offline");
    };
    const goOnline = () => {
      setState((prev) => (prev === "offline" ? "restored" : prev));
      timer = setTimeout(() => setState("online"), 4000);
    };
    if (!navigator.onLine) goOffline();
    window.addEventListener("offline", goOffline);
    window.addEventListener("online", goOnline);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("offline", goOffline);
      window.removeEventListener("online", goOnline);
    };
  }, []);

  if (state === "online") return null;
  const offline = state === "offline";
  return (
    <div
      role="status"
      aria-live="polite"
      className={`sticky top-0 z-50 px-4 py-2.5 text-center text-sm font-semibold ${
        offline ? "bg-status-risk-bg text-status-risk" : "bg-status-active-bg text-status-active"
      }`}
    >
      {offline ? "Sin acceso a internet. Revisa tu conexión; te avisaremos cuando se restablezca." : "Conexión restablecida."}
    </div>
  );
}
