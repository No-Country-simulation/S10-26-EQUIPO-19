"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  useNodesInitialized,
  useReactFlow,
  useStore,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { ArchitectureComponent, ArchitectureConnection } from "@/types/api";

// Mapa de arquitectura (9.1): dibuja con React Flow los componentes y las conexiones que
// devuelve el asistente en el campo "architecture". Las líneas no llevan texto: el nombre y el
// rol van dentro de cada tarjeta, y el detalle de cada conexión está en "Cómo se conectan".

const COL_GAP = 290;
const ROW_GAP = 120;
// Modo compacto: con muchas herramientas, las tarjetas muestran solo el nombre y quedan más juntas.
// El rol completo aparece al pasar el cursor y está en "Stack recomendado" y "Cómo se conectan".
const COMPACT_FROM = 9;
const COMPACT_COL_GAP = 220;
const COMPACT_ROW_GAP = 70;
const INDIGO = "#6366f1";

type ToolData = { title: string; subtitle: string; status: string | null; alerts: number; repoId: number; compact: boolean };
type ToolNode = Node<ToolData, "tool">;

const STATUS_DOT: Record<string, string> = {
  Activo: "bg-status-active",
  "En riesgo": "bg-status-risk",
  Abandonado: "bg-status-abandoned",
};

function ToolCard({ data }: NodeProps<ToolNode>) {
  return (
    <div
      title={data.compact ? `${data.title}: ${data.subtitle}` : undefined}
      aria-label={`${data.title}: ${data.subtitle}`}
      className={`cursor-pointer rounded-xl border-2 border-brand-indigo bg-card text-left text-text shadow-sm transition-colors hover:bg-surface-hover ${
        data.compact ? "w-40 px-3 py-2" : "w-56 px-4 py-3"
      }`}
    >
      <Handle type="target" position={Position.Left} isConnectable={false} className="border-0! bg-brand-indigo!" />
      <div className="flex items-center gap-2">
        <span
          aria-hidden="true"
          title={data.status ?? "Sin datos"}
          className={`size-2.5 shrink-0 rounded-full ${STATUS_DOT[data.status ?? ""] ?? "bg-status-unknown"}`}
        />
        <span className="truncate font-display text-sm font-semibold first-letter:uppercase">{data.title}</span>
        {data.alerts > 0 && (
          <span title={`${data.alerts} alerta${data.alerts === 1 ? "" : "s"} de riesgo`} className="ml-auto shrink-0 text-xs">
            ⚠️
          </span>
        )}
      </div>
      {!data.compact && <p className="mt-1 line-clamp-2 text-xs text-text-muted">{data.subtitle}</p>}
      <Handle type="source" position={Position.Right} isConnectable={false} className="border-0! bg-brand-indigo!" />
    </div>
  );
}

const NODE_TYPES = { tool: ToolCard };
const FIT_OPTIONS = { padding: 0.15 };

/** Vuelve a encuadrar el mapa cuando cambia el tamaño del recuadro (por ejemplo, al girar el celular). */
function FitOnResize() {
  const { fitView } = useReactFlow();
  const width = useStore((s) => s.width);
  const height = useStore((s) => s.height);
  const ready = useNodesInitialized();
  useEffect(() => {
    if (ready && width > 0 && height > 0) void fitView(FIT_OPTIONS);
  }, [ready, width, height, fitView]);
  return null;
}

