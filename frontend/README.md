# OpenBridge · Frontend

Interfaz web del catálogo de OpenBridge, hecha con **Next.js (App Router)**, **React**, **TypeScript** y **Tailwind CSS v4**.

## Requisitos

- Node.js 20.9 o superior
- npm

## Cómo levantarlo en tu computador

```bash
cd frontend
npm install
cp .env.example .env.local   # en Windows (PowerShell): copy .env.example .env.local
npm run dev
```

Abre <http://localhost:3000>.

## Variables de entorno

| Variable | Para qué sirve | Valor en `.env.example` |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | URL base de la API del backend | `https://openbridge-rcv2.onrender.com/api/v1` (API desplegada). Para la API local: `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_USE_MOCK` | `false` consulta la API; `true` usa los datos de ejemplo de `data/mock.ts` | `false` |

La API desplegada está en el plan gratuito de Render, que se suspende cuando no se usa: la primera carga puede tardar cerca de un minuto mientras el servicio despierta.

Nunca subas claves ni tokens al repositorio: van en `.env.local`, que está ignorado por git.

## Estructura

```
frontend/
├── app/
│   ├── layout.tsx            # Layout general: tipografía Poppins, encabezado, pie y tema
│   ├── page.tsx              # Inicio con el esqueleto del catálogo
│   ├── globals.css           # Design tokens (colores, tipografía, radios, modo claro/oscuro)
│   ├── asistente/            # Esqueleto de la pantalla del asistente
│   └── guia-de-estilo/       # Vista viva de la guía de estilo
├── components/               # Header, NavLinks, ThemeToggle, Catalog, RepositoryCard, HealthBadge
├── data/mock.ts              # Datos de ejemplo alineados con el contrato de API
├── lib/api.ts                # Cliente de la API (categorías y búsqueda)
├── types/api.ts              # Tipos del contrato de API
└── public/                   # logo-horizontal.png (encabezado) y logo.png (ícono)
```

## Guía de estilo

Las reglas de uso de colores, tipografía, componentes y modo oscuro están en [`../docs/guia-de-estilo.md`](../docs/guia-de-estilo.md). Con el proyecto corriendo, la vista viva está en <http://localhost:3000/guia-de-estilo>.

## Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Compilación de producción |
| `npm run start` | Sirve la compilación de producción |
