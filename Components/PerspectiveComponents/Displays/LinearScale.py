from typing import Tuple, Optional, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class LinearScale(BasicPerspectiveComponent):
    """A Perspective Linear Scale Component."""
    _TRANSFORM_ELEMENT_LOCATOR = (By.CSS_SELECTOR, 'svg > g')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq
        )
        self._transform_element = ComponentPiece(
            locator=self._TRANSFORM_ELEMENT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def is_horizontal(self) -> bool:
        """
        Determine if the Linear Scale is currently in a horizontal layout.

        :returns: True, if the Linear Scale is currently rendering in a horizontal manner - False otherwise.
        """
        return 'rotate(90)' in self._transform_element.find().get_attribute('transform')