/** Ubica cada herramienta en una columna según el camino más largo desde un nodo sin entradas. */
function buildGraph(components: ArchitectureComponent[], connections: ArchitectureConnection[]) {
  const keys = new Set(components.map((c) => c.key));
  const valid = connections.filter((cn) => keys.has(cn.from) && keys.has(cn.to) && cn.from !== cn.to);
  const rank = new Map(components.map((c) => [c.key, 0]));
  // Relajación acotada: termina aunque el asistente devuelva un ciclo.
  for (let i = 0; i < components.length; i++) {
    for (const cn of valid) {
      const next = Math.min((rank.get(cn.from) ?? 0) + 1, components.length - 1);
      if (next > (rank.get(cn.to) ?? 0)) rank.set(cn.to, next);
    }
  }
  const compact = components.length >= COMPACT_FROM;
  const colGap = compact ? COMPACT_COL_GAP : COL_GAP;
  const rowGap = compact ? COMPACT_ROW_GAP : ROW_GAP;
  const columns = new Map<number, ArchitectureComponent[]>();
  for (const c of components) {
    const r = rank.get(c.key) ?? 0;
    columns.set(r, [...(columns.get(r) ?? []), c]);
  }
  const nodes: ToolNode[] = [];
  for (const [r, list] of columns) {
    list.forEach((c, i) => {
      nodes.push({
        id: c.key,
        type: "tool",
        position: { x: r * colGap, y: (i - (list.length - 1) / 2) * rowGap },
        data: {
          title: c.full_name.split("/")[1] ?? c.full_name,
          subtitle: c.role,
          status: c.health_status,
          alerts: c.alerts?.length ?? 0,
          repoId: c.repository_id,
          compact,
        },
      });
    });
  }
  const edges: Edge[] = valid.map((cn, i) => ({
    id: `${cn.from}-${cn.to}-${i}`,
    source: cn.from,
    target: cn.to,
    type: "smoothstep",
    style: { stroke: INDIGO, strokeWidth: 2, strokeDasharray: cn.verified ? undefined : "6 5" },
    markerEnd: { type: MarkerType.ArrowClosed, color: INDIGO },
  }));
  return { nodes, edges, compact };
}

/** Sigue el selector de tema de la página (clase "dark" en <html>). */
function useDarkMode() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const root = document.documentElement;
    const update = () => setDark(root.classList.contains("dark"));
    update();
    const observer = new MutationObserver(update);
    observer.observe(root, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);
  return dark;
}

export default function ArchitectureMap({
  components,
  connections,
  onOpen,
}: {
  components: ArchitectureComponent[];
  connections: ArchitectureConnection[];
  onOpen: (id: number) => void;
}) {
  const { nodes, edges, compact } = useMemo(() => buildGraph(components, connections), [components, connections]);
  const dark = useDarkMode();
  if (components.length < 2) return null;

  return (
    <section aria-label="Mapa de arquitectura" className="flex flex-col gap-2">
      <h2 className="text-lg font-semibold">Mapa de arquitectura</h2>
      <div className="h-80 overflow-hidden rounded-xl border border-border bg-surface md:h-96">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={NODE_TYPES}
          colorMode={dark ? "dark" : "light"}
          fitView
          fitViewOptions={FIT_OPTIONS}
          minZoom={0.3}
          maxZoom={2}
          nodesDraggable={false}
          nodesConnectable={false}
          zoomOnScroll={false}
          preventScrolling={false}
          onNodeClick={(_, node) => onOpen((node as ToolNode).data.repoId)}
        >
          <Background gap={20} size={1} />
          <Controls showInteractive={false} position="bottom-right" />
          <FitOnResize />
        </ReactFlow>
      </div>
      <p className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-text-muted">
        <span className="inline-flex items-center gap-2">
          <svg width="28" height="6" aria-hidden="true"><line x1="0" y1="3" x2="28" y2="3" stroke={INDIGO} strokeWidth="2" /></svg>
          Idea de integración del catálogo
        </span>
        <span className="inline-flex items-center gap-2">
          <svg width="28" height="6" aria-hidden="true"><line x1="0" y1="3" x2="28" y2="3" stroke={INDIGO} strokeWidth="2" strokeDasharray="6 5" /></svg>
          Conexión sugerida por el asistente
        </span>
        {compact && <span>Vista compacta: pasa el cursor sobre una herramienta para ver su rol.</span>}
        <span>Usa + y − para acercar o alejar, arrastra para moverte y haz clic en una herramienta para ver su ficha.</span>
      </p>
    </section>
  );
}
