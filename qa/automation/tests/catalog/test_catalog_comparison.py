import pytest
import re
from playwright.sync_api import expect
from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.e2e
def test_compare_two_repositories(page):

    catalog = CatalogPage(page)

    # 1. Abrir catálogo
    catalog.open()

    # 2. Seleccionar los dos repositorios
    catalog.add_repository_to_comparison("ollama")
    catalog.add_repository_to_comparison("langchain")

    # 3. Validar que ambos estén seleccionados
    comparison_link = catalog.get_comparison_link()
    expect(comparison_link).to_be_visible()

    expected_url = comparison_link.get_attribute("href")
    expect(comparison_link).to_have_attribute(
        "href",
        re.compile(r"^/comparar\?ids=")
    )

    # 4. Navegar al comparador
    comparison_link.click()
    page.wait_for_url(f"**{expected_url}")

    # 5. Validar encabezado
    expect(
        page.get_by_role(
            "heading",
            name="Comparar herramientas",
            exact=True
        )
    ).to_be_visible()

    # 6. Esperar a que termine la carga real
    expect(
        page.locator('[aria-label="Cargando la comparación"]')
    ).to_have_count(0, timeout=20000)

    # 7. Validar tabla comparativa
    comparison_table = page.get_by_role(
        "table",
        name="Comparación lado a lado de 2 herramientas"
    )

    expect(comparison_table).to_be_visible()

    # Validar encabezado de Ollama
    expect(
        comparison_table.get_by_role(
            "columnheader",
            name=re.compile("ollama", re.IGNORECASE)
        )
    ).to_be_visible()

    # Validar encabezado de Langchain
    expect(
        comparison_table.get_by_role(
            "columnheader",
            name=re.compile("langchain", re.IGNORECASE)
        )
    ).to_be_visible()


    # 8. Validar métricas de comparación
    metrics = [
        "Health score",
        "Estrellas",
        "Forks",
        "Licencia",
        "Lenguaje",
        "Issues abiertos"
    ]

    for metric in metrics:
        expect(
            comparison_table.get_by_role(
                "rowheader",
                name=re.compile(re.escape(metric), re.IGNORECASE)
            )
        ).to_be_visible()

    # 9. Validar información específica

    # Health Score
    expect(comparison_table).to_contain_text("95/100")
    expect(comparison_table).to_contain_text("99/100")

    # Validar que ambos repositorios muestran sus estrellas
    stars_row = comparison_table.get_by_role(
        "row"
    ).filter(has=page.get_by_role("rowheader", name=re.compile("Estrellas", re.IGNORECASE)))

    expect(stars_row).to_be_visible()

    stars_cells = stars_row.get_by_role("cell")

    expect(stars_cells).to_have_count(2)

    for cell in stars_cells.all():
        expect(cell).to_contain_text(re.compile(r"\d"))



    # 10. Regresar al catálogo
    back_link = page.get_by_role(
        "link",
        name=re.compile("Volver al catálogo")
    )

    expect(back_link).to_be_visible()
    back_link.click()

    expect(page).to_have_url(re.compile(r"/$"))
