# OpenBridge QA Automation

## 1. Descripción general

La carpeta `qa/automation/` contiene el framework de automatización de
pruebas funcionales y end-to-end (E2E) de **OpenBridge**, desarrollado
con Python, Pytest y Playwright.

Su objetivo es comprobar de forma repetible que las funciones
principales de OpenBridge operan correctamente, detectar regresiones y
generar reportes que faciliten la revisión de resultados por parte del
equipo.

**Entorno predeterminado:** https://openbridge-dev.vercel.app/\
**Navegador:** Chromium\
**Ejecución en GitHub Actions:** manual mediante `workflow_dispatch`.

> La automatización valida la aplicación desde la perspectiva del
> usuario. No sustituye las pruebas unitarias, las pruebas de contrato
> de API ni las revisiones de seguridad.

## 2. Objetivos y utilidad

-   Verificar la disponibilidad de las funciones principales.
-   Comprobar búsquedas, filtros, ordenamiento y combinación de
    criterios.
-   Validar la visualización y comparación de repositorios.
-   Comprobar la carga e interacción del asistente según los casos
    implementados.
-   Detectar fallos funcionales y regresiones en los flujos cubiertos.
-   Conservar evidencia técnica de las ejecuciones: reportes, capturas y
    trazas cuando se generan.
-   Proporcionar resultados reproducibles para apoyar las revisiones de
    calidad.

## 3. Arquitectura y organización

El framework utiliza **Page Object Model (POM)** para separar las
interacciones con la interfaz de los casos de prueba.

``` text
qa/automation/
├── .gitignore
├── conftest.py
├── pytest.ini
├── requirements.txt
├── data/
├── pages/
│   ├── __init__.py
│   ├── assistant_page.py
│   ├── base_page.py
│   ├── catalog_page.py
│   └── comparison_page.py
├── scripts/
│   └── generate_executive_report.py
└── tests/
    ├── assistant/
    │   └── test_assistant.py
    ├── catalog/
    │   ├── __init__.py
    │   ├── test_catalog_categories.py
    │   ├── test_catalog_combined_filters.py
    │   ├── test_catalog_comparison.py
    │   ├── test_catalog_filters.py
    │   ├── test_catalog_happy_path.py
    │   ├── test_catalog_search.py
    │   └── test_catalog_sorting.py
    └── smoke/
        └── test_smoke.py
```

### Responsabilidad de los componentes

  ----------------------------------------------------------------------------
  Componente                               Responsabilidad
  ---------------------------------------- -----------------------------------
  `conftest.py`                            Fixtures compartidas de Playwright,
                                           navegador, contexto y página;
                                           tiempos de espera y configuración
                                           headless para CI.

  `pytest.ini`                             Rutas de descubrimiento, URL base,
                                           marcadores y opciones de ejecución
                                           y reporte.

  `requirements.txt`                       Dependencias Python fijadas para el
                                           framework.

  `pages/`                                 Page Objects que centralizan las
                                           interacciones con la aplicación.

  `tests/smoke/`                           Comprobaciones rápidas de funciones
                                           críticas.

  `tests/catalog/`                         Pruebas funcionales del catálogo.

  `tests/assistant/`                       Pruebas del asistente.

  `scripts/generate_executive_report.py`   Convierte resultados JUnit XML en
                                           un resumen ejecutivo HTML.

  `data/`                                  Directorio reservado para datos de
                                           prueba.
  ----------------------------------------------------------------------------

### Page Object Model

-   `base_page.py`: funcionalidad compartida.
-   `catalog_page.py`: interacciones con el catálogo.
-   `comparison_page.py`: interacciones con la comparación de
    repositorios.
-   `assistant_page.py`: interacciones con el asistente.

Los localizadores se resuelven mediante atributos HTML, roles accesibles
y texto visible. La automatización no depende de atributos `data-testid`
que actualmente no están implementados de forma general en la
aplicación.

## 4. Suites y cobertura

Pytest utiliza dos marcadores:

-   `smoke`: comprobaciones rápidas de disponibilidad de funciones
    esenciales.
-   `e2e`: recorridos funcionales end-to-end.

### Smoke

La suite Smoke contiene cinco verificaciones:

  ID        Verificación
  --------- ----------------------------------------
  SMK-001   Carga del catálogo.
  SMK-002   Búsqueda de Ollama.
  SMK-003   Filtro por la categoría Autenticación.
  SMK-004   Visualización del repositorio Ollama.
  SMK-005   Carga de la interfaz del asistente.

SMK-005 comprueba la carga de la interfaz; no envía una consulta al
asistente ni valida la respuesta generada.

### E2E y pruebas funcionales

  -----------------------------------------------------------------------
  Módulo                              Cobertura
  ----------------------------------- -----------------------------------
  Catálogo                            Flujo principal, búsqueda por
                                      texto, filtros, categorías y
                                      combinación de filtros.

  Ordenamiento                        Validación de las opciones de
                                      ordenamiento disponibles.

  Comparación                         Selección y comparación de
                                      repositorios.

  Asistente                           Carga e interacción contemplada por
                                      los casos automatizados.
  -----------------------------------------------------------------------

La ejecución completa de Pytest incluye todos los tests descubiertos,
independientemente de su marcador.

**Referencia de validación local:** en la última validación documentada
se ejecutaron 25 pruebas: 5 Smoke y 20 E2E, todas aprobadas. Es el
resultado de esa ejecución concreta, no una garantía sobre ejecuciones
futuras.

## 5. Requerimientos

