import { Fragment, type ReactNode } from "react";

// Intérprete de Markdown básico y seguro para las respuestas del asistente (4.4).
// Entiende títulos (#), viñetas (*, -, +), listas numeradas, **negrita**, *cursiva*,
// `código` y enlaces [texto](https://...). No interpreta HTML: todo se muestra como texto,
// y solo se enlazan direcciones https.

type Block =
  | { kind: "heading"; level: number; text: string }
  | { kind: "paragraph"; text: string }
  | { kind: "list"; ordered: boolean; items: ListItem[] };

type ListItem = { text: string; children: ListItem[]; ordered: boolean };

const HEADING = /^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/;
const BULLET = /^(\s*)[*+-]\s+(.*)$/;
const NUMBERED = /^(\s*)\d+[.)]\s+(.*)$/;
const RULE = /^\s{0,3}([-*_])(\s*\1){2,}\s*$/;

function parseBlocks(text: string): Block[] {
  const blocks: Block[] = [];
  let paragraph: string[] = [];
  let list: Extract<Block, { kind: "list" }> | null = null;
  let lastItem: ListItem | null = null;
  let afterBlank = false;

  const closeParagraph = () => {
    if (paragraph.length) blocks.push({ kind: "paragraph", text: paragraph.join(" ") });
    paragraph = [];
  };
  const closeList = () => {
    list = null;
    lastItem = null;
  };

  for (const raw of text.replace(/\r\n?/g, "\n").split("\n")) {
    const line = raw.replace(/\s+$/, "");
    if (!line.trim()) {
      closeParagraph();
      afterBlank = true;
      continue;
    }
    const wasBlank = afterBlank;
    afterBlank = false;
    if (RULE.test(line)) {
      closeParagraph();
      closeList();
      continue;
    }
    const heading = line.match(HEADING);
    if (heading) {
      closeParagraph();
      closeList();
      blocks.push({ kind: "heading", level: heading[1].length, text: heading[2] });
      continue;
    }
    const item = line.match(BULLET) ?? line.match(NUMBERED);
    if (item) {
      closeParagraph();
      const ordered = !BULLET.test(line);
      const nested = item[1].length >= 2 && lastItem !== null;
      const entry: ListItem = { text: item[2], children: [], ordered };
      if (nested && lastItem) {
        lastItem.children.push(entry);
      } else {
        if (!list || list.ordered !== ordered) {
          list = { kind: "list", ordered, items: [] };
          blocks.push(list);
        }
        list.items.push(entry);
        lastItem = entry;
      }
      continue;
    }
    // Línea que continúa la viñeta anterior: sangrada, o pegada a ella sin línea en blanco.
    if (list && lastItem && paragraph.length === 0 && (!wasBlank || /^\s{2,}/.test(line))) {
      const target: ListItem = lastItem.children.at(-1) ?? lastItem;
      target.text += " " + line.trim();
      continue;
    }
    closeList();
    paragraph.push(line.trim());
  }
  closeParagraph();
  return blocks;
}

// `código` | [texto](url) | **negrita** | __negrita__ | *cursiva* | _cursiva_
const INLINE =
  /`([^`]+)`|\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)|\*\*(.+?)\*\*|__(.+?)__|(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])|(?<![\w_])_(?![\s_])(.+?)(?<![\s_])_(?![\w_])/g;

function safeUrl(url: string): string | null {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" ? parsed.href : null;
  } catch {
    return null;
  }
}

function inline(text: string, key = "i"): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let n = 0;
  for (const m of text.matchAll(INLINE)) {
    const start = m.index ?? 0;
    if (start > last) out.push(text.slice(last, start));
    const k = `${key}-${n++}`;
    if (m[1] !== undefined) {
      out.push(
        <code key={k} className="rounded bg-surface-muted px-1 py-0.5 font-mono text-[13px]">
          {m[1]}
        </code>,
      );
    } else if (m[2] !== undefined) {
      const href = safeUrl(m[3]);
      out.push(
        href ? (
          <a
            key={k}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-primary underline underline-offset-2"
          >
            {inline(m[2], k)}
          </a>
        ) : (
          <Fragment key={k}>{inline(m[2], k)}</Fragment>
        ),
      );
    } else if (m[4] !== undefined || m[5] !== undefined) {
      out.push(<strong key={k}>{inline(m[4] ?? m[5], k)}</strong>);
    } else {
      out.push(<em key={k}>{inline(m[6] ?? m[7], k)}</em>);
    }
    last = start + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

function List({ items, ordered, k }: { items: ListItem[]; ordered: boolean; k: string }) {
  const Tag = ordered ? "ol" : "ul";
  return (
    <Tag className={`flex flex-col gap-1 pl-5 ${ordered ? "list-decimal" : "list-disc"}`}>
      {items.map((item, i) => (
        <li key={`${k}-${i}`}>
          {inline(item.text, `${k}-${i}`)}
          {item.children.length > 0 && (
            <div className="mt-1">
              <List items={item.children} ordered={item.children[0].ordered} k={`${k}-${i}-c`} />
            </div>
          )}
        </li>
      ))}
    </Tag>
  );
}

export default function Markdown({ text }: { text: string }) {
  return (
    <>
      {parseBlocks(text).map((block, i) => {
        const k = `b${i}`;
        if (block.kind === "heading") {
          // Dentro del chat los títulos van chicos: h3 para # y ##, h4 para el resto.
          return block.level <= 2 ? (
            <h3 key={k} className="mt-2 text-lg font-semibold">
              {inline(block.text, k)}
            </h3>
          ) : (
            <h4 key={k} className="mt-2 text-base font-semibold">
              {inline(block.text, k)}
            </h4>
          );
        }
        if (block.kind === "list") return <List key={k} items={block.items} ordered={block.ordered} k={k} />;
        return <p key={k}>{inline(block.text, k)}</p>;
      })}
    </>
  );
}
