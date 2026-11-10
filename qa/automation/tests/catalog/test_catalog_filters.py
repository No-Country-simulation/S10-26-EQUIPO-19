
from playwright.sync_api import expect
from pages.catalog_page import CatalogPage
import pytest

pytestmark = pytest.mark.e2e


def test_filter_by_language(page):
    catalog = CatalogPage(page)
    catalog.open()
    catalog.select_language("Java")

    repositories = catalog.get_visible_repository_cards()

    # Esperar a que el contador coincida con las tarjetas visibles.
    page.wait_for_function("""
        () => {
            const cards = [
                ...document.querySelectorAll(
                    'button[aria-label^="Ver la ficha de "]'
                )
            ].filter(card => card.getClientRects().length > 0);

            const heading = [...document.querySelectorAll("h2")]
                .find(element =>
                    /^\\d+ herramientas$/.test(
                        element.textContent.trim()
                    )
                );

            if (!heading) return false;

            const match = heading.textContent.match(/^\\d+/);

            return match && Number(match[0]) === cards.length;
        }
    """)

    count = repositories.count()

    assert count > 0, "El filtro Java no devolvió repositorios"

    for index in range(count):
        expect(repositories.nth(index)).to_contain_text("Java")


def test_filter_by_license(page):
    catalog = CatalogPage(page)
    catalog.open()
    catalog.select_license("Apache-2.0")

    repositories = catalog.get_visible_repository_cards()

    expect(repositories.first).to_be_visible()

    for index in range(repositories.count()):
        expect(repositories.nth(index)).to_contain_text("Apache-2.0")


def test_filter_by_maintenance(page):
    catalog = CatalogPage(page)
    catalog.open()
    catalog.select_maintenance("Activo")

    repositories = catalog.get_visible_repository_cards()

    expect(repositories.first).to_be_visible()

    for index in range(repositories.count()):
        expect(repositories.nth(index)).to_contain_text("Activo")


def test_clear_catalog_filters(page):
    catalog = CatalogPage(page)
    catalog.open()

    # Aplicar los tres filtros originales.
    catalog.select_language("Java")
    catalog.select_license("Apache-2.0")
    catalog.select_maintenance("Activo")

    # Limpiar los filtros.
    catalog.clear_filters()

    # Validar que los tres controles recuperen sus valores por defecto.
    expect(catalog.language_filter).to_have_value("")
    expect(catalog.license_filter).to_have_value("")
    expect(catalog.maintenance_filter).to_have_value("")
