import type { ReactNode } from "react";
import HealthBadge from "@/components/HealthBadge";

export const metadata = { title: "Guía de estilo · OpenBridge" };

// Vista viva de la guía de estilo (tarea 5.2). Sigue la estructura de la guía de diseño:
// 01 Marca · 02 Tipografía y componentes · 03 Colores semánticos · 04 Modo claro
// 05 Modo oscuro · 06 Reglas del rosa · 07 Saturación y luminosidad · 08 Pantallas.

const BRAND = [
  { name: "Rosa", token: "brand-pink", hex: "#FC0395", cls: "bg-brand-pink" },
  { name: "Índigo", token: "brand-indigo", hex: "#6366F1", cls: "bg-brand-indigo" },
  { name: "Cian", token: "brand-cyan", hex: "#07BCEB", cls: "bg-brand-cyan" },
  { name: "Turquesa", token: "brand-teal", hex: "#1BDBC5", cls: "bg-brand-teal" },
  { name: "Pizarra", token: "brand-slate", hex: "#64748B", cls: "bg-brand-slate" },
  { name: "Rosa suave", token: "brand-pink-soft", hex: "#FFE4F3", cls: "bg-brand-pink-soft" },
  { name: "Índigo suave", token: "brand-indigo-soft", hex: "#EEF0FE", cls: "bg-brand-indigo-soft" },
  { name: "Rosa profundo", token: "brand-pink-deep", hex: "#C0027A", cls: "bg-brand-pink-deep", isNew: true },
];

const SEMANTIC = [
  { token: "surface", use: "Fondo de la página", light: "#F8FAFC", dark: "#0B1220" },
  { token: "surface-muted", use: "Fondo secundario", light: "#F1F5F9", dark: "#131C2E" },
  { token: "surface-hover", use: "Hover", light: "#EEF0FE", dark: "#1E2A44" },
  { token: "card", use: "Tarjetas y paneles", light: "#FFFFFF", dark: "#131C2E" },
  { token: "border", use: "Bordes y separadores", light: "#E2E8F0", dark: "#24314A" },
  { token: "text", use: "Texto principal", light: "#0F172A", dark: "#F1F5F9" },
  { token: "text-muted", use: "Texto secundario", light: "#475569", dark: "#94A3B8" },
  { token: "primary", use: "Botones, enlaces y foco", light: "#4F46E5", dark: "#818CF8" },
  { token: "accent", use: "Acentos y etiquetas", light: "#C0027A", dark: "#FC0395" },
];

const SATURATION = [
  { name: "Rosa", hex: "#FC0395", sl: "S 98 % · L 50 %", expands: true },
  { name: "Cian", hex: "#07BCEB", sl: "S 94 % · L 47 %", expands: true },
  { name: "Turquesa", hex: "#1BDBC5", sl: "S 78 % · L 48 %", expands: true },
  { name: "Índigo", hex: "#6366F1", sl: "S 84 % · L 67 %", expands: true },
  { name: "Índigo primario", hex: "#4F46E5", sl: "S 75 % · L 59 %", expands: true },
  { name: "Rosa profundo", hex: "#C0027A", sl: "S 98 % · L 38 %", expands: false },
  { name: "Pizarra", hex: "#64748B", sl: "S 16 % · L 47 %", expands: false },
  { name: "Azul noche", hex: "#0F172A", sl: "S 47 % · L 11 %", expands: false },
];

const CHECKLIST = [
  "Un monitor sRGB estándar",
  "Una pantalla Retina u OLED de gama amplia",
  "Un móvil con brillo alto y con brillo bajo",
  "Modo claro y modo oscuro, con el modo nocturno del sistema activado",
  "El contraste: texto ≥ 4,5:1 y componentes ≥ 3:1",
];

