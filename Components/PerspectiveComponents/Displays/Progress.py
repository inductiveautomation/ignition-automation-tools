from enum import Enum
from typing import Optional, List, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS


class Mode(Enum):
    """The modes available to the Progress Component."""
    DETERMINATE = "determinate"
    INDETERMINATE = "indeterminate"


class Progress(BasicPerspectiveComponent):
    """A Perspective Progress Component."""
    _TRACK_CLASS = 'ia_progressBar__track'
    _DETERMINATE_CLASS = f'{_TRACK_CLASS}--determinate'
    _INDETERMINATE_CLASS = f'{_TRACK_CLASS}--indeterminate'
    _VALUE_DISPLAY_LOCATOR = (By.CSS_SELECTOR, "span.ia_progressBar__displayValue")
    _BAR_LOCATOR = (By.CSS_SELECTOR, "div.ia_progressBar__bar")

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
        self._track = ComponentPiece(
            locator=(By.CSS_SELECTOR, "div"), driver=driver, parent_locator_list=self.locator_list)
        self._bar = ComponentPiece(
            locator=self._BAR_LOCATOR, driver=driver, parent_locator_list=self._track.locator_list)
        self._value_display = ComponentPiece(
            locator=self._VALUE_DISPLAY_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def get_bar_color(self) -> str:
        """
        Obtain the color of the bar piece of the Progress Component.

        :returns: The color of the bar of the Progress Component, as a string. Note that different browsers may return
            this color in different formats (RGB vs hex).
        """
        return self._bar.get_css_property(property_name=CSS.BACKGROUND_COLOR)

    def get_displayed_percentage(self) -> float:
        """
        Obtain the current visual percentage of the Progress Component. This is not a check against the Label, but is an
        actual calculation of the volume of the bar of the Progress Component.

        :returns: The visual percentage of the Progress Component, as a user would see it.
        """
        progress_origin_x = float(self.get_origin().X)
        progress_width = float(self.get_computed_width())
        return ((float(self._bar.get_termination().X) - progress_origin_x) * 100) / progress_width

    def get_max(self) -> float:
        """
        Obtain the current maximum value the Progress Component may display.

        :returns: The 'max' attribute of the Progress Bar.
        """
        return float(self._track.find().get_attribute('data-max'))

    def get_min(self):
        """
        Obtain the current minimum value the Progress Component may display.

        :returns: The 'min' attribute of the Progress Bar.
        """
        return float(self._track.find().get_attribute('data-min'))

    def get_text(self) -> Optional[str]:
        """
        Obtain the displayed label text of the Progress Component.

        :returns: The text of the label for the Progress Component, or None if the component is not configured to
            display a value.
        """
        try:
            return self._value_display.get_text()
        except TimeoutException:
            return None

    def get_track_color(self) -> str:
        """
        Obtain the color of the track piece of the Progress Component.

        :returns: The color of the track of the Progress Component, as a string. Note that different browsers may return
            this color in different formats (RGB vs hex).
        """
        return self._track.get_css_property(property_name=CSS.BACKGROUND_COLOR)

    def get_value(self) -> float:
        """
        Obtain the value of the Progress Component.

        :returns: The 'value' attribute of the Progress Bar.
        """
        return float(self._track.find().get_attribute('data-value'))

    def is_indeterminate_progress_bar(self) -> bool:
        """
        Determine if the Progress Component is currently displaying as indeterminate.

        :returns: True if the Progress Bar is in "indeterminate" mode, False otherwise.
        """
        variant = self._track.find().get_attribute('data-variant')
        return variant is not None and variant == Mode.INDETERMINATE.value