-   Python **3.13**.
-   pip.
-   Playwright y navegador Chromium.
-   Git para obtener y actualizar el repositorio.
-   Conectividad con la aplicación que se desea probar.

Las versiones de las dependencias están fijadas en `requirements.txt`.
Las dependencias principales incluyen `pytest`, `playwright`,
`pytest-playwright` y `pytest-html`.

## 6. Instalación local

Desde la raíz del repositorio, abrir PowerShell:

``` powershell
cd .\qa\automation
```

Crear y activar un entorno virtual (recomendado):

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instalar Chromium:

``` powershell
python -m playwright install chromium
```

Crear el directorio de reportes:

``` powershell
New-Item -ItemType Directory -Force .\reports
```

## 7. Ejecución de pruebas

Todos los comandos siguientes se ejecutan desde `qa/automation/`.

**Smoke:**

``` powershell
pytest -m smoke
```

**E2E:**

``` powershell
pytest -m e2e
```

**Suite completa:**

``` powershell
pytest
```

**Un archivo específico:**

``` powershell
pytest .\tests\catalog\test_catalog_search.py
```

### Cambiar la URL base

La URL predeterminada está definida en `pytest.ini`. Puede
sobrescribirse en una ejecución:

``` powershell
pytest -m smoke --base-url="https://openbridge-dev.vercel.app"
```

Utilizar únicamente entornos autorizados y preparados para pruebas.
Antes de ejecutar contra otro entorno, comprobar que las operaciones y
datos de prueba sean seguros para ese entorno.

### Configuración del navegador

-   En local, Chromium se abre en modo visible.
-   Cuando la variable `CI` tiene el valor `true`, Chromium se ejecuta
    en modo headless.
-   Viewport: 1440 × 900.
-   Tiempo de espera predeterminado de página y navegación: 15 segundos.

## 8. Reportes y evidencias

`pytest.ini` configura un reporte HTML de Pytest y la conservación de
trazas y capturas cuando corresponde.

Para generar también JUnit XML:

``` powershell
pytest -m smoke --junitxml=reports/junit.xml
```

Después, generar el resumen ejecutivo:

``` powershell
python .\scripts\generate_executive_report.py
```

  -----------------------------------------------------------------------
  Archivo o directorio                Contenido
  ----------------------------------- -----------------------------------
  `reports/report.html`               Reporte HTML detallado de Pytest.

  `reports/junit.xml`                 Resultados estructurados JUnit XML,
                                      si se solicita con `--junitxml`.

  `reports/resumen_ejecutivo.html`    Resumen ejecutivo generado a partir
                                      de `junit.xml`.

  `test-results/`                     Evidencias de Playwright, como
                                      capturas o trazas, cuando se
                                      generan.
  -----------------------------------------------------------------------

Los reportes y evidencias son artefactos de ejecución y no deben
versionarse como código fuente. El `.gitignore` de esta carpeta excluye
los artefactos locales configurados.

El generador ejecutivo requiere que exista `reports/junit.xml`; por
ello, primero se debe ejecutar Pytest con `--junitxml`.

## 9. GitHub Actions

El workflow está ubicado en:

``` text
.github/workflows/qa-tests.yml
```

La ejecución es manual:

1.  Abrir el repositorio en GitHub.
2.  Entrar en **Actions**.
3.  Seleccionar **OpenBridge QA - Automated Tests**.
4.  Pulsar **Run workflow**.
5.  Seleccionar la rama que contiene el workflow.
6.  Elegir una suite:
    -   `smoke`: pruebas críticas.
    -   `e2e`: pruebas end-to-end.
    -   `all`: suite completa.
7.  Ejecutar y revisar el resultado.

El workflow instala Python y dependencias, instala Chromium, ejecuta la
suite seleccionada, genera el resumen ejecutivo e intenta cargar
reportes y evidencias como artefactos. La retención configurada para
estos artefactos es de 14 días.

La carga de evidencias se intenta incluso si las pruebas fallan. Al
final, el workflow marca la ejecución como fallida si fallaron las
pruebas o la generación del reporte.

**Importante:** el workflow actual es manual. No está configurado para
ejecutarse automáticamente con cada `push` ni con cada despliegue de
Vercel.

## 10. Consideraciones y alcance

-   La URL base predeterminada apunta a DEV.
-   Las pruebas dependen de la disponibilidad de la aplicación y de que
    los elementos de interfaz mantengan los comportamientos y
    localizadores esperados.
-   Los cambios en la interfaz pueden requerir actualizar Page Objects o
    casos de prueba.
-   Comprobar que la interfaz del asistente carga no equivale a validar
    la exactitud de sus respuestas.
-   Los resultados representan el comportamiento observado en el entorno
    y momento de la ejecución.
-   Los reportes pueden contener información técnica útil para
    depuración; revisarlos antes de compartirlos fuera del equipo.

## 11. Mantenimiento

Al incorporar nuevas pruebas:

1.  Colocar el archivo en el módulo correspondiente dentro de `tests/`.
2.  Utilizar el patrón de nombre `test_*.py`.
3.  Marcar las pruebas rápidas con `@pytest.mark.smoke` y las end-to-end
    con `@pytest.mark.e2e`.
4.  Reutilizar o ampliar los Page Objects en `pages/`.
5.  Ejecutar localmente la prueba nueva y la suite relacionada.
6.  Revisar reportes y evidencias antes de integrar los cambios.

Mantener sincronizados `requirements.txt`, `pytest.ini`, los Page
Objects, los casos de prueba y el workflow de GitHub Actions.
