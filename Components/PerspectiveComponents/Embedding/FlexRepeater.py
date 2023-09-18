from typing import Tuple, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class FlexRepeater(BasicPerspectiveComponent):
    """
    A Perspective Flex Repeater Component.
    """
    _DIRECT_CHILD_LOCATOR = (By.CSS_SELECTOR, '>div')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            description=description,
            poll_freq=poll_freq)
        self._children = ComponentPiece(
            locator=self._DIRECT_CHILD_LOCATOR, driver=driver, parent_locator_list=self.locator_list)

    def get_count_of_instances(self) -> int:
        """Obtain a count of instances within the Flex Repeater."""
        try:
            return len(self._children.find_all())
        except TimeoutException:
            return 0
