from enum import Enum
from typing import Optional, List, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS


class LEDDisplay(BasicPerspectiveComponent):
    """A Perspective LED Display Component."""
    _DIGIT_LOCATOR = (By.TAG_NAME, "g")
    _BACKGROUND_RECT_LOCATOR = (By.TAG_NAME, "rect.ia_ledComponent__background")

    class Segments(Enum):
        """Available segment count configurations."""
        SEGMENTS_14 = "14 segment"
        SEGMENTS_7 = "7 segment"

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
        self._digit = ComponentPiece(
            locator=self._DIGIT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._background_rect = ComponentPiece(
            locator=self._BACKGROUND_RECT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._digit_coll = {}

    def get_active_diode_color(self) -> str:
        """
        Obtain the color in use by active segments/diodes. This function works as long as the 0th index (from the right)
        is not a '.'.

        :returns: The active diode color as a string. Note that different browsers may return this value in different
            formats (RGB vs hex).

        :raises TimeoutException: If the LED Display is not currently displaying any value.
        """
        return ComponentPiece(
            locator=(By.TAG_NAME, "use.ia_ledComponent__diode--on"),
            driver=self.driver,
            parent_locator_list=self._get_digit_by_index(zero_based_index_from_right=0).locator_list,
            wait_timeout=1,
            poll_freq=self.poll_freq).get_css_property(property_name=CSS.FILL)

    def get_background_color(self) -> str:
        """
        Obtain the color in use by the background.

        :returns: The background color as a string. Note that different browsers may return this value in different
            formats (RGB vs hex).
        """
        return self._background_rect.get_css_property(property_name=CSS.FILL)

    def get_character_at_index(self, zero_based_index_from_right: int) -> str:
        """
        Obtain the character displayed at a given index.

        :param zero_based_index_from_right: The zero-based index of the value FROM THE RIGHT for which you would like
            to obtain the displayed character.

        :returns: The character at the supplied index, as a string.

        :raises TimeoutException: If the supplied index is invalid, based on the length of the displayed value.
        """
        return self._get_digit_by_index(
            zero_based_index_from_right=zero_based_index_from_right).find().get_attribute(name="data-char")

    def get_inactive_diode_color(self) -> str:
        """
        Obtain the color in use by inactive segments/diodes. This function works as long as the 0th index (from the
        right) is not a '.'.

        :returns: The inactive diode color as a string. Note that different browsers may return this value in different
            formats (RGB vs hex).

        :raises TimeoutException: If the LED Display is not currently displaying any value.
        """
        return ComponentPiece(
            locator=(By.TAG_NAME, "use.ia_ledComponent__diode--off"),
            driver=self.driver,
            parent_locator_list=self._get_digit_by_index(zero_based_index_from_right=0).locator_list,
            wait_timeout=1,
            poll_freq=self.poll_freq).get_css_property(property_name=CSS.FILL)

    def get_text(self) -> str:
        """
        Obtain the text of the LED Display.

        :return: The text of the LEDDisplay.
        """
        return self._get_display_value_as_text()

    def is_fourteen_segment_display(self) -> bool:
        """
        Determine if the LED Display is currently rendering in a 14-segment layout (as opposed to 7-segment layout).

        :returns: True, if the LED Display is in 14 segment mode - False otherwise.
        """
        try:
            return len(ComponentPiece(
                locator=(By.TAG_NAME, "use"),
                driver=self.driver,
                parent_locator_list=self._get_digit_by_index(zero_based_index_from_right=0).locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq).find_all()) > 7
        except TimeoutException:
            # If we fail to find the expected fourteen-segment svgs, we should at least verify the LED exists.
            return self.find() is None

    def _display_has_text(self, expected_text: str, trim: bool = False) -> bool:
        """
        Determine if the LED Display is currently displaying the supplied expected_text.

        :param expected_text: The text you expect the LED Display to be displaying.
        :param trim: If True, we will ignore any leading whitespace.

        :returns: True, if the currently displayed value is an exact match for the expected_text - False otherwise.
        """
        return str(self._get_display_value_as_text(trim=trim)) == str(expected_text)

    def _get_display_value_as_text(self, trim: bool = False) -> str:
        """
        Obtain the displayed value of the LED Display.

        :param trim: If True, we will remove any leading spaces from the displayed value.

        :returns: The displayed value of the LED Display.

        :raises TimeoutException: If no value is currently displayed for the LED Display.
        """
        displayed_text = []
        try:
            all_digits = self._digit.find_all()
        except TimeoutException:
            all_digits = []
        for i in range(len(all_digits)):
            displayed_text.insert(
                0,
                self._get_digit_by_index(zero_based_index_from_right=i).find().get_attribute(name="data-char"))
        displayed_text = ''.join(displayed_text)
        if trim:
            displayed_text = displayed_text.lstrip(" ")
        return displayed_text

    def _get_digit_by_index(self, zero_based_index_from_right: int) -> ComponentPiece:
        """
        Obtain a specific character from the LED Display by its index.

        :param zero_based_index_from_right: The zero-based index of the desired character FROM THE RIGHT.
        """
        digit = self._digit_coll.get(zero_based_index_from_right)
        if not digit:
            digit = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'svg[data-index="{zero_based_index_from_right}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq)
            self._digit_coll[zero_based_index_from_right] = digit
        return digit