function Section({ num, kicker, title, children }: { num: string; kicker: string; title: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-6 border-t border-border pt-10">
      <div className="flex flex-col gap-1">
        <p className="text-xs font-bold uppercase tracking-wider text-accent">
          {num} — {kicker}
        </p>
        <h2 className="text-3xl font-bold">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Swatch({ hex }: { hex: string }) {
  return <span className="h-4 w-4 shrink-0 rounded-full border border-border" style={{ backgroundColor: hex }} aria-hidden />;
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 20 20" className="h-5 w-5 shrink-0" aria-hidden>
      <circle cx="10" cy="10" r="10" fill="#1BDBC5" />
      <path d="M6 10.5l2.6 2.6L14 7.6" fill="none" stroke="#0F172A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* Tarjetas de vista previa de los modos claro y oscuro (secciones 04 y 05).
   Usan solo tokens semánticos; el contenedor .light o .dark fija los valores. */
function PreviewCard({ mode, preview, title, token, hex, swatch, contrast, note }: {
  mode: "light" | "dark"; preview: ReactNode; title: string; token: string; hex: string; swatch?: string; contrast?: string; note: string;
}) {
  return (
    <div className="flex flex-col overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
      <div className={`${mode} m-2 flex h-40 flex-col justify-center gap-3 rounded-xl border border-border bg-surface p-5 text-text`}>{preview}</div>
      <div className="flex flex-col gap-1 p-4 pt-2 text-xs">
        <p className="text-sm font-semibold">{title}</p>
        <p className="font-mono text-text-muted">{token}</p>
        <p className="mt-1 flex items-center gap-2 font-medium">
          <Swatch hex={swatch ?? hex} /> {hex}
        </p>
        {contrast && <p className="text-text-muted">Contraste {contrast} sobre el fondo</p>}
        <p className="mt-2 text-text-muted">{note}</p>
      </div>
    </div>
  );
}

function ModePalette({ mode }: { mode: "light" | "dark" }) {
  const d = mode === "dark";
  const v = (light: string, dark: string) => (d ? dark : light);
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <PreviewCard
        mode={mode}
        title="Fondo de la página" token="surface" hex={v("#F8FAFC", "#0B1220")} note="Lienzo general detrás de todo."
        preview={<div className="flex flex-col gap-2 rounded-lg border border-border bg-card p-3"><span className="h-1.5 w-12 rounded bg-text" /><span className="h-1 w-full rounded bg-text-muted" /><span className="h-1 w-2/3 rounded bg-text-muted" /></div>}
      />
      <PreviewCard
        mode={mode}
        title="Fondo secundario" token="surface-muted" hex={v("#F1F5F9", "#131C2E")} note="Paneles, barras y zonas de apoyo."
        preview={<div className="flex flex-col gap-2 rounded-lg border border-border bg-surface-muted p-3"><span className="text-xs">Panel de filtros</span><span className="h-1 w-full rounded bg-text-muted" /><span className="h-1 w-2/3 rounded bg-text-muted" /></div>}
      />
      <PreviewCard
        mode={mode}
        title="Hover" token="surface-hover" hex={v("#EEF0FE", "#1E2A44")} note="Filas y elementos al pasar el cursor."
        preview={<><span className="rounded-lg border border-border bg-card px-3 py-1.5 text-xs">Supabase</span><span className="flex justify-between rounded-lg bg-surface-hover px-3 py-1.5 text-xs"><span>Meilisearch</span><span className="text-text-muted">hover</span></span></>}
      />
      <PreviewCard
        mode={mode}
        title="Bordes y separadores" token="border" hex={v("#E2E8F0", "#24314A")} note="Líneas de campos, tarjetas y divisores."
        preview={<><span className="rounded-lg border-2 border-border bg-card px-3 py-1.5 text-xs text-text-muted">Buscar…</span><span className="mt-1 h-0.5 w-full bg-border" /><span className="text-[10px] text-text-muted">Divisor de sección</span></>}
      />
      <PreviewCard
        mode={mode}
        title="Texto principal" token="text" hex={v("#0F172A", "#F1F5F9")} contrast="17,1:1" note="Títulos y cuerpo de texto."
        preview={<><span className="text-base font-bold">Título principal</span><span className="text-xs">Texto de cuerpo en Poppins regular a 16 px.</span></>}
      />
      <PreviewCard
        mode={mode}
        title="Texto secundario" token="text-muted" hex={v("#475569", "#94A3B8")} contrast={v("7,2:1", "7,3:1")} note="Metadatos, ayudas y pies."
        preview={<><span className="text-xs text-text-muted">Última actualización hace 2 días · MIT</span><span className="text-[10px] text-text-muted">Metadatos y ayudas</span></>}
      />
      <PreviewCard
        mode={mode}
        title="Primario" token="primary" hex={v("#4F46E5", "#818CF8")} contrast={v("6,0:1", "6,3:1")} note="Botones, enlaces y foco."
        preview={<><span className="flex items-center gap-3"><span className="rounded-lg bg-primary px-3 py-1.5 text-xs text-primary-contrast">Ver ficha</span><span className="text-xs text-primary underline">Enlace</span></span><span className="rounded-lg border-2 border-primary bg-card px-3 py-1 text-xs text-text-muted">Foco</span></>}
      />
      <PreviewCard
        mode={mode}
        title="Acentos y etiquetas" token="accent" hex={v("#C0027A", "#FC0395 · #C0027A")} swatch={v("#C0027A", "#FC0395")} contrast={v("5,7:1", "5,0:1")} note="Etiquetas destacadas e indicadores."
        preview={d ? (
          <>
            <span className="flex items-center gap-3"><span className="h-3 w-3 rounded-full bg-brand-pink" /><span className="rounded-[var(--radius-pill)] border-2 border-accent px-4 py-1 text-xs text-accent">Destacado</span></span>
            <span className="flex items-center gap-4"><span className="rounded-[var(--radius-pill)] bg-brand-pink-deep px-4 py-1 text-xs font-semibold text-white">Nuevo</span><span className="h-4 w-4 rounded-full border-2 border-brand-pink" /></span>
          </>
        ) : (
          <>
            <span className="w-fit rounded-[var(--radius-pill)] bg-brand-pink-soft px-4 py-1 text-xs text-accent">Destacado</span>
            <span className="flex items-center gap-4"><span className="rounded-[var(--radius-pill)] bg-brand-pink-deep px-4 py-1 text-xs font-semibold text-white">Nuevo</span><span className="h-3 w-3 rounded-full bg-brand-pink-deep" /></span>
          </>
        )}
      />
    </div>
  );
}

export default function StyleGuidePage() {
  return (
    <div className="flex flex-col gap-12">
      <header className="flex flex-col gap-3">
        <h1 className="text-4xl font-bold">Guía de estilo y design tokens</h1>
        <p className="text-text-muted">Paleta de marca · Modo claro y modo oscuro · Percepción del color · Versión 1.0 · Octubre 2026</p>
        <p className="max-w-3xl text-sm text-text-muted">
          Vista viva de los tokens definidos en <code className="font-mono">app/globals.css</code>. Las reglas de uso están en{" "}
          <code className="font-mono">docs/guia-de-estilo.md</code>.
        </p>
        <div className="mt-2 grid h-2 grid-cols-4 overflow-hidden rounded-full" aria-hidden>
          <span className="bg-brand-pink" /><span className="bg-brand-indigo" /><span className="bg-brand-cyan" /><span className="bg-brand-teal" />
        </div>
      </header>

      <Section num="01" kicker="Marca" title="Paleta de marca">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {BRAND.map((c) => (
            <div key={c.token} className="overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
              <div className={`h-24 ${c.cls}`} />
              <div className="flex flex-col gap-0.5 p-4 text-sm">
                <p className="flex items-center justify-between font-semibold">
                  {c.name}
                  {c.isNew && <span className="text-[10px] font-bold uppercase text-accent">Nuevo</span>}
                </p>
                <p className="text-xs text-text-muted">{c.hex}</p>
                <p className="font-mono text-xs text-text-muted">{c.token}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section num="02" kicker="Tipografía y componentes" title="Poppins y componentes base">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="flex flex-col gap-4">
            {[
              ["text-4xl font-bold", "Título principal", "36 px · 700"],
              ["text-2xl font-semibold", "Título de sección", "24 px · 600"],
              ["text-lg font-semibold", "Subtítulo", "18 px · 600"],
              ["text-base", "Texto de cuerpo", "16 px · 400"],
              ["text-sm", "Texto secundario", "14 px · 400"],
              ["font-mono text-sm", "Código · monoespaciada · 14 px", "14 px · 400"],
            ].map(([cls, label, spec]) => (
              <div key={label} className="flex items-baseline justify-between gap-4">
                <span className={cls}>{label}</span>
                <span className="shrink-0 text-xs text-text-muted">{spec}</span>
              </div>
            ))}
          </div>
          <div className="flex flex-col gap-4">
            <p className="text-xs font-bold uppercase tracking-wider text-accent">Componentes base</p>
            <div className="flex flex-wrap items-center gap-3 rounded-[var(--radius-card)] border border-border bg-surface-muted p-5">
              <button type="button" className="h-11 rounded-[var(--radius-pill)] bg-primary px-5 font-semibold text-primary-contrast hover:opacity-90">
                Botón principal
              </button>
              <button type="button" className="h-11 rounded-[var(--radius-pill)] border border-border bg-card px-5 font-semibold hover:bg-surface-hover">
                Botón secundario
              </button>
              <a href="#" className="font-semibold text-primary hover:underline">Enlace</a>
            </div>
            <div className="flex flex-wrap gap-2">
              <HealthBadge status="Activo" score={91} />
              <HealthBadge status="En riesgo" score={48} />
              <HealthBadge status="Abandonado" score={12} />
              <HealthBadge status={null} />
            </div>
            <p className="text-sm text-text-muted">
              Los estados de salud usan colores de apoyo sobre fondos suaves. El texto siempre es legible y el color no es el único indicador.
            </p>
          </div>
        </div>
      </Section>

      <Section num="03" kicker="Colores semánticos" title="Tokens en modo claro y oscuro">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="text-xs font-bold uppercase tracking-wider text-text-muted">
              <tr className="border-b border-border">
                <th className="py-3 font-bold">Token</th>
                <th className="py-3 font-bold">Uso</th>
                <th className="py-3 font-bold">Modo claro</th>
                <th className="py-3 font-bold">Modo oscuro</th>
              </tr>
            </thead>
            <tbody>
              {SEMANTIC.map((t) => (
                <tr key={t.token} className="border-b border-border">
                  <td className="py-3 font-mono text-xs">{t.token}</td>
                  <td className="py-3">{t.use}</td>
                  <td className="py-3"><span className="flex items-center gap-2"><span className="h-6 w-6 rounded-md border border-border" style={{ backgroundColor: t.light }} />{t.light}</span></td>
                  <td className="py-3"><span className="flex items-center gap-2"><span className="h-6 w-6 rounded-md border border-border" style={{ backgroundColor: t.dark }} />{t.dark}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section num="04" kicker="Modo claro" title="Paleta para el modo claro">
        <ModePalette mode="light" />
      </Section>

      <Section num="05" kicker="Modo oscuro" title="Paleta para el modo oscuro">
        <ModePalette mode="dark" />
      </Section>

      <Section num="06" kicker="Modo oscuro · Reglas" title="Rosa: forma o fondo, nunca los dos">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="flex flex-col gap-5 rounded-[var(--radius-card)] bg-[#0B1220] p-6 text-[#F1F5F9]">
            <div>
              <p className="text-lg font-semibold">#FC0395 es color de forma ✓</p>
              <p className="text-sm text-[#94A3B8]">Íconos, puntos, líneas, gráficos e indicadores.</p>
            </div>
            <div className="flex items-end gap-6" aria-hidden>
              <span className="h-6 w-6 rounded-full bg-brand-pink" />
              <span className="h-6 w-6 rounded-full border-4 border-brand-pink" />
              <span className="flex items-end gap-1"><span className="h-3 w-2 bg-brand-pink" /><span className="h-6 w-2 bg-brand-pink" /><span className="h-4 w-2 bg-brand-pink" /></span>
              <span className="h-2 w-24 overflow-hidden rounded-full bg-[#24314A]"><span className="block h-full w-2/3 bg-brand-pink" /></span>
              <svg viewBox="0 0 40 20" className="h-5 w-10"><path d="M2 18l12-10 8 6 16-12" fill="none" stroke="#FC0395" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </div>
            <div className="border-t border-[#24314A] pt-5">
              <p className="font-semibold">No como fondo ✗</p>
              <div className="mt-3 flex items-center gap-4">
                <span className="rounded-xl bg-brand-pink px-6 py-6 text-sm text-white">Texto sobre rosa</span>
                <p className="text-xs text-[#94A3B8]">
                  <span className="font-semibold text-[#F1F5F9]">Texto blanco: 3,8:1.</span> Insuficiente para texto pequeño y, en grandes
                  superficies, vibra y cansa la vista sobre fondo oscuro.
                </p>
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-5 rounded-[var(--radius-card)] bg-[#0B1220] p-6 text-[#F1F5F9]">
            <div>
              <p className="text-lg font-semibold">#C0027A sí puede ser fondo ✓</p>
              <p className="text-sm text-[#94A3B8]">Con formas, íconos y texto en blanco encima.</p>
            </div>
            <div className="flex items-center gap-3">
              <button type="button" className="h-11 rounded-xl bg-brand-pink-deep px-8 text-sm font-semibold text-white hover:opacity-90">Ver ficha</button>
              <span className="rounded-[var(--radius-pill)] bg-brand-pink-deep px-4 py-1.5 text-xs font-semibold text-white">Destacado</span>
            </div>
            <p className="text-sm">
              Contraste del blanco sobre #C0027A: 5,9:1
              <span className="block text-xs text-[#94A3B8]">Pasa AA para texto normal (mín. 4,5:1).</span>
            </p>
            <div className="flex items-center gap-4 rounded-xl bg-brand-pink-deep p-5 text-white">
              <span className="h-8 w-8 rounded-full border-4 border-white" aria-hidden />
              <span className="flex items-end gap-1" aria-hidden><span className="h-4 w-2 bg-white" /><span className="h-7 w-2 bg-white" /><span className="h-5 w-2 bg-white" /></span>
              <span>
                <span className="block font-semibold">Tarjeta destacada</span>
                <span className="text-sm">Formas y texto en blanco</span>
              </span>
            </div>
          </div>
        </div>
      </Section>

      <Section num="07" kicker="Saturación y luminosidad" title="Colores que expanden y colores que contraen">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="flex flex-col gap-4 text-sm">
            <p><span className="font-semibold">Expansivos.</span> Alta saturación (S ≥ 75 %) y luminosidad media-alta (L ≥ 45 %). Parecen más grandes y cercanos; sobre fondo oscuro, además, se “agrandan” por irradiación.</p>
            <p><span className="font-semibold">Contractivos.</span> Poca luminosidad (L &lt; 45 %) o poca saturación (S &lt; 30 %). Parecen más pequeños y estables, y son los que sostienen superficies grandes.</p>
            <p className="text-primary"><span className="font-semibold">Regla práctica:</span> superficies grandes en contractivos; acentos, íconos y detalles en expansivos, con trazos algo más finos en modo oscuro.</p>
            <div className="flex items-center justify-around rounded-[var(--radius-card)] bg-[#0B1220] p-8 text-xs text-[#F1F5F9]">
              <span className="flex flex-col items-center gap-3"><span className="h-24 w-24 rounded-full bg-brand-pink" />#FC0395 · expande</span>
              <span className="flex flex-col items-center gap-3"><span className="h-24 w-24 rounded-full bg-brand-pink-deep" />#C0027A · contrae</span>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[420px] text-left text-sm">
              <thead className="text-xs font-bold uppercase tracking-wider text-text-muted">
                <tr className="border-b border-border">
                  <th className="py-3 font-bold">Color</th>
                  <th className="py-3 font-bold">Saturación · Luminosidad</th>
                  <th className="py-3 text-right font-bold">Efecto</th>
                </tr>
              </thead>
              <tbody>
                {SATURATION.map((c) => (
                  <tr key={c.hex} className="border-b border-border">
                    <td className="py-2.5">
                      <span className="flex items-center gap-3">
                        <span className="h-7 w-7 shrink-0 rounded-md" style={{ backgroundColor: c.hex }} />
                        <span><span className="block font-medium">{c.name}</span><span className="text-xs text-text-muted">{c.hex}</span></span>
                      </span>
                    </td>
                    <td className="py-2.5">{c.sl}</td>
                    <td className="py-2.5 text-right">
                      <span className={`rounded-[var(--radius-pill)] px-3 py-1 text-xs font-semibold text-white ${c.expands ? "bg-brand-pink-deep" : "bg-brand-indigo-strong"}`}>
                        {c.expands ? "Expande" : "Contrae"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Section>

      <Section num="08" kicker="Pantallas" title="Cómo cambia el color según la pantalla">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="flex flex-col gap-4 text-sm">
            <p><span className="font-semibold">El HEX es el mismo, la percepción no.</span> Los colores web se definen en sRGB, pero las pantallas de gama amplia (como muchas con pantalla Retina u OLED), con más brillo y negros más profundos, hacen que el rosa, el cian y el turquesa se vean más intensos.</p>
            <p><span className="font-semibold">Retina no es solo más color.</span> La alta densidad de píxeles aporta nitidez: los trazos finos y los íconos se ven más limpios, y el contraste percibido sube. Un diseño que luce perfecto en Retina puede verse más pálido o más plano en un monitor estándar.</p>
            <p><span className="font-semibold">En modo oscuro el efecto crece.</span> Sobre fondo oscuro, los colores luminosos parecen brillar y ocupar más espacio. Por eso el rosa #FC0395 se reserva para formas y el fondo se hace con #C0027A.</p>
          </div>
          <div className="flex flex-col gap-4 rounded-[var(--radius-card)] bg-surface-hover p-6 text-sm">
            <p className="font-semibold">Antes de aprobar un color, revísalo en…</p>
            <ul className="flex flex-col gap-3">
              {CHECKLIST.map((item) => (
                <li key={item} className="flex items-start gap-3"><CheckIcon />{item}</li>
              ))}
            </ul>
            <p className="text-primary">No dependas solo del color para comunicar estados: acompáñalo con texto o íconos.</p>
          </div>
        </div>
      </Section>
    </div>
  );
}
