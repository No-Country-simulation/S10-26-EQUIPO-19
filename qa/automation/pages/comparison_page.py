from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ComparisonPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = page.get_by_role(
            "heading",
            name="Comparar herramientas",
            exact=True
        )

        self.back_to_catalog_button = page.get_by_role(
            "link",
            name="Volver al catálogo"
        )

        self.comparison_table = page.get_by_role("table")

        self.comparison_caption = page.locator(
            "table caption"
        )

    def get_repository_in_comparison(
        self,
        repository_name: str
    ) -> Locator:

        return self.comparison_table.get_by_text(
            repository_name,
            exact=True
        )

    def get_comparison_rows(self):
        return self.comparison_table.locator("tbody tr")

    def return_to_catalog(self):
        self.back_to_catalog_button.click()
