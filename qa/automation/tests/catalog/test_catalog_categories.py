
from playwright.sync_api import expect
import pytest
from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.e2e
def test_filter_repositories_by_category(page):
    """
    E2E-CAT-002:
    Filter repositories by category.
    """

    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_category("Autenticación")

    selected_category = catalog.is_category_selected(
        "Autenticación"
    )

    expect(selected_category).to_have_attribute(
        "aria-pressed",
        "true"
    )

    repositories = catalog.get_visible_repository_cards()

    expect(repositories.first).to_be_visible()

    for index in range(repositories.count()):

        repository = repositories.nth(index)

        category = catalog.get_repository_category(repository)

        expect(category).to_have_attribute(
            "title",
            "Autenticación"
        )
