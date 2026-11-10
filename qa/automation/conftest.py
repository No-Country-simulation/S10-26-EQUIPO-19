
import os
import pytest


# --------------------------------------------------
# BROWSER CONFIGURATION
# --------------------------------------------------

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Local: Headed mode.
    CI/CD: Headless mode.
    """

    is_ci = os.getenv("CI", "").lower() == "true"

    return {
        **browser_type_launch_args,
        "headless": is_ci
    }


# --------------------------------------------------
# BROWSER CONTEXT CONFIGURATION
# --------------------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Shared browser context configuration.
    """

    return {
        **browser_context_args,
        "viewport": {
            "width": 1440,
            "height": 900
        }
    }


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

@pytest.fixture
def page(page):
    """
    Configure default timeouts for each test.
    """

    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(15_000)

    return page
