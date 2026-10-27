# Guía de estilo y design tokens · OpenBridge

Tarea 5.2. Define cómo se aplica la identidad visual de OpenBridge (tarea 5.1) en la interfaz. Los tokens están implementados en `frontend/app/globals.css` y se pueden ver en vivo en `/guia-de-estilo`.

## 1. Paleta de marca

| Nombre | Hex | Token Tailwind | Uso |
|---|---|---|---|
| Rosa | `#FC0395` | `brand-pink` | Acento de marca en elementos grandes (ilustraciones, bordes, fondos de destaque). |
| Índigo | `#6366F1` | `brand-indigo` | Color principal de marca. |
| Cian | `#07BCEB` | `brand-cyan` | Apoyo en gráficos y decoración. |
| Turquesa | `#1BDBC5` | `brand-teal` | Apoyo en gráficos y decoración. |
| Pizarra | `#64748B` | `brand-slate` | Neutro de marca. |
| Rosa suave | `#FFE4F3` | `brand-pink-soft` | Fondos de avisos y etiquetas. |
| Índigo suave | `#EEF0FE` | `brand-indigo-soft` | Fondos de secciones y etiquetas de categoría. |

**Contraste:** el rosa y el índigo puros no alcanzan el contraste mínimo (4,5:1) para texto pequeño sobre blanco. Para texto y botones se usan sus versiones fuertes: `brand-pink-strong` (`#C0027A`) y `brand-indigo-strong` (`#4F46E5`).

## 2. Colores semánticos (modo claro y oscuro)

Los componentes usan estos tokens, no los colores de marca directamente, para que el modo oscuro (opcional 9.7) funcione sin cambios en cada pantalla.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `surface` | `#F8FAFC` | `#0B1020` | Fondo de la página |
| `surface-muted` | `#EEF2F7` | `#111833` | Fondos secundarios y hover |
| `card` | `#FFFFFF` | `#151D3B` | Tarjetas y paneles |
| `border` | `#E2E8F0` | `#283257` | Bordes y separadores |
| `text` | `#1E293B` | `#F1F5F9` | Texto principal |
| `text-muted` | `#475569` | `#A5B0C8` | Texto secundario |
| `primary` | `#4F46E5` | `#818CF8` | Botones, enlaces y foco |
| `accent` | `#C0027A` | `#FF5CB8` | Acentos y etiquetas destacadas |

Ejemplo: `bg-card text-text border-border`.

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
- **Botón secundario:** borde `border-border`, fondo transparente, hover `bg-surface-muted`.
- **Enlace:** `text-primary`, subrayado al pasar el cursor.
- **Tarjeta de repositorio:** `components/RepositoryCard.tsx`.
- **Selector de tema:** `components/ThemeToggle.tsx`.

## 7. Accesibilidad

- Contraste mínimo 4,5:1 para texto normal.
- Foco visible en todos los elementos interactivos (`:focus-visible` con `primary`).
- Áreas táctiles de al menos 44 px.
- Estados y niveles siempre con texto, no solo con color.
- Interfaz en español (`<html lang="es">`).

## 8. Modo claro y modo oscuro (opcional 9.7)

- Se activa con la clase `dark` en `<html>`; el selector guarda la preferencia en el navegador.
- Sin preferencia guardada, se respeta la del sistema operativo.
- Para nuevos componentes: usar solo tokens semánticos; si hace falta un ajuste puntual, usar la variante `dark:`.
