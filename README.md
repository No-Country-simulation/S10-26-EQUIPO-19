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
├── app/                  # Código fuente del backend (FastAPI)
│   ├── schemas/          # Modelos de validación Pydantic
│   ├── main.py           # Instancia de FastAPI, configuración de CORS y rutas base
│   └── __init__.py
├── docs/                 # Documentación técnica de desarrollo
│   └── api-contract.md   # Especificación del contrato de API REST
├── documentacion/        # Documentos oficiales del proyecto (consigna, WBS, arquitectura)
├── .env.example          # Plantilla de variables de entorno (sin secretos)
├── requirements.txt      # Dependencias de Python
└── README.md             # Documentación general del proyecto
```

## ⚙️ Instalación y ejecución

### 🚀 Backend (FastAPI)

#### Requisitos previos
- [Python 3.10+](https://www.python.org/)
- Git

#### 1. Clonar el repositorio y navegar a la carpeta raíz
```bash
git clone <url-del-repositorio>
cd S10-26-EQUIPO-19
```

#### 2. Crear y activar el entorno virtual

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

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno
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

#### 5. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload
```
La API quedará escuchando en: `http://127.0.0.1:8000`

#### 6. Verificación de funcionamiento
- **Ruta de verificación (Health Check):**  
  Navegar a [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) en el navegador. Debe responder:
  ```json
  {"status": "ok", "message": "El backend de OpenBridge está activo y funcionando"}
  ```
- **Documentación interactiva (Swagger UI):**  
  Disponible en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para explorar y probar todos los endpoints documentados.
- **Documentación alternativa (Redoc):**  
  Disponible en [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 👥 Equipo

## 👥 Equipo

| Integrante | Rol |
|---|---|
| Alexis Albarenga | Backend Developer |
| Demian Naon | Full Stack Developer |
| Francisco Aguilar García | QA Engineer |
| Gabriela Valdivia | QA Engineer |
| Juan Espinosa | Backend Developer |
| Maria Fatima Soares Gomes | Project Manager |
| Melina Daniela Martinez | Backend Developer |
| Thiago Viana Santos | Software Engineer |

---

<p align="center">Hecho con 💙 por el <b>S10-26-equipo 19</b> · Simulación Laboral NoCountry · 2026</p>

