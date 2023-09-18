from typing import List, Optional, Union, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.color import Color

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.Common.Button import CommonButton
from Helpers.CSSEnumerations import CSSPropertyValue, CSS
from Helpers.IAAssert import IAAssert


class MultiStateButton(BasicPerspectiveComponent):
    """A Perspective Multi-State Button Component."""
    _GENERAL_BUTTON_LOCATOR = (By.TAG_NAME, "button")
    _DEFAULT_INACTIVE_BACKGROUND_COLOR = '#FAFAFA'

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 3,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._generic_button = ComponentPiece(
            locator=self._GENERAL_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._buttons = {}

    def click(self, **kwargs) -> None:
        """
        Multi-State Buttons should not be blindly clicked because the 0th button would always receive the click.

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def click_button_by_text(self, button_text: str, wait_timeout: float = 0.5, binding_wait_time: float = 0.5) -> None:
        """
        Click one of the Multi-State Buttons by text. If multiple buttons share the same text only the first match will
        be clicked.

        :param button_text: The text of the button you would like to click.
        :param wait_timeout: The amount of time to wait until a button with the specified text becomes visible.
        :param binding_wait_time: The amount of time after the click event to wait before allowing code to continue.

        :raises TimeoutException: If no button with the specified text is found.
        """
        self._get_button_by_text(button_text=button_text).click(
            wait_timeout=wait_timeout, binding_wait_time=binding_wait_time)

    def get_css_property_value_of_button_by_text(
            self,
            button_text: str,
            property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of a CSS property for a button of the Multi-State Button based on the text of the button.

        :param button_text: The text of the button from which you would like a CSS property value
        :param property_name: The CSS property value you would like to obtain.

        :raises TimeoutException: If no button with the specified text is found.
        """
        return self._get_button_by_text(button_text=button_text).get_css_property(property_name=property_name)

    def get_button_count(self, wait_timeout: float = 0.5) -> int:
        """Obtain a count of all states contained within this Multi-State Button."""
        return len(self._generic_button.find_all(wait_timeout=wait_timeout))

    def get_button_gap(self) -> float:
        """Obtain the current gap between each button."""
        return float(self._generic_button.get_css_property(
            property_name=CSS.MARGIN_BOTTOM if self.is_column_oriented() else CSS.MARGIN_RIGHT).split("px")[0])

    def get_current_indicator_button_text(self) -> Optional[str]:
        """
        Get the text of the button which is currently displaying as selected/active. This function assumes that all
        buttons in the Multi-State Button are using their default appearance. If any button is NOT using the default
        appearance, it is possible that button text would be erroneously returned.
        """
        for button in self._generic_button.find_all():
            try:
                IAAssert.is_equal_to(
                    actual_value=button.value_of_css_property(
                        CSS.BACKGROUND_COLOR.value),
                    expected_value=self._DEFAULT_INACTIVE_BACKGROUND_COLOR,
                    failure_msg="Button does not have default background color, so it must be selected.",
                    as_type=Color)
            except AssertionError:
                return button.text
        return None

    def hover_over_button_by_text(self, button_text: str) -> None:
        """
        Hover over the button of the Multi-State Button which has the supplied text.

        :raises TimeoutException: If no button matches the supplied text.
        """
        self._get_button_by_text(button_text=button_text).hover()

    def is_column_oriented(self) -> bool:
        """
        Determine if the Multi-State Button is rendered in a column layout, as opposed to a row.

        :returns: True if the Multi-State Button is rendered as a column.
        """
        return self._generic_button.find().get_attribute(name="data-button-orientation") == "column"

    def _get_button_by_text(self, button_text: str) -> CommonButton:
        """Obtain the underlying CommonButton component from the Multi-State Button based on its text."""
        button = self._buttons.get(button_text)
        if not button:
            button = CommonButton(
                locator=(By.CSS_SELECTOR, f'{self._GENERAL_BUTTON_LOCATOR[1]}[data-label="{button_text}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq)
            self._buttons[button_text] = button
        return button
