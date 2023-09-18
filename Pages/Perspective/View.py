from typing import Tuple, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Pages.PagePiece import PagePiece


class View(PagePiece):
    """
    "View" is a Perspective concept of a displayed container which does NOT have to be a page.
    Views can have components and properties, but they MUST NEVER have a URL path. Headers and Footers are examples
    of "Docked" Views, as they are anchored to a location and are visible (potentially across many pages),
    yet you can never visit a header/footer by navigating to it via URL. Views are essentially identical to
    PageComponents, and are only used instead of PageComponents for clarity.
    """

    def __init__(
            self,
            driver: WebDriver,
            primary_locator: Tuple[By, str] = None,
            view_resource_path: Optional[str] = None,
            wait_timeout: float = 10):
        """
        :param driver: The WebDriver in use for the browser window.
        :param primary_locator: The primary locator used to identify a component of the View. This will be the same as
            the `root_id` in most cases.
        :param view_resource_path: The path to the View within the Designer, after `Perspective/Views`.
        :param wait_timeout: The amount of time this resource should implicitly wait when querying.
        """
        PagePiece.__init__(
            self,
            driver=driver,
            primary_locator=primary_locator,
            wait_timeout=wait_timeout)
        self._view_resource_path = view_resource_path

    def get_view_resource_path(self) -> Optional[str]:
        return self._view_resource_path
