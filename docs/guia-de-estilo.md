# Guía de estilo y design tokens · OpenBridge

Tarea 5.2. Define cómo se aplica la identidad visual de OpenBridge (tarea 5.1) en la interfaz. Los tokens están implementados en `frontend/app/globals.css` y se pueden ver en vivo en `/guia-de-estilo`.

## 1. Paleta de marca

| Nombre | Hex | Token Tailwind | Uso |
|---|---|---|---|
| Rosa | `#FC0395` | `brand-pink` | Color de forma: íconos, puntos, líneas, gráficos e indicadores. Nunca como fondo. |
| Índigo | `#6366F1` | `brand-indigo` | Color principal de marca. |
| Cian | `#07BCEB` | `brand-cyan` | Apoyo en gráficos y decoración. |
| Turquesa | `#1BDBC5` | `brand-teal` | Apoyo en gráficos y decoración. |
| Pizarra | `#64748B` | `brand-slate` | Neutro de marca. |
| Rosa suave | `#FFE4F3` | `brand-pink-soft` | Fondos de avisos y etiquetas. |
| Índigo suave | `#EEF0FE` | `brand-indigo-soft` | Fondos de secciones, etiquetas de categoría y hover en modo claro. |
| Rosa profundo | `#C0027A` | `brand-pink-deep` | Fondo de botones, etiquetas y tarjetas destacadas, con formas, íconos y texto en blanco. |

**Rosa: forma o fondo, nunca los dos.**

- `#FC0395` es color de **forma**. Como fondo no sirve: el texto blanco encima tiene un contraste de 3,8:1, insuficiente para texto normal (mínimo 4,5:1), y en superficies grandes vibra y cansa la vista, sobre todo en modo oscuro.
- `#C0027A` sí puede ser **fondo**, con formas, íconos y texto en blanco encima (contraste 5,9:1, pasa AA).
- Como color de texto, el acento es `#C0027A` en modo claro (5,7:1 sobre el fondo) y `#FC0395` en modo oscuro (5,0:1 sobre el fondo). Por eso los componentes usan el token `accent` y no el color de marca directamente.

**Saturación y luminosidad.** Los colores muy saturados y luminosos (rosa, cian, turquesa, índigo) "expanden": parecen más grandes y, sobre fondo oscuro, brillan más. Los de poca luminosidad o saturación (rosa profundo, pizarra, azul noche) "contraen". Regla práctica: superficies grandes en colores que contraen; acentos, íconos y detalles en colores que expanden, con trazos algo más finos en modo oscuro.

Para texto y botones el índigo se usa en su versión accesible, `brand-indigo-strong` (`#4F46E5`).

## 2. Colores semánticos (modo claro y oscuro)

Los componentes usan estos tokens, no los colores de marca directamente, para que el modo oscuro (opcional 9.7) funcione sin cambios en cada pantalla.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `surface` | `#F8FAFC` | `#0B1220` | Fondo de la página |
| `surface-muted` | `#F1F5F9` | `#131C2E` | Fondo secundario: paneles, barras y zonas de apoyo |
| `surface-hover` | `#EEF0FE` | `#1E2A44` | Filas y elementos al pasar el cursor |
| `card` | `#FFFFFF` | `#131C2E` | Tarjetas y paneles |
| `border` | `#E2E8F0` | `#24314A` | Bordes y separadores |
| `text` | `#0F172A` | `#F1F5F9` | Texto principal (17,1:1) |
| `text-muted` | `#475569` | `#94A3B8` | Texto secundario (7,2:1 / 7,3:1) |
| `primary` | `#4F46E5` | `#818CF8` | Botones, enlaces y foco (6,0:1 / 6,3:1) |
| `accent` | `#C0027A` | `#FC0395` | Acentos, etiquetas e indicadores (5,7:1 / 5,0:1) |

Los contrastes indicados se miden sobre el fondo de la página (`surface`). Ejemplo de uso: `bg-card text-text border-border`.

## 3. Nivel de mantenimiento

Corresponde a `health_status` del contrato de API. Cada estado lleva siempre su nombre visible, para no depender solo del color.

| Estado | Token de texto / fondo | Cuándo |
|---|---|---|
| Activo | `status-active` / `status-active-bg` | Último commit hace 90 días o menos |
| En riesgo | `status-risk` / `status-risk-bg` | Más de 90 y hasta 180 días |
| Abandonado | `status-abandoned` / `status-abandoned-bg` | Más de 180 días o archivado |
| Sin datos | `status-unknown` / `status-unknown-bg` | Fecha del último commit desconocida (`null`) |

Componente: `components/HealthBadge.tsx`.

## 4. Tipografía

Fuente: **Poppins** (Google Fonts), cargada con `next/font` en `app/layout.tsx`. Código: fuente monoespaciada del sistema.

| Nivel | Clase Tailwind | Tamaño / peso |
|---|---|---|
| Título principal | `text-4xl font-bold` | 36 px · 700 |
| Título de sección | `text-2xl font-semibold` | 24 px · 600 |
| Subtítulo | `text-lg font-semibold` | 18 px · 600 |
| Cuerpo | `text-base` | 16 px · 400 |
| Secundario | `text-sm text-text-muted` | 14 px · 400 |
| Código | `font-mono text-sm` | 14 px |

## 5. Espaciado, radios y sombras

- Espaciado en múltiplos de 4 px (escala de Tailwind): `gap-2`, `gap-4`, `p-5`, `py-8`.
- Ancho máximo del contenido: `max-w-6xl` con `px-4` de margen lateral.
- Radios: tarjetas `var(--radius-card)` (16 px); botones y etiquetas `var(--radius-pill)` (redondeados); campos `rounded-xl`.
- Sombras suaves solo en tarjetas: `shadow-sm`.

## 6. Componentes base

- **Botón principal:** `bg-primary text-primary-contrast`, alto mínimo 44 px, forma de píldora.
- **Botón secundario:** borde `border-border`, fondo transparente, hover `bg-surface-hover`.
- **Botón y etiqueta destacados ("Nuevo"):** `bg-brand-pink-deep text-white`.
- **Etiqueta destacada con borde:** `border-2 border-accent text-accent`.
- **Enlace:** `text-primary`, subrayado al pasar el cursor.
- **Tarjeta de repositorio:** `components/RepositoryCard.tsx`.
- **Selector de tema:** `components/ThemeToggle.tsx`.

## 7. Accesibilidad

- Contraste mínimo 4,5:1 para texto normal y 3:1 para texto grande y elementos gráficos (WCAG 2.1 AA).
- Se puede comprobar con Lighthouse (pestaña de las herramientas de desarrollo de Chrome, categoría Accesibilidad) o con la extensión axe DevTools.
- Foco visible en todos los elementos interactivos (`:focus-visible` con `primary`).
- Áreas táctiles de al menos 44 px.
- Estados y niveles siempre con texto o íconos, no solo con color.
- Antes de aprobar un color, revisarlo en un monitor estándar, en una pantalla de gama amplia (Retina u OLED) y en el móvil con brillo alto y bajo: el mismo HEX se percibe más intenso en pantallas de gama amplia y en modo oscuro.
- Interfaz en español (`<html lang="es">`).

## 8. Modo claro y modo oscuro (opcional 9.7)

- Se activa con la clase `dark` en `<html>`; el selector guarda la preferencia en el navegador.
- Sin preferencia guardada, se respeta la del sistema operativo.
- Para nuevos componentes: usar solo tokens semánticos; si hace falta un ajuste puntual, usar la variante `dark:`.
