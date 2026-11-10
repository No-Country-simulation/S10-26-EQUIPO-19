from playwright.sync_api import expect
import pytest
from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.e2e
def test_search_repository_by_name(page):
    """
    E2E-CAT-001:
    Search repository by name.
    """

    catalog = CatalogPage(page)
    catalog.open()

    catalog.search_repository("LocalAI")

    repository = catalog.get_repository_card("LocalAI")

    expect(repository).to_be_visible()
