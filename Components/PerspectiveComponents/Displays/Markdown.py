from typing import Optional, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Markdown(BasicPerspectiveComponent):
    _TEXT_CONTAINER_LOCATOR = (By.TAG_NAME, "p")

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
        self._text_container = ComponentPiece(
            locator=self._TEXT_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def get_text(self) -> str:
        """
        Obtain the text of the Markdown Component.

        :returns: The text of the Markdown Component.
        """
        return self._text_container.get_text()
