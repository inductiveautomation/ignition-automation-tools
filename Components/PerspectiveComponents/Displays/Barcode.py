from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Barcode(BasicPerspectiveComponent):
    """A Perspective Barcode Component."""
    _INNER_WRAPPER_LOCATOR = (By.CSS_SELECTOR, 'div.barcode')
    _VALUE_LOCATOR = (By.CSS_SELECTOR, 'div.barcode-value')
    _CANVAS_LOCATOR = (By.CSS_SELECTOR, 'canvas')
    _ERROR_STATE_LOCATOR = (By.CSS_SELECTOR, 'div.barcode-error')

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
        self._barcode_value = ComponentPiece(
            locator=self._VALUE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._barcode_wrapper = ComponentPiece(
            locator=self._INNER_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._barcode_canvas = ComponentPiece(
            locator=self._CANVAS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._barcode_error_state = ComponentPiece(
            locator=self._ERROR_STATE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def barcode_is_displaying_value(self) -> bool:
        """
        Determine if the Barcode Component is currently displaying a value.

        :returns: True, if the Barcode Component is currently displaying any value - False otherwise.
        """
        try:
            return self._barcode_value.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def get_barcode_value(self) -> str:
        """
        Obtain the displayed text of the Barcode Component.

        :returns: The text currently displayed by the Barcode component.

        :raises TimeoutException: If no value is displayed.
        """
        try:
            return self._barcode_value.get_text()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the value container of the Barcode Component.") from toe

    def is_in_error_state(self) -> bool:
        """
        Determine if the Barcode Component is currently in an error state.

        :returns: True, if the Barcode Component is currently in an error state - False otherwise.
        """
        try:
            return self._barcode_error_state.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def get_error_message(self) -> str:
        """
        Obtain the error message displayed in the Barcode Component.

        :returns: The displayed text of the error message currently displayed in the Barcode Component.
        """
        try:
            return self._barcode_error_state.get_text()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the error state of the Barcode Component.") from toe

    def value_displayed_below(self) -> bool:
        """
        Determine if the value of the Barcode Component is currently displayed below the canvas (visual barcode).

        :returns: True, if the text is below the barcode.

        :raises TimeoutException: If unable to locate the value or canvas.
        """
        try:
            return self._barcode_value.get_origin().Y > self._barcode_canvas.get_origin().Y
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate either the value container or the barcode canvas.") from toe

    def get_barcode_as_data_url(self) -> str:
        """
        Obtain the shape of the Barcode as a string. Useful only for validating differences in values.

        :returns: A gibberish string which represents the shape of the displayed barcode as a string.
        """
        try:
            return self.driver.execute_script('return arguments[0].toDataURL()', self._barcode_canvas.find())
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the canvas of the barcode Component.") from toe
