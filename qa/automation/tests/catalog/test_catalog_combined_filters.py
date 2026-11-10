from playwright.sync_api import expect
from pages.catalog_page import CatalogPage
import pytest

pytestmark = pytest.mark.e2e
def test_combined_catalog_filters(page):
    catalog = CatalogPage(page)
    catalog.open()

    # STEP 1: Apply language filter
    catalog.select_language("Java")

    # STEP 2: Apply license filter
    catalog.select_license("Apache-2.0")

    # STEP 3: Apply maintenance filter
    catalog.select_maintenance("Activo")

    # STEP 4: Validate Keycloak is present
    keycloak = catalog.get_repository_card("Keycloak")
    expect(keycloak).to_be_visible()

    # STEP 5: Validate all visible repositories
    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()

    for index in range(repositories.count()):
        repository = repositories.nth(index)

        expect(repository).to_contain_text("Java")
        expect(repository).to_contain_text("Apache-2.0")
        expect(repository).to_contain_text("Activo")

    # STEP 6: Validate selected filter values
    expect(catalog.language_filter).to_have_value("Java")
    expect(catalog.license_filter).to_have_value("Apache-2.0")
    expect(catalog.maintenance_filter).to_have_value("Activo")


def test_clear_combined_catalog_filters(page):
    catalog = CatalogPage(page)
    catalog.open()

    # Apply combined filters
    catalog.select_language("Java")
    catalog.select_license("Apache-2.0")
    catalog.select_maintenance("Activo")

    # Clear all filters
    catalog.clear_filters()

    # Validate filters return to default values
    expect(catalog.language_filter).to_have_value("")
    expect(catalog.license_filter).to_have_value("")
    expect(catalog.maintenance_filter).to_have_value("")

    # Validate catalog results are available again
    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()
