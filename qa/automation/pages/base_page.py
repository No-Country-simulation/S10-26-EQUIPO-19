from playwright.sync_api import Page, Locator


class BasePage:
    """
    Base class for all OpenBridge page objects.
    Contains reusable browser interactions.
    """

    def __init__(self, page: Page):
        self.page = page

    def open(self, path: str = "/"):
        """Navigate to a page."""
        return self.page.goto(path)

    def get_locator(self, selector: str) -> Locator:
        """Locate an element using a CSS selector."""
        return self.page.locator(selector)

    def get_by_role(
        self,
        role: str,
        name: str = None,
        exact: bool = False
    ) -> Locator:
        """Locate elements using accessible roles."""
        return self.page.get_by_role(
            role,
            name=name,
            exact=exact
        )

    def get_by_text(
        self,
        text: str,
        exact: bool = False
    ) -> Locator:
        """Locate elements using visible text."""
        return self.page.get_by_text(
            text,
            exact=exact
        )

    def get_title(self) -> str:
        """Return the current page title."""
        return self.page.title()

    def get_url(self) -> str:
        """Return the current URL."""
        return self.page.url
