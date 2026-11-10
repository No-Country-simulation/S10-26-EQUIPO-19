import re

from playwright.sync_api import Page, Locator, expect

from pages.base_page import BasePage


class CatalogPage(BasePage):
    """
    Page Object for the OpenBridge catalog.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Search
        self.search_input = page.get_by_placeholder(
            "Nombre o descripción",
            exact=True
        )

        # Category filters
        self.category_buttons = page.locator(
            'button[aria-pressed]'
        )

        # Repository cards
        self.repository_cards = page.locator(
            'button[aria-label^="Ver la ficha de "]'
        )

        # Technical detail dialog
        self.repository_dialog = page.get_by_role("dialog")

        # Close dialog
        self.close_dialog_button = page.get_by_role(
            "button",
            name="Cerrar la ficha",
            exact=True
        )

        # Catalog filters
        self.language_filter = page.locator(
            "label"
        ).filter(has_text="Lenguaje").locator("select")

        self.license_filter = page.locator(
            "label"
        ).filter(has_text="Licencia").locator("select")

        self.maintenance_filter = page.locator(
            "label"
        ).filter(has_text="Nivel de mantenimiento").locator("select")

        # Sorting
        self.sort_filter = page.locator(
            "label"
        ).filter(has_text="Ordenar por").locator("select")

        # Clear filters
        self.clear_filters_button = page.get_by_role(
            "button",
            name="Limpiar filtros",
            exact=True
        )

        # Sort direction
        self.sort_direction_button = page.locator(
            'button[aria-label^="Orden:"]'
        )

        # Repository comparison
        self.comparison_buttons = page.locator(
            'button[aria-pressed]'
        )

        self.comparison_link = page.get_by_role(
            "link",
            name=re.compile(r"^Comparar \(2\)$")
        )

        self.clear_comparison_button = page.get_by_role(
            "button",
            name="Limpiar",
            exact=True
        )
    # ==========================================
    # SEARCH
    # ==========================================

    def search_repository(self, repository_name: str):
        """Search repositories by name or description."""

        self.search_input.fill(repository_name)

    def clear_search(self):
        """Clear the search field."""

        self.search_input.clear()

    # ==========================================
    # CATEGORY FILTERS
    # ==========================================

    def select_category(self, category_name: str):
        """Select a category by its visible name."""

        category_button = self.page.get_by_role(
            "button",
            name=re.compile(
                rf"^{re.escape(category_name)}(?:\s*·.*)?$"
            )
        )

        category_button.click()

    def is_category_selected(
        self,
        category_name: str
    ) -> Locator:
        """Return the category button."""

        return self.page.get_by_role(
            "button",
            name=re.compile(
                rf"^{re.escape(category_name)}(?:\s*·.*)?$"
            )
        )

    # ==========================================
    # REPOSITORY CARDS
    # ==========================================

    def get_repository_card(self, repository_name: str) -> Locator:
        """
        Get a repository card by accessible name.
        Matching is case-insensitive.
        """

        return self.page.get_by_role(
            "button",
            name=re.compile(
                rf"^Ver la ficha de {re.escape(repository_name)}$",
                re.IGNORECASE
            )
        )

    def get_visible_repository_cards(self) -> Locator:
        """Return only visible repository cards."""

        return self.repository_cards.filter(
            visible=True
        )

    def open_repository(self, repository_name):
        repository_button = self.get_repository_card(repository_name)
        expect(repository_button).to_be_visible()
        repository_button.click()

    # ==========================================
    # FILTER VALIDATION
    # ==========================================

    def get_repository_category(
        self,
        repository_card: Locator
    ) -> Locator:
        """Return the category label of a repository card."""

        return repository_card.locator(
            "span[title]"
        ).first

    # ==========================================
    # TECHNICAL DETAIL
    # ==========================================

    def get_repository_dialog(self):
        return self.page.get_by_role("dialog")

    def get_repository_title(self):
        return self.get_repository_dialog().locator("#ficha-titulo")

    def close_repository_dialog(self):
        """Close the technical detail dialog."""

        self.close_dialog_button.click()

    # ==========================================
    # LANGUAGE FILTER
    # ==========================================

    def select_language(self, language: str):
        self.language_filter.select_option(label=language)


    # ==========================================
    # LICENSE FILTER
    # ==========================================

    def select_license(self, license_name: str):
        self.license_filter.select_option(label=license_name)


    # ==========================================
    # MAINTENANCE FILTER
    # ==========================================

    def select_maintenance(self, maintenance_level: str):
        self.maintenance_filter.select_option(
            label=maintenance_level
        )


    # ==========================================
    # CLEAR FILTERS
    # ==========================================

    def clear_filters(self):
        self.clear_filters_button.click()


    # ==========================================
    # SORTING
    # ==========================================

    def select_sort_order(self, sort_option: str):
        self.sort_filter.select_option(value=sort_option)


    def change_sort_direction(self):
        self.sort_direction_button.click()

    # ==========================================
    # SORTING DATA EXTRACTION
    # ==========================================

    def get_repository_stars(self, repository_card: Locator) -> int:
        value = repository_card.locator(
            '[aria-label*="estrellas"]'
        ).get_attribute("aria-label")

        return int(
            value.split()[0].replace(".", "").replace(",", "")
        )


    def get_repository_forks(self, repository_card: Locator) -> int:
        value = repository_card.locator(
            '[aria-label*="forks"]'
        ).get_attribute("aria-label")

        return int(
            value.split()[0].replace(".", "").replace(",", "")
        )


    def get_repository_health_score(self, repository_card: Locator) -> int:
        value = repository_card.locator(
            'span[class*="bg-status-active-bg"], '
            'span[class*="bg-status-warning-bg"], '
            'span[class*="bg-status-danger-bg"]'
        ).inner_text()

        return int(value.split("·")[-1].strip().split("/")[0])


    def get_repository_update_date(self, repository_card: Locator):
        return repository_card.locator(
            "span[title]"
        ).get_attribute("title")

    # ==========================================
    # REPOSITORY COMPARISON
    # ==========================================

    def add_repository_to_comparison(self, repository_name: str):
        repository_card = self.get_repository_card(repository_name)

        # El botón de comparación es hermano de la tarjeta.
        repository_container = repository_card.locator("xpath=..")

        compare_button = repository_container.locator(
            'button[aria-pressed]'
        )

        expect(compare_button).to_be_visible()
        expect(compare_button).to_have_attribute(
            "aria-pressed",
            "false"
        )

        compare_button.click()

        expect(compare_button).to_have_attribute(
            "aria-pressed",
            "true"
        )

        return compare_button


    def get_comparison_link(self):
        return self.comparison_link


    def clear_comparison(self):
        self.clear_comparison_button.click()
