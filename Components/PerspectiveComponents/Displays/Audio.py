from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Audio(BasicPerspectiveComponent):
    """A Perspective Audio Component."""
    _AUDIO_LOCATOR = (By.TAG_NAME, "audio")

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
        self._audio = ComponentPiece(
            locator=self._AUDIO_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def get_source(self) -> str:
        """
        Obtain the path of the file currently in use by the Audio Component.

        :returns: The path of the file currently in use by the component, as a slash-delimited string.

        :raises TimeoutException: If unable to locate the internal <audio> element.
        """
        try:
            return self._audio.find().get_attribute("src")
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the inner <audio> piece of the Audio Component.") from toe

    def is_displayed(self) -> bool:
        """
        Determine if the Audio Component is currently displayed. The Audio Component has a complicated set of display
        logic, and so even if the Audio Component is displayed, it may not be visible. Double-check expected states
        by using the :func:`is_visible` function.

        :returns: True, if the component is currently displayed - False otherwise.

        :raises TimeoutException: If unable to locate the internal <audio> element.
        """
        try:
            return self._audio.find().is_displayed()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the inner <audio> piece of the Audio Component.") from toe

    def is_visible(self) -> bool:
        """
        Determine if the Audio Component is currently visible. The Audio Component has a complicated set of display
        logic, and so even if the Audio Component is visible, it may not be displayed. Double-check expected states
        by using the :func:`is_displayed` function.

        :returns: True, if the component is currently visible - False otherwise.

        :raises TimeoutException: If unable to locate the Audio Component.
        """
        try:
            return self.get_css_property(property_name="visibility") != "hidden"
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the Audio Component as defined by its locator.") from toe
