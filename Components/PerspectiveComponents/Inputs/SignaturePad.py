from enum import Enum
from typing import Tuple, List, Optional

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.PerspectiveComponents.Inputs.Button import Button


class Orientation(Enum):
    """
    Orientation describes the relative positioning of the action bar of the Signature Pad in relation to the canvas
    of the Component, where the action bar contains the Clear and Submit buttons.
    """
    TOP = "column-reverse"
    BOTTOM = "column"
    RIGHT = "row"
    LEFT = "row-reverse"


class SignaturePad(BasicPerspectiveComponent):
    """A Perspective Signature Pad Component."""
    _SIG_PAD_LOCATOR = (By.CSS_SELECTOR, 'div.ia-signature-pad-canvas-wrapper')
    _SIG_PAD_BAR_LOCATOR = (By.CSS_SELECTOR, 'div.ia-signature-pad-action-bar')
    _CLEAR_BUTTON_LOCATOR = (By.CSS_SELECTOR, f'button[data-button-type="clear"]')
    _SUBMIT_BUTTON_LOCATOR = (By.CSS_SELECTOR, f'button[data-button-type="submit"]')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._action_bar = ComponentPiece(
            locator=self._SIG_PAD_BAR_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._clear_button = Button(
            locator=self._CLEAR_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._action_bar.locator_list,
            poll_freq=poll_freq)
        self._submit_button = Button(
            locator=self._SUBMIT_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._action_bar.locator_list,
            poll_freq=poll_freq)
        self._signature_pad = ComponentPiece(
            locator=self._SIG_PAD_LOCATOR, driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)

    def action_bar_has_orientation(self, expected_orientation: Orientation) -> bool:
        """
        Determine the orientation of the action bar of the Signature Pad.

        :returns: True, if the action bar has the supplied Orientation - False otherwise.
        """
        return expected_orientation.value.lower() == self.find().value_of_css_property("flex-direction").lower()

    def clear_button_is_enabled(self) -> bool:
        """
        Determine if the Clear button is currently enabled for the Signature Pad.

        :returns: True, if the Clear button is enabled - False otherwise.
        """
        return self._clear_button.is_enabled()

    def clear_button_is_primary(self) -> bool:
        """
        Determine if the Clear button is currently declaring as a Primary button type.

        :returns: True, if the Clear button is a Primary button - False otherwise.

        :raises TimeoutException: If the Clear button is not currently displayed.
        """
        return self._clear_button.is_primary()

    def clear_button_is_secondary(self) -> bool:
        """
        Determine if the Clear button is currently declaring as a Secondary button type.

        :returns: True, if the Clear button is a Secondary button - False otherwise.

        :raises TimeoutException: If the Clear button is not currently displayed.
        """
        return self._clear_button.is_secondary()

    def click_clear_button(self) -> None:
        """
        Click the Clear button.

        :raises TimeoutException: If the Clear button is not currently displayed.
        """
        self._clear_button.click()

    def click_submit_button(self) -> None:
        """
        Click the Submit button.

        :raises TimeoutException: If the Clear button is not currently displayed.
        """
        self._submit_button.click()

    def draw_on_canvas(self) -> None:
        """
        Make a small mark on the canvas of the Signature Pad. Useful for mocking a signature.
        """
        ActionChains(driver=self.driver)\
            .click_and_hold(on_element=self._signature_pad.find())\
            .move_by_offset(xoffset=10, yoffset=10)\
            .release()\
            .perform()

    def get_text_of_clear_button(self) -> str:
        """
        Obtain the text currently displayed for the Clear button.

        :raises TimeoutException: If the Clear button is not currently displayed.
        """
        return self._clear_button.get_text()

    def get_text_of_submit_button(self) -> str:
        """
        Obtain the text currently displayed for the Submit button.

        :raises TimeoutException: If the Submit button is not currently displayed.
        """
        return self._submit_button.get_text()

    def submit_button_is_enabled(self) -> bool:
        """
        Determine if the Submit button is currently enabled.
        """
        return self._submit_button.is_enabled()

    def submit_button_is_primary(self) -> bool:
        """
        Determine if the Submit button is currently declaring as a Primary button type.

        :raises TimeoutException: If the Submit button is not currently displayed.
        """
        return self._submit_button.is_primary()

    def submit_button_is_secondary(self) -> bool:
        """
        Determine if the Submit button is currently declaring as a Secondary button type.

        :raises TimeoutException: If the Submit button is not currently displayed.
        """
        return self._submit_button.is_secondary()
