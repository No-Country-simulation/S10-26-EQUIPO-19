import type { ChatResponse } from "@/types/api";

// Exportar la propuesta del asistente (9.6) como Markdown: se lee en cualquier editor, y en
// GitHub o HackMD el bloque Mermaid se dibuja como diagrama.

const shortName = (fullName: string) => fullName.split("/")[1] ?? fullName;
const cell = (text: string) => text.replace(/\|/g, "\\|").replace(/\s*\n\s*/g, " ");
const mermaidId = (key: string) => "n_" + key.replace(/[^A-Za-z0-9_]/g, "_");
const mermaidText = (text: string) => text.replace(/"/g, "'");

export function proposalMarkdown(question: string | null, r: ChatResponse, date = new Date()): string {
  const components = r.architecture?.components ?? [];
  const connections = r.architecture?.connections ?? [];
  const byKey = new Map(components.map((c) => [c.key, c]));
  const name = (key: string) => {
    const c = byKey.get(key);
    return c ? shortName(c.full_name) : key;
  };
  const lines: string[] = [
    "# Propuesta de arquitectura · OpenBridge",
    "",
    `Generada el ${date.toLocaleDateString("es-CL", { day: "2-digit", month: "2-digit", year: "numeric" })} con el asistente de OpenBridge.`,
    "",
  ];

  if (question) lines.push("## Necesidad", "", question, "");
  lines.push("## Recomendación", "", r.answer, "");

  if (components.length) {
    lines.push("## Stack recomendado", "", "| Herramienta | Rol | Licencia | Estado | Alertas |", "|---|---|---|---|---|");
    for (const c of components) {
      const alerts = c.alerts?.length ? c.alerts.map((a) => a.title).join("; ") : "Ninguna";
      lines.push(`| [${cell(c.full_name)}](https://github.com/${c.full_name}) | ${cell(c.role)} | ${c.license ?? "Sin licencia"} | ${c.health_status ?? "Sin datos"} | ${cell(alerts)} |`);
    }
    lines.push("", "### Por qué cada herramienta", "");
    for (const c of components) lines.push(`- **${shortName(c.full_name)}:** ${cell(c.justification)}`);
    lines.push("");
  }

  if (components.length > 1) {
    lines.push("## Mapa de arquitectura", "", "```mermaid", "flowchart LR");
    for (const c of components) lines.push(`  ${mermaidId(c.key)}["${mermaidText(shortName(c.full_name))}<br/><small>${mermaidText(c.role)}</small>"]`);
    for (const cn of connections) {
      if (!byKey.has(cn.from) || !byKey.has(cn.to)) continue;
      lines.push(`  ${mermaidId(cn.from)} ${cn.verified ? "-->" : "-.->"} ${mermaidId(cn.to)}`);
    }
    lines.push("```", "", "Línea continua: idea de integración del catálogo. Línea punteada: conexión sugerida por el asistente.", "");
  }

  if (connections.length) {
    lines.push("## Cómo se conectan", "");
    for (const cn of connections) {
      const origin = cn.verified ? `idea del catálogo${cn.integration_code ? ` ${cn.integration_code}` : ""}` : "sugerida por el asistente";
      lines.push(`- **${name(cn.from)} → ${name(cn.to)}:** ${cell(cn.label)} (${origin}).`);
    }
    lines.push("");
  }

  if (r.sources.length) {
    lines.push("## Fuentes del catálogo", "");
    for (const s of r.sources) lines.push(`- [${s.full_name}](${s.url}) · ${Math.round(s.relevance_score * 100)} % de coincidencia`);
    lines.push("");
  }

  lines.push("---", "", "OpenBridge · El camino corto a tu stack open source. Las métricas corresponden a la fecha de generación.", "");
  return lines.join("\n");
}

export function downloadProposal(question: string | null, r: ChatResponse) {
  const date = new Date();
  const blob = new Blob([proposalMarkdown(question, r, date)], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `openbridge-propuesta-${date.toISOString().slice(0, 10)}.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
