from typing import Tuple, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS


class EmbeddedView(BasicPerspectiveComponent):
    """A Perspective Embedded View Component."""
    _PRIMARY_MESSAGE_LOCATOR = (By.CSS_SELECTOR, 'div.message-primary')
    _SECONDARY_MESSAGE_LOCATOR = (By.CSS_SELECTOR, 'div.message-secondary')
    _STATE_DISPLAY_LOCATOR = (By.CSS_SELECTOR, "div.view-state-display")

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
        self._primary_message = ComponentPiece(
            locator=self._PRIMARY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._secondary_message = ComponentPiece(
            locator=self._SECONDARY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._state_display = ComponentPiece(
            locator=self._STATE_DISPLAY_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def get_primary_message(self) -> str:
        """
        Obtain the primary message of the Embedded View. This is the message seen when a View is not properly
        configured.

        :raises TimeoutException: If a View is properly configured - and therefore not displaying a config error message
            - or the Embedded View is not found.
        """
        return self._primary_message.get_text()

    def get_secondary_message(self) -> str:
        """
        Obtain the secondary message of the Embedded View. This is the message seen when a View is not properly
        configured.

        :raises TimeoutException: If a View is properly configured - and therefore not displaying a config error message
            - or the Embedded View is not found.
        """
        return self._secondary_message.get_text()

    def get_state_display_background(self) -> str:
        """
        Obtain the background color of the Embedded View. Usually only useful when a View is not properly configured.
        """
        return self._state_display.get_css_property(property_name=CSS.BACKGROUND_COLOR)

    def view_path_is_invalid(self) -> bool:
        """
        Determine if the currently applied View path is INVALID.

        :returns: True, if the currently applied View path is invalid - False if the currently applied View path is
            valid.
        """
        try:
            self._primary_message.find()
            self._secondary_message.find()
            return True
        except TimeoutException:
            return False

    def view_path_is_blank(self) -> bool:
        """
        Determine if the currently applied View path is an empty string. This function is non-conclusive, as it only
        verifies the Embedded View contains no text. There is still a possibility that the embedded View could be valid
        and rendered, but contain no text.

        :returns: True, if the Embedded View contains no text content - False otherwise.
        """
        return self.get_text() == ''
