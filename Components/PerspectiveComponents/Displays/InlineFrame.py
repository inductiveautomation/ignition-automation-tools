from typing import Tuple, Optional, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class InlineFrame(BasicPerspectiveComponent):
    """A Perspective Inline Frame (iframe) Component"""
    _IFRAME_LOCATOR = (By.TAG_NAME, "iframe")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._iframe = ComponentPiece(locator=self._IFRAME_LOCATOR, driver=driver, poll_freq=poll_freq)

    def get_source(self) -> str:
        """
        Obtain the source in use by the Inline Frame component. The source is essentially the URl of the website
        embedded into the iframe.

        :returns: The URl of the website embedded into the Inline Frame Component.
        """
        return self._iframe.find().get_attribute('src')
