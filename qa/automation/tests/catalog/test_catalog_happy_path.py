from playwright.sync_api import expect
from pages.catalog_page import CatalogPage
import pytest

pytestmark = pytest.mark.e2e
def test_catalog_discovery_happy_path(page):
    """
    E2E-CAT-HP-001:

    User discovers a repository,
    filters by category and evaluates
    its technical details.
    """

    catalog = CatalogPage(page)

    # STEP 1: Access catalog
    catalog.open()

    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()

    # STEP 2: Search LocalAI
    catalog.search_repository("LocalAI")

    localai = catalog.get_repository_card("LocalAI")
    expect(localai).to_be_visible()

    # STEP 3: Clear search
    catalog.clear_search()

    # STEP 4: Select Authentication category
    catalog.select_category("Autenticación")

    selected_category = catalog.is_category_selected("Autenticación")

    expect(selected_category).to_have_attribute(
        "aria-pressed",
        "true"
    )

    # STEP 5: Validate Keycloak result
    keycloak = catalog.get_repository_card("Keycloak")
    expect(keycloak).to_be_visible()

    # STEP 6: Open technical detail
    catalog.open_repository("Keycloak")

    dialog = catalog.get_repository_dialog()
    expect(dialog).to_be_visible()

    # STEP 7: Validate repository title
    title = catalog.get_repository_title()

    expect(title).to_be_visible()
    expect(title).to_have_text("keycloak", ignore_case=True)

    # STEP 8: Close technical detail
    catalog.close_repository_dialog()

    expect(dialog).not_to_be_visible()
