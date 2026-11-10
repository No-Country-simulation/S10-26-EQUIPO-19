from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from html import escape


REPORTS_DIR = Path("reports")
INPUT_FILE = REPORTS_DIR / "junit.xml"
OUTPUT_FILE = REPORTS_DIR / "resumen_ejecutivo.html"

TEST_DESCRIPTIONS = {
    "test_smk_001_catalog_loads": (
        "Disponibilidad del catálogo",
        "Comprueba que el catálogo abre correctamente "
        "y muestra herramientas disponibles."
    ),
    "test_smk_002_catalog_search": (
        "Búsqueda de herramientas",
        "Comprueba que el buscador permite localizar "
        "la herramienta Ollama."
    ),
    "test_smk_003_category_filter": (
        "Filtro por categoría",
        "Comprueba que se puede seleccionar la categoría "
        "Autenticación y visualizar resultados."
    ),
    "test_smk_004_repository_detail": (
        "Consulta de ficha técnica",
        "Comprueba que se puede abrir la ficha técnica "
        "de la herramienta Ollama."
    ),
    "test_smk_005_assistant_loads": (
        "Disponibilidad del asistente",
        "Comprueba que la interfaz del asistente y sus "
        "controles están visibles."
    ),
}


def get_test_status(test_case):
    if test_case.find("failure") is not None:
        return "Fallida"

    if test_case.find("error") is not None:
        return "Error"

    if test_case.find("skipped") is not None:
        return "Omitida"

    return "Aprobada"


def read_junit_report():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo {INPUT_FILE}. "
            "Ejecuta primero las pruebas generando el reporte JUnit."
        )

    root = ET.parse(INPUT_FILE).getroot()

    if root.tag == "testsuites":
        test_cases = root.findall(".//testcase")
    else:
        test_cases = root.findall("testcase")

    results = []

    for case in test_cases:
        raw_name = case.attrib.get("name", "Prueba sin nombre")
        test_id = raw_name.split("[")[0]

        title, description = TEST_DESCRIPTIONS.get(
            test_id,
            (test_id, "Prueba automatizada de OpenBridge.")
        )

        results.append({
            "id": test_id,
            "title": title,
            "description": description,
            "status": get_test_status(case),
            "duration": float(case.attrib.get("time", 0)),
            "details": (
                case.findtext("failure")
                or case.findtext("error")
                or case.findtext("skipped")
                or ""
            )
        })

    return results


def generate_html(results):
    total = len(results)
    passed = sum(r["status"] == "Aprobada" for r in results)
    failed = sum(r["status"] in ("Fallida", "Error") for r in results)
    skipped = sum(r["status"] == "Omitida" for r in results)
    duration = sum(r["duration"] for r in results)

    if total == 0:
        overall_status = "Sin resultados"
        conclusion = "No se encontraron pruebas en el archivo de resultados."
    elif failed:
        overall_status = "Se detectaron problemas"
        conclusion = (
            "Una o más verificaciones presentaron problemas. "
            "Se recomienda revisar los detalles y las evidencias."
        )
    elif skipped:
        overall_status = "Ejecución con pruebas omitidas"
        conclusion = (
            "No se detectaron fallos entre las pruebas ejecutadas, "
            "pero algunas verificaciones fueron omitidas."
        )
    else:
        overall_status = "Verificaciones aprobadas"
        conclusion = (
            "Todas las verificaciones incluidas en esta ejecución "
            "finalizaron correctamente."
        )

    rows = ""

    for result in results:
        status_class = {
            "Aprobada": "passed",
            "Fallida": "failed",
            "Error": "failed",
            "Omitida": "skipped",
        }.get(result["status"], "skipped")

        details = escape(result["details"].strip())
        details_html = (
            f'<details><summary>Consultar detalle</summary>'
            f'<pre>{details}</pre></details>'
            if details else "—"
        )

        rows += f"""
        <tr>
            <td>{escape(result["title"])}</td>
            <td>{escape(result["description"])}</td>
            <td><span class="status {status_class}">
                {escape(result["status"])}
            </span></td>
            <td>{result["duration"]:.2f} s</td>
            <td>{details_html}</td>
        </tr>
        """

    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte ejecutivo - OpenBridge</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        background: #f4f6f9;
        color: #243247;
        margin: 0;
        padding: 30px;
    }}
    main {{
        max-width: 1150px;
        margin: auto;
    }}
    header, section {{
        background: white;
        padding: 24px;
        margin-bottom: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px #0000000d;
    }}
    h1 {{ margin-bottom: 8px; }}
    .muted {{ color: #68778a; }}
    .summary {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
    }}
    .metric {{
        background: #f4f6f9;
        padding: 18px;
        border-radius: 9px;
    }}
    .metric strong {{
        display: block;
        font-size: 28px;
        margin-top: 8px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
    }}
    th, td {{
        text-align: left;
        padding: 13px;
        border-bottom: 1px solid #e5e9ef;
        vertical-align: top;
    }}
    th {{ background: #f4f6f9; }}
    .status {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
    }}
    .passed {{ background: #dcfce7; color: #166534; }}
    .failed {{ background: #fee2e2; color: #991b1b; }}
    .skipped {{ background: #fef3c7; color: #92400e; }}
    pre {{
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        max-width: 450px;
    }}
    @media (max-width: 750px) {{
        body {{ padding: 12px; }}
        table {{ font-size: 13px; }}
        th, td {{ padding: 8px; }}
    }}
</style>
</head>
<body>
<main>
<header>
    <h1>Reporte ejecutivo de calidad</h1>
    <p class="muted">OpenBridge · Automatización QA</p>
    <p><strong>Entorno evaluado:</strong> DEV</p>
    <p><strong>Fecha de generación:</strong> {generated_at}</p>
    <h2>{overall_status}</h2>
    <p>{escape(conclusion)}</p>
</header>

<section>
    <h2>Resumen de resultados</h2>
    <div class="summary">
        <div class="metric">Pruebas evaluadas
            <strong>{total}</strong>
        </div>
        <div class="metric">Aprobadas
            <strong>{passed}</strong>
        </div>
        <div class="metric">Fallidas
            <strong>{failed}</strong>
        </div>
        <div class="metric">Omitidas
            <strong>{skipped}</strong>
        </div>
        <div class="metric">Duración total
            <strong>{duration:.2f} s</strong>
        </div>
    </div>
</section>

<section>
    <h2>Resultados por funcionalidad</h2>
    <table>
        <thead>
            <tr>
                <th>Verificación</th>
                <th>¿Qué se comprobó?</th>
                <th>Resultado</th>
                <th>Duración</th>
                <th>Observaciones</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</section>

<section>
    <h2>Alcance de esta evaluación</h2>
    <p>
        Este reporte presenta los resultados de las pruebas automatizadas
        incluidas en esta ejecución. Un resultado aprobado confirma
        únicamente las verificaciones descritas; no representa una
        certificación integral de toda la plataforma.
    </p>
</section>
</main>
</body>
</html>"""


def main():
    results = read_junit_report()
    html_content = generate_html(results)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html_content, encoding="utf-8")

    print(f"Reporte ejecutivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
