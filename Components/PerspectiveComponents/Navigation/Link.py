from typing import Optional, Tuple, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Link(BasicPerspectiveComponent):
    """A Perspective Link Component."""

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: int = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._anchor = ComponentPiece(
            locator=(By.TAG_NAME, "a"),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def get_link_href(self) -> str:
        """
        Obtain the destination URL of the Link component. Returned values which begin with a slash are Perspective
        page URLs which would be appended to the Gateway address (including port) to fashion a full URL, though
        the actual navigation is done internally instead of through an HTTP GET request.
        """
        return self._anchor.find().get_attribute('href')

    def get_target(self) -> str:
        """
        Obtain the browser target of the link.

        _blank - The destination specified within the href attribute will be opened in a new browser tab.
        All other values would open in the same browser tab.
        """
        return self._anchor.find().get_attribute('target')
