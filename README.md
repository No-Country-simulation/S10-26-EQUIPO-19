# 🌉 OpenBridge — Acelerador de Integraciones Open Source

> Catálogo inteligente de herramientas open-source con asistente de arquitectura basado en IA (RAG).

**Simulación Laboral Abierta · NoCountry** · Equipo **S10-26-equipo 19**  
**Sector:** Developer Tools / Servicios de Consultoría Tech (B2B)  

![Estado](https://img.shields.io/badge/estado-en%20planificaci%C3%B3n-blue)

---

## 📋 Tabla de contenidos

- [El problema](#-el-problema)
- [Nuestra solución](#-nuestra-solución)
- [Funcionalidades](#-funcionalidades)
- [Desafíos técnicos](#-desafíos-técnicos)
- [Entregables](#-entregables)
- [Stack tecnológico](#-stack-tecnológico)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Instalación y ejecución](#-instalación-y-ejecución)
- [Despliegue en producción](#-despliegue-en-producción)
- [Equipo](#-equipo)

---

## 🎯 El problema

Una firma de desarrollo y consultoría tecnológica gestiona **más de 30 proyectos al año** para startups y empresas medianas, donde el *Time-to-Market* y los costos de infraestructura son clave.

Hoy sus arquitectos y líderes técnicos invierten **entre 15 y 20 horas por proyecto** investigando manualmente herramientas, microservicios y librerías open-source. La información está dispersa en GitHub, listas *Awesome*, foros y Product Hunt, lo que provoca:

- Duplicación de esfuerzos entre proyectos.
- Adopción de librerías abandonadas.
- Pérdida de oportunidades para integrar alternativas gratuitas y auto-hospedadas (como Supabase, Keycloak o Meilisearch) desde el día uno.

## 💡 Nuestra solución

**OpenBridge** centraliza, categoriza y cura un catálogo de herramientas open-source con ideas de integración estructuradas, y suma un **asistente consultor con IA (RAG)** que analiza la descripción de un negocio y recomienda la combinación técnica ideal.

> **Ejemplo:**  
> *Input:* "Estoy construyendo un e-commerce B2B de logística"  
> *Output:* mapa de arquitectura recomendado con un stack open-source justificado y cómo conectar sus componentes.  

## ✨ Funcionalidades

| Módulo | Descripción |
|---|---|
| 📚 **Catálogo** | Navegación por categorías funcionales: Autenticación, Base de Datos, Pagos, IA, Analítica, Búsqueda, etc. |
| 📄 **Ficha técnica** | Por repositorio: nombre, descripción, estrellas, última actualización, licencia, lenguaje, *health score*, issues abiertos y mantenedor activo. |
| 🔌 **Ideas de integración** | Estructuradas: tipo de integración (REST, Docker, SDK), disparadores/webhooks, snippet de ejemplo, compatibilidad de stack y nivel de dificultad. |
| 🔍 **Buscador avanzado** | Filtros por lenguaje, licencia (MIT, Apache…), nivel de mantenimiento, estrellas mínimas y categoría. |
| 🤖 **Asistente consultor (RAG)** | Recibe la descripción de un producto y devuelve una propuesta de arquitectura open-source justificada. |
| 🔄 **Pipeline de ingesta** | Proceso diario que consume la API de GitHub, actualiza metadatos, recalcula el *health score* y guarda embeddings. |

## 🧩 Desafíos técnicos

1. **Sincronización y métricas de salud:** diseñar la ingesta respetando los *rate limits* de GitHub y manteniendo actualizada la actividad de commits, estrellas e issues.
2. **Recomendación semántica (RAG):** estructurar la base vectorial y los embeddings para que el asistente entienda el contexto del negocio, no solo coincidencias de palabras.
3. **Ideas de integración estandarizadas:** modelar los datos para que cada idea sea una guía técnica real y no texto plano.

## 📦 Entregables

- [ ] Catálogo web interactivo y responsivo, con categorías, filtros y búsqueda por texto.
- [ ] Asistente consultor de arquitectura con IA.
- [ ] Pipeline automatizado de ingesta desde la API de GitHub.
- [ ] Base de datos poblada con **al menos 100 repositorios** open-source, con ideas de integración y métricas.

## 🛠️ Stack tecnológico

> ⚠️ Stack sugerido por la consigna. **Pendiente de confirmar por el equipo.**

| Capa | Tecnologías |
|---|---|
| Frontend | Next.js · React · Tailwind CSS |
| Backend | FastAPI (Python) o Node.js (NestJS / Express) |
| Base de datos y búsqueda vectorial | PostgreSQL + pgvector · Supabase o Qdrant |
| IA y automatización | LangChain / LlamaIndex · OpenAI API u modelos open-source (Ollama / Together AI) · GitHub REST/GraphQL API |

## 📁 Estructura del repositorio

```text
S10-26-EQUIPO-19/
├── app/                  # Código fuente del backend (FastAPI)
│   ├── core/             # Componentes transversales (rate limiting, middlewares de seguridad)
│   ├── routers/          # Endpoints de la API separados por dominio (categories, repositories, github)
│   ├── schemas/          # Modelos de validación Pydantic
│   ├── database.py       # Configuración y cliente de conexión a Supabase
│   ├── main.py           # Instancia de FastAPI, configuración de CORS, cabeceras y rutas base
│   └── __init__.py
├── docs/                 # Documentación técnica (guía de estilo, contrato de API)
│   └── api-contract.md   # Especificación del contrato de API REST
├── frontend/             # Interfaz web: Next.js + React + TypeScript + Tailwind CSS
├── .env.example          # Plantilla de variables de entorno del backend (sin secretos)
├── requirements.txt      # Dependencias de Python
└── README.md             # Documentación general del proyecto
```

## ⚙️ Instalación y ejecución

### 📥 Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd S10-26-EQUIPO-19
```

### 🖥️ Frontend

**Requisitos:** Node.js 20.9 o superior y npm.

```bash
cd frontend
npm install
cp .env.example .env.local   # en Windows (PowerShell): copy .env.example .env.local
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000). Por defecto usa datos de ejemplo (`NEXT_PUBLIC_USE_MOCK=true`), así que no necesita el backend para funcionar.

Más detalles (variables de entorno y estructura del frontend) en [`frontend/README.md`](frontend/README.md).

### 🚀 Backend (FastAPI)

**Requisitos previos:** [Python 3.10+](https://www.python.org/) y Git.

#### 1. Crear y activar el entorno virtual

Desde la carpeta raíz del repositorio:

- **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell restringe la ejecución de scripts, podés habilitarlo temporalmente con `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`).*

- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno
Copiar la plantilla `.env.example` para generar tu archivo local `.env`:

- **En Windows (PowerShell):**
  ```powershell
  copy .env.example .env
  ```
- **En Linux / macOS:**
  ```bash
  cp .env.example .env
  ```
> ⚠️ El archivo `.env` nunca debe subirse al repositorio. Las credenciales de desarrollo se comparten de forma segura por canales internos del equipo.

#### 4. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload
```
La API quedará escuchando en: `http://127.0.0.1:8000`

#### 5. Verificación de funcionamiento
- **Ruta de verificación (Health Check):**  
  Navegar a [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) en el navegador. Debe responder:
  ```json
  {"status": "ok", "message": "El backend de OpenBridge está activo y funcionando"}
  ```
- **Documentación interactiva (Swagger UI):**  
  Disponible en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para explorar y probar todos los endpoints documentados.
- **Documentación alternativa (Redoc):**  
  Disponible en [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🚀 Despliegue en Producción

### ☁️ Plataforma elegida: Render
Para el backend de **OpenBridge** el equipo técnico definió a **[Render](https://render.com)** como la plataforma oficial de alojamiento (Web Service) debido a las siguientes razones técnicas:
1. **Despliegue continuo nativo (CI/CD):** Se conecta directamente con la rama `main` del repositorio de GitHub, ejecutando la compilación y el arranque automáticamente ante cada cambio integrado.
2. **Compatibilidad ASGI y Uvicorn:** Permite ejecutar aplicaciones asíncronas FastAPI en Python sin necesidad de configurar y mantener manualmente servidores dedicados ni proxies inversos.
3. **Capa de seguridad y SSL administrada:** Integración nativa con Cloudflare en el borde que provee certificados TLS/HTTPS automáticos, mitigación de ataques volumétricos y enrutamiento seguro.
4. **Administración centralizada de variables de entorno:** Gestión segura de secretos en producción sin exponer credenciales en el código fuente.

### 📦 Pasos para el despliegue

#### 1. Configuración del servicio en Render
1. Acceder al panel de control de [Render](https://dashboard.render.com/) y crear un nuevo **Web Service**.
2. Conectar el repositorio de GitHub: `No-Country-simulation/S10-26-EQUIPO-19`.
3. Establecer los parámetros de ejecución:
   - **Environment:** `Python 3`
   - **Root Directory:** `./`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Auto-Deploy:** `Yes` (para desplegar automáticamente ante pushes a `main`).

#### 2. Variables de entorno en producción
En la sección **Environment** del Web Service en Render, configurar las variables necesarias (sin incluir secretos reales en el repositorio):

| Variable | Descripción | Valor / Ejemplo |
|---|---|---|
| `SUPABASE_URL` | URL del proyecto Supabase | `https://<proyecto>.supabase.co` |
| `SUPABASE_KEY` | Clave de servicio / API Key de Supabase | *(service_role o anon key)* |
| `GITHUB_TOKEN` | Token de acceso personal de GitHub (PAT) para ingesta y consultas | `ghp_xxxxxxxxxxxx` |
| `ENVIRONMENT` | Entorno de ejecución (`production` deshabilita `/docs` y `/redoc` por seguridad) | `production` |
| `ALLOWED_ORIGINS` | Lista blanca de dominios autorizados para CORS separados por coma | `https://openbridge-rcv2.onrender.com,http://localhost:3000` |
| `SYNC_API_KEY` | Clave secreta para autorizar peticiones al endpoint de sincronización (`/sync`) | `tu_clave_secreta` |
| `PORT` | Puerto HTTP (asignado dinámicamente por Render) | `10000` |

### 🔄 Pipeline y tareas automatizadas (GitHub Actions)

El repositorio incluye dos flujos automatizados en `.github/workflows/`:
- **Sincronización de repositorios (`github_sync.yml`):** Ejecuta periódicamente la ingesta y actualización de métricas del catálogo de GitHub en Supabase.
- **Keep-Alive de producción (`keep-alive.yml` y `keep_alive.py`):** Ejecuta un ping HTTP cada 10 minutos contra el endpoint `/health` de Render para evitar la suspensión por inactividad (*cold start*) propia de las instancias gratuitas, garantizando disponibilidad continua para el frontend.

### ✅ Prueba de arranque y verificación

El backend en producción se encuentra operativo y validado en la siguiente URL base:
**`https://openbridge-rcv2.onrender.com`**

Para verificar el arranque correcto:
```bash
curl -f https://openbridge-rcv2.onrender.com/health
```

**Respuesta esperada (HTTP 200 OK):**
```json
{
  "status": "ok",
  "message": "El backend de OpenBridge está activo y funcionando"
}
```

En este entorno productivo:
- La documentación `/docs` y `/openapi.json` se encuentra restringida bajo `ENVIRONMENT=production`.
- Se aplican las cabeceras de endurecimiento de seguridad (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Content-Security-Policy`).
- El rate limiting se encuentra activo para proteger los recursos de IA y llamadas a GitHub.

---

## 👥 Equipo

| Integrante | Rol |
|---|---|
| Alexis Albarenga | Backend Developer |
| Demian Naon | Full Stack Developer |
| Francisco Aguilar García | QA Engineer |
| Gabriela Valdivia | QA Engineer |
| Juan Espinosa | Backend Developer |
| Martin Valdes | Ethical Hacker |
| Maria Fatima Soares Gomes | Project Manager |
| Melina Daniela Martinez | Backend Developer |
| Thiago Viana Santos | Software Engineer |

---

<p align="center">Hecho con 💙 por el <b>S10-26-equipo 19</b> · Simulación Laboral NoCountry · 2026</p>
