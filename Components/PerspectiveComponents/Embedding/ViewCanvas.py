from typing import Optional, List, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS


class ViewCanvas(BasicPerspectiveComponent):
    """
    A Perspective View Canvas Component.

    Functions for this class only provide insight into the View Canvas, and not the Views instanced by the View Canvas.
    """
    _CHILD_VIEW_LOCATOR = (By.CSS_SELECTOR, "> div")

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
            poll_freq=poll_freq)
        self._children = ComponentPiece(
            locator=self._CHILD_VIEW_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def get_count_of_instanced_views(self) -> int:
        """
        Obtain a count of the Views instanced by this View Canvas.
        """
        try:
            return len(self._children.find_all())
        except TimeoutException:
            return 0

    def get_transition_duration(self) -> str:
        """
        Obtain the transition duration for the View Canvas.

        :raises TimeoutException: If no Views are currently instanced by this View Canvas.
        """
        return self._children.get_css_property(property_name=CSS.TRANSITION_DURATION)

    def get_transition_timing_function(self) -> str:
        """
        Obtain the transition timing function for the View Canvas.

        :raises TimeoutException: If no Views are currently instanced by this View Canvas.
        """
        return self._children.get_css_property(property_name=CSS.TRANSITION_TIMING_FUNCTION)
