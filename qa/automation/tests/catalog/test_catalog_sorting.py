from playwright.sync_api import expect
from pages.catalog_page import CatalogPage
import pytest

pytestmark = pytest.mark.e2e
def test_sort_by_stars(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("stars")

    expect(catalog.sort_filter).to_have_value("stars")


def test_sort_by_forks(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("forks")

    expect(catalog.sort_filter).to_have_value("forks")


def test_sort_by_last_update(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("last_commit_at")

    expect(catalog.sort_filter).to_have_value("last_commit_at")


def test_sort_by_health_score(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("health_score")

    expect(catalog.sort_filter).to_have_value("health_score")


def test_change_sort_direction(page):
    catalog = CatalogPage(page)
    catalog.open()

    # Initial direction
    expect(catalog.sort_direction_button).to_have_attribute(
        "aria-label",
        "Orden: Mayor a menor. Cambiar orden"
    )

    # Change direction
    catalog.change_sort_direction()

    expect(catalog.sort_direction_button).to_have_attribute(
        "aria-label",
        "Orden: Menor a mayor. Cambiar orden"
    )

    # Change direction again
    catalog.change_sort_direction()

    expect(catalog.sort_direction_button).to_have_attribute(
        "aria-label",
        "Orden: Mayor a menor. Cambiar orden"
    )

def get_numeric_values(catalog, repositories, extractor):
    return [
        extractor(repositories.nth(index))
        for index in range(repositories.count())
    ]


def test_stars_are_sorted_descending(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("stars")

    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()

    values = get_numeric_values(
        catalog,
        repositories,
        catalog.get_repository_stars
    )

    assert values == sorted(values, reverse=True)


def test_forks_are_sorted_descending(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("forks")

    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()

    values = get_numeric_values(
        catalog,
        repositories,
        catalog.get_repository_forks
    )

    assert values == sorted(values, reverse=True)


def test_health_score_is_sorted_descending(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("health_score")

    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()

    values = get_numeric_values(
        catalog,
        repositories,
        catalog.get_repository_health_score
    )

    assert values == sorted(values, reverse=True)


def test_stars_sort_direction_changes_order(page):
    catalog = CatalogPage(page)
    catalog.open()

    catalog.select_sort_order("stars")

    repositories = catalog.get_visible_repository_cards()
    expect(repositories.first).to_be_visible()

    descending_values = get_numeric_values(
        catalog,
        repositories,
        catalog.get_repository_stars
    )

    assert descending_values == sorted(
        descending_values,
        reverse=True
    )

    catalog.change_sort_direction()

    ascending_values = get_numeric_values(
        catalog,
        repositories,
        catalog.get_repository_stars
    )

    assert ascending_values == sorted(ascending_values)
