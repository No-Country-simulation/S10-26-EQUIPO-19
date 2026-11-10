import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage
from pages.assistant_page import AssistantPage


@pytest.mark.smoke
def test_smk_001_catalog_loads(page):
    """Verifica la disponibilidad del catálogo."""

    response = page.goto("/")

    assert response is not None
    assert response.status == 200

    catalog = CatalogPage(page)

    expect(catalog.search_input).to_be_visible()
    expect(catalog.get_visible_repository_cards().first).to_be_visible()


@pytest.mark.smoke
def test_smk_002_catalog_search(page):
    """Verifica que la búsqueda encuentre un repositorio."""

    catalog = CatalogPage(page)
    catalog.open("/")

    catalog.search_repository("Ollama")

    expect(catalog.get_repository_card("Ollama")).to_be_visible()


@pytest.mark.smoke
def test_smk_003_category_filter(page):
    """Verifica que se pueda seleccionar una categoría."""

    catalog = CatalogPage(page)
    catalog.open("/")

    category_button = catalog.is_category_selected("Autenticación")

    expect(category_button).to_be_visible()
    expect(category_button).to_have_attribute(
        "aria-pressed", "false"
    )

    catalog.select_category("Autenticación")

    expect(category_button).to_have_attribute(
        "aria-pressed", "true"
    )

    expect(
        catalog.get_visible_repository_cards().first
    ).to_be_visible()


@pytest.mark.smoke
def test_smk_004_repository_detail(page):
    """Verifica que se pueda abrir una ficha técnica."""

    catalog = CatalogPage(page)
    catalog.open("/")

    catalog.open_repository("Ollama")

    expect(catalog.get_repository_dialog()).to_be_visible()
    expect(catalog.get_repository_title()).to_be_visible()


@pytest.mark.smoke
def test_smk_005_assistant_loads(page):
    """Verifica que la interfaz del asistente esté disponible."""

    assistant = AssistantPage(page)
    assistant.open_assistant()

    expect(assistant.query_input).to_be_visible()
    expect(assistant.send_button).to_be_visible()
