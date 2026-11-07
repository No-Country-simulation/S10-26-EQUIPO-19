import { Suspense } from "react";
import CompareView from "@/components/CompareView";

export const metadata = { title: "Comparar · OpenBridge" };

// Comparador lado a lado (9.5): /comparar?ids=1,2,3
export default function ComparePage() {
  return (
    <Suspense fallback={<p className="text-text-muted">Cargando la comparación…</p>}>
      <CompareView />
    </Suspense>
  );
}
